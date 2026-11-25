import pytest
import requests

from app.publishing import instagram
from app.publishing.base import PublishError
from app.publishing.instagram import InstagramPublisher, build_instagram_publisher

TOKEN = "SECRET-TOKEN-123"


class FakeResponse:
    def __init__(self, body, status_code=200):
        self._body = body
        self.status_code = status_code

    def json(self):
        if self._body is None:
            raise ValueError("no json")

        return self._body


class FakeSession:
    """Plays back scripted responses and records every call."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def _next(self, method, url, kwargs):
        # Read the upload stream now, while the file is still open.
        data = kwargs.get("data")
        uploaded = data.read() if hasattr(data, "read") else None

        self.calls.append({"method": method, "url": url, "uploaded": uploaded, **kwargs})

        item = self.responses.pop(0)

        if isinstance(item, Exception):
            raise item

        return item

    def post(self, url, **kwargs):
        return self._next("post", url, kwargs)

    def get(self, url, **kwargs):
        return self._next("get", url, kwargs)


class Clock:
    """A fake clock: sleeping moves time forward without waiting."""

    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture()
def video(tmp_path):
    file = tmp_path / "reel.mp4"
    file.write_bytes(b"0123456789")
    return file


def make(responses, **options):
    session = FakeSession(responses)
    clock = Clock()

    publisher = InstagramPublisher(
        access_token=TOKEN,
        account_id="17841400000000000",
        session=session,
        sleep=clock.sleep,
        clock=clock.time,
        **options,
    )

    return publisher, session, clock


def ok(body):
    return FakeResponse(body)


def test_resumable_upload_happy_path(video):
    publisher, session, clock = make(
        [
            ok({"id": "container-1"}),
            ok({"success": True, "message": "Upload successful."}),
            ok({"status_code": "IN_PROGRESS"}),
            ok({"status_code": "FINISHED"}),
            ok({"id": "media-9"}),
            ok({"permalink": "https://www.instagram.com/reel/abc/"}),
        ]
    )

    result = publisher.publish(video, "LED Desk Lamp", "Upgrade your desk. #Lighting")

    assert result.external_id == "media-9"
    assert result.external_url == "https://www.instagram.com/reel/abc/"

    create, upload, status1, status2, publish, permalink = session.calls

    assert create["url"] == "https://graph.facebook.com/v26.0/17841400000000000/media"
    assert create["headers"]["Authorization"] == f"Bearer {TOKEN}"
    assert create["json"] == {
        "media_type": "REELS",
        "caption": "Upgrade your desk. #Lighting",
        "is_ai_generated": True,
        "upload_type": "resumable",
    }

    assert upload["url"] == "https://rupload.facebook.com/ig-api-upload/v26.0/container-1"
    assert upload["headers"]["Authorization"] == f"OAuth {TOKEN}"
    assert upload["headers"]["offset"] == "0"
    assert upload["headers"]["file_size"] == "10"
    assert upload["uploaded"] == b"0123456789"

    assert status1["url"] == "https://graph.facebook.com/v26.0/container-1"
    assert status1["params"] == {"fields": "status_code"}
    assert clock.sleeps == [15.0]  # waited once, between IN_PROGRESS and FINISHED

    assert publish["url"] == "https://graph.facebook.com/v26.0/17841400000000000/media_publish"
    assert publish["json"] == {"creation_id": "container-1"}
    assert permalink["params"] == {"fields": "permalink"}


def test_url_mode_sends_a_public_link_and_does_not_upload(video):
    publisher, session, _ = make(
        [
            ok({"id": "c1"}),
            ok({"status_code": "FINISHED"}),
            ok({"id": "m1"}),
            ok({"permalink": "https://www.instagram.com/reel/x/"}),
        ],
        upload_mode="url",
        public_base_url="https://my-tunnel.example.com/media/",
    )

    publisher.publish(video, "t", "caption")

    create = session.calls[0]

    assert create["json"]["video_url"] == "https://my-tunnel.example.com/media/reel.mp4"
    assert "upload_type" not in create["json"]
    assert not any("rupload" in call["url"] for call in session.calls)


def test_url_mode_requires_a_public_base_url(video):
    publisher, session, _ = make([], upload_mode="url")

    with pytest.raises(PublishError, match="INSTAGRAM_PUBLIC_VIDEO_BASE_URL"):
        publisher.publish(video, "t", "caption")

    assert session.calls == []


def test_invalid_upload_mode_is_rejected():
    with pytest.raises(PublishError, match="INSTAGRAM_UPLOAD_MODE"):
        InstagramPublisher(access_token="x", account_id="1", upload_mode="carrier-pigeon")


def test_ai_label_can_be_turned_off(video):
    publisher, session, _ = make(
        [ok({"id": "c"}), ok({"success": True}), ok({"status_code": "FINISHED"}), ok({"id": "m"}), ok({})],
        ai_label=False,
    )

    publisher.publish(video, "t", "caption")

    assert "is_ai_generated" not in session.calls[0]["json"]


def test_processing_error_stops_before_publishing(video):
    publisher, session, _ = make(
        [ok({"id": "c"}), ok({"success": True}), ok({"status_code": "ERROR"})]
    )

    with pytest.raises(PublishError, match="could not process the video"):
        publisher.publish(video, "t", "caption")

    assert not any(call["url"].endswith("media_publish") for call in session.calls)


def test_gives_up_if_instagram_never_finishes(video):
    publisher, session, clock = make(
        [ok({"id": "c"}), ok({"success": True})] + [ok({"status_code": "IN_PROGRESS"})] * 40,
        poll_interval=15,
        max_wait=60,
    )

    with pytest.raises(PublishError, match="still processing"):
        publisher.publish(video, "t", "caption")

    assert clock.now >= 60
    assert not any(call["url"].endswith("media_publish") for call in session.calls)


def test_instagram_errors_become_readable_messages_without_the_token(video):
    publisher, _, _ = make(
        [
            FakeResponse(
                {"error": {"message": f"Invalid OAuth access token {TOKEN}", "code": 190}},
                status_code=400,
            )
        ]
    )

    with pytest.raises(PublishError) as error:
        publisher.publish(video, "t", "caption")

    assert "190" in str(error.value)
    assert TOKEN not in str(error.value)


def test_upload_failure_is_reported(video):
    publisher, _, _ = make(
        [
            ok({"id": "c"}),
            FakeResponse(
                {"debug_info": {"retriable": False, "type": "ProcessingFailedError", "message": "bad video"}},
                status_code=400,
            ),
        ]
    )

    with pytest.raises(PublishError, match="upload failed: bad video"):
        publisher.publish(video, "t", "caption")


def test_network_problem_is_reported(video):
    publisher, _, _ = make([requests.ConnectionError("no internet")])

    with pytest.raises(PublishError, match="Could not reach Instagram"):
        publisher.publish(video, "t", "caption")


def test_http_error_without_a_json_body(video):
    publisher, _, _ = make([FakeResponse(None, status_code=502)])

    with pytest.raises(PublishError, match="HTTP 502"):
        publisher.publish(video, "t", "caption")


def test_caption_that_is_too_long_never_reaches_instagram(video):
    publisher, session, _ = make([])

    with pytest.raises(PublishError, match="2200"):
        publisher.publish(video, "t", "x" * 2201)

    assert session.calls == []


def test_missing_video_file_is_reported(tmp_path):
    publisher, session, _ = make([])

    with pytest.raises(PublishError, match="not found"):
        publisher.publish(tmp_path / "missing.mp4", "t", "caption")

    assert session.calls == []


def test_the_reel_still_counts_as_published_if_the_permalink_lookup_fails(video):
    publisher, _, _ = make(
        [
            ok({"id": "c"}),
            ok({"success": True}),
            ok({"status_code": "FINISHED"}),
            ok({"id": "m1"}),
            FakeResponse({"error": {"message": "nope", "code": 100}}, status_code=400),
        ]
    )

    result = publisher.publish(video, "t", "caption")

    assert result.external_id == "m1"
    assert result.external_url is None


def test_factory_needs_a_token_and_account_id(monkeypatch):
    monkeypatch.setattr(instagram, "INSTAGRAM_ACCESS_TOKEN", "")
    monkeypatch.setattr(instagram, "INSTAGRAM_ACCOUNT_ID", "")

    with pytest.raises(PublishError, match="IG_ACCESS_TOKEN and IG_USER_ID"):
        build_instagram_publisher()


def test_factory_reads_the_settings(monkeypatch):
    monkeypatch.setattr(instagram, "INSTAGRAM_ACCESS_TOKEN", "tok")
    monkeypatch.setattr(instagram, "INSTAGRAM_ACCOUNT_ID", "42")
    monkeypatch.setattr(instagram, "INSTAGRAM_UPLOAD_MODE", "url")
    monkeypatch.setattr(instagram, "INSTAGRAM_PUBLIC_VIDEO_BASE_URL", "https://x.example/")

    publisher = build_instagram_publisher()

    assert (publisher.access_token, publisher.account_id) == ("tok", "42")
    assert publisher.upload_mode == "url"
    assert publisher.public_base_url == "https://x.example"
