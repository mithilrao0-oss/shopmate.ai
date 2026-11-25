import json

import pytest
from fastapi.testclient import TestClient

from app.database import get_db_connection, initialize_database
from app.main import app


@pytest.fixture()
def env(tmp_path, monkeypatch):
    """A fresh temporary database and media folder for every test."""

    (tmp_path / "media").mkdir()

    monkeypatch.setattr("app.database.DATABASE_PATH", tmp_path / "test.db")
    monkeypatch.setattr("app.routes.posts.BACKEND_DIR", tmp_path)
    monkeypatch.setattr("app.routes.posts.MEDIA_DIR", tmp_path / "media")
    monkeypatch.setattr("app.routes.posts.PUBLISH_MODE", "dry-run")

    initialize_database()

    return tmp_path, TestClient(app)


def make_review(
    tmp_path,
    status="Approved",
    content_type="Reel Script",
    with_video=True,
    video_path="media/reel.mp4",
):
    if with_video:
        target = tmp_path / video_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"fake video")
    else:
        video_path = None

    payload = json.dumps(
        {
            "scenes": [{"voiceover": "Hi", "on_screen_text": "Hi"}],
            "caption": "Upgrade your desk.",
            "hashtags": ["#HomeOffice", "#Lighting"],
        }
    )

    connection = get_db_connection()
    cursor = connection.execute(
        "INSERT INTO reviews (productName, contentType, tone, content, status, payload, video_path) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ("LED Desk Lamp", content_type, "Friendly", "text", status, payload, video_path),
    )
    connection.commit()
    review_id = cursor.lastrowid
    connection.close()

    return review_id


def queue(client, review_id, platforms=("instagram", "youtube")):
    return client.post(
        "/api/posts", json={"review_id": review_id, "platforms": list(platforms)}
    )


def test_queue_creates_one_post_per_platform(env):
    tmp_path, client = env
    response = queue(client, make_review(tmp_path))

    assert response.status_code == 201

    posts = response.json()["posts"]

    assert [p["platform"] for p in posts] == ["instagram", "youtube"]
    assert all(p["status"] == "Queued" for p in posts)

    instagram, youtube = posts

    assert instagram["caption"] == "Upgrade your desk.\n\n#HomeOffice #Lighting"
    assert youtube["title"] == "LED Desk Lamp #Shorts"
    assert youtube["caption"].endswith("#Shorts")


def test_queue_rejects_unapproved_review(env):
    tmp_path, client = env
    assert queue(client, make_review(tmp_path, status="Pending")).status_code == 400


def test_queue_rejects_review_without_video(env):
    tmp_path, client = env
    assert queue(client, make_review(tmp_path, with_video=False)).status_code == 400


def test_queue_rejects_non_reel_content(env):
    tmp_path, client = env
    review_id = make_review(tmp_path, content_type="Product Caption")
    assert queue(client, review_id).status_code == 400


def test_queue_rejects_unknown_review(env):
    _, client = env
    assert queue(client, 999).status_code == 404


def test_video_outside_media_folder_is_refused(env):
    tmp_path, client = env
    (tmp_path / "secret.mp4").write_bytes(b"not a reel")
    review_id = make_review(tmp_path, video_path="media/../secret.mp4")
    assert queue(client, review_id).status_code == 400


def test_same_reel_cannot_be_queued_twice_for_a_platform(env):
    tmp_path, client = env
    review_id = make_review(tmp_path)

    assert queue(client, review_id, ["instagram"]).status_code == 201
    assert queue(client, review_id, ["instagram"]).status_code == 409
    # A different platform is still allowed.
    assert queue(client, review_id, ["youtube"]).status_code == 201


def test_publish_in_dry_run_marks_post_as_posted(env):
    tmp_path, client = env
    post = queue(client, make_review(tmp_path), ["instagram"]).json()["posts"][0]

    result = client.post(f"/api/posts/{post['id']}/publish").json()

    assert result["status"] == "Posted"
    assert result["mode"] == "dry-run"
    assert result["external_id"].startswith("dry-run-instagram-")
    assert result["postedAt"]


def test_post_cannot_be_published_twice(env):
    tmp_path, client = env
    post = queue(client, make_review(tmp_path), ["instagram"]).json()["posts"][0]

    assert client.post(f"/api/posts/{post['id']}/publish").status_code == 200
    assert client.post(f"/api/posts/{post['id']}/publish").status_code == 409


def test_publish_fails_if_reel_was_rejected_after_queueing(env):
    tmp_path, client = env
    review_id = make_review(tmp_path)
    post = queue(client, review_id, ["instagram"]).json()["posts"][0]

    connection = get_db_connection()
    connection.execute("UPDATE reviews SET status = 'Rejected' WHERE id = ?", (review_id,))
    connection.commit()
    connection.close()

    result = client.post(f"/api/posts/{post['id']}/publish").json()

    assert result["status"] == "Failed"
    assert "no longer approved" in result["error"]


def test_live_mode_fails_cleanly_until_real_publishers_exist(env, monkeypatch):
    tmp_path, client = env
    post = queue(client, make_review(tmp_path), ["youtube"]).json()["posts"][0]

    monkeypatch.setattr("app.routes.posts.PUBLISH_MODE", "live")

    result = client.post(f"/api/posts/{post['id']}/publish").json()

    assert result["status"] == "Failed"
    assert "not set up yet" in result["error"]


def test_cancel_then_requeue(env):
    tmp_path, client = env
    review_id = make_review(tmp_path)
    post = queue(client, review_id, ["instagram"]).json()["posts"][0]

    assert client.post(f"/api/posts/{post['id']}/cancel").json()["status"] == "Cancelled"
    assert client.post(f"/api/posts/{post['id']}/cancel").status_code == 409
    assert queue(client, review_id, ["instagram"]).status_code == 201


def test_list_and_filter_posts(env):
    tmp_path, client = env
    review_id = make_review(tmp_path)
    queue(client, review_id)
    first = client.get("/api/posts").json()

    assert len(first) == 2
    assert first[0]["id"] > first[1]["id"]  # newest first
    assert len(client.get("/api/posts?status=Posted").json()) == 0
    assert len(client.get(f"/api/posts?review_id={review_id}").json()) == 2


def test_mode_endpoint(env):
    _, client = env
    assert client.get("/api/posts/mode").json() == {"mode": "dry-run"}


def test_live_instagram_without_credentials_fails_with_a_clear_message(env, monkeypatch):
    tmp_path, client = env
    post = queue(client, make_review(tmp_path), ["instagram"]).json()["posts"][0]

    monkeypatch.setattr("app.routes.posts.PUBLISH_MODE", "live")
    monkeypatch.setattr("app.publishing.instagram.INSTAGRAM_ACCESS_TOKEN", "")
    monkeypatch.setattr("app.publishing.instagram.INSTAGRAM_ACCOUNT_ID", "")

    result = client.post(f"/api/posts/{post['id']}/publish").json()

    assert result["status"] == "Failed"
    assert "IG_ACCESS_TOKEN" in result["error"]


def test_live_instagram_publish_is_recorded(env, monkeypatch):
    from app.publishing.base import PublishResult, Publisher

    class FakeInstagram(Publisher):
        platform = "instagram"
        seen = {}

        def publish(self, video_file, title, caption):
            FakeInstagram.seen = {"file": video_file.name, "caption": caption}
            return PublishResult(external_id="media-77", external_url="https://www.instagram.com/reel/q/")

    tmp_path, client = env
    post = queue(client, make_review(tmp_path), ["instagram"]).json()["posts"][0]

    monkeypatch.setattr("app.routes.posts.PUBLISH_MODE", "live")
    monkeypatch.setattr("app.routes.posts.build_instagram_publisher", lambda: FakeInstagram())

    result = client.post(f"/api/posts/{post['id']}/publish").json()

    assert result["status"] == "Posted"
    assert result["mode"] == "live"
    assert result["external_id"] == "media-77"
    assert result["external_url"] == "https://www.instagram.com/reel/q/"
    assert FakeInstagram.seen["file"] == "reel.mp4"
    assert "Upgrade your desk." in FakeInstagram.seen["caption"]
