"""
Instagram Reels publisher (Instagram Platform content publishing API).

Flow: create a REELS media container -> get the video to Instagram ->
wait until the container is FINISHED -> publish it.

Two ways to get the video to Instagram:
  "resumable": upload the local file straight to Meta (no public link needed).
  "url":       Instagram downloads the video from a public link you provide.
"""

import time
from pathlib import Path

import requests

from app.config import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_ACCOUNT_ID,
    INSTAGRAM_AI_LABEL,
    INSTAGRAM_API_HOST,
    INSTAGRAM_API_VERSION,
    INSTAGRAM_PUBLIC_VIDEO_BASE_URL,
    INSTAGRAM_UPLOAD_MODE,
)
from app.publishing.base import PublishError, PublishResult, Publisher

MAX_CAPTION_LENGTH = 2200
UPLOAD_HOST = "https://rupload.facebook.com"
UPLOAD_MODES = ("resumable", "url")


class InstagramPublisher(Publisher):
    platform = "instagram"

    def __init__(
        self,
        access_token: str,
        account_id: str,
        api_host: str = "https://graph.facebook.com",
        api_version: str = "v26.0",
        upload_mode: str = "resumable",
        public_base_url: str = "",
        ai_label: bool = True,
        poll_interval: float = 15.0,
        max_wait: float = 300.0,
        session=None,
        sleep=time.sleep,
        clock=time.monotonic,
    ):
        if upload_mode not in UPLOAD_MODES:
            raise PublishError(
                f"INSTAGRAM_UPLOAD_MODE must be one of {', '.join(UPLOAD_MODES)}"
            )

        self.access_token = access_token
        self.account_id = account_id
        self.api_host = api_host.rstrip("/")
        self.api_version = api_version
        self.upload_mode = upload_mode
        self.public_base_url = public_base_url.rstrip("/")
        self.ai_label = ai_label
        self.poll_interval = poll_interval
        self.max_wait = max_wait

        # session, sleep and clock can be replaced in tests.
        self.session = session or requests.Session()
        self._sleep = sleep
        self._clock = clock

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _graph_url(self, path: str) -> str:
        return f"{self.api_host}/{self.api_version}/{path}"

    def _graph_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}"}

    def _redact(self, text: str) -> str:
        """Never let the access token end up in an error message."""

        if self.access_token:
            text = text.replace(self.access_token, "***")

        return text

    @staticmethod
    def _describe_error(response, body: dict) -> str:
        error = body.get("error")

        if isinstance(error, dict):
            code = error.get("code")
            message = error.get("message") or "unknown error"
            return f"Instagram error {code}: {message}" if code else f"Instagram error: {message}"

        debug_info = body.get("debug_info")

        if isinstance(debug_info, dict):
            detail = debug_info.get("message") or debug_info.get("type") or "unknown error"
            return f"Instagram upload failed: {detail}"

        return f"Instagram returned HTTP {response.status_code}"

    def _call(self, method: str, url: str, timeout: float = 60, **kwargs) -> dict:
        """One HTTP call. Returns the JSON body, or raises PublishError."""

        try:
            response = getattr(self.session, method)(url, timeout=timeout, **kwargs)
        except requests.RequestException as error:
            raise PublishError(self._redact(f"Could not reach Instagram: {error}"))

        try:
            body = response.json()
        except ValueError:
            body = {}

        if not isinstance(body, dict):
            body = {}

        if response.status_code >= 400 or body.get("error"):
            raise PublishError(self._redact(self._describe_error(response, body)))

        return body

    # ------------------------------------------------------------------
    # The four steps
    # ------------------------------------------------------------------

    def _public_url(self, video_file: Path) -> str:
        if not self.public_base_url:
            raise PublishError(
                "INSTAGRAM_PUBLIC_VIDEO_BASE_URL is required when INSTAGRAM_UPLOAD_MODE is 'url'"
            )

        return f"{self.public_base_url}/{video_file.name}"

    def _create_container(self, caption: str, video_url: str | None) -> str:
        body = {"media_type": "REELS", "caption": caption}

        if self.ai_label:
            body["is_ai_generated"] = True

        if video_url:
            body["video_url"] = video_url
        else:
            body["upload_type"] = "resumable"

        data = self._call(
            "post",
            self._graph_url(f"{self.account_id}/media"),
            headers=self._graph_headers(),
            json=body,
        )

        container_id = data.get("id")

        if not container_id:
            raise PublishError("Instagram did not return a media container id")

        return str(container_id)

    def _upload(self, container_id: str, video_file: Path) -> None:
        url = f"{UPLOAD_HOST}/ig-api-upload/{self.api_version}/{container_id}"

        headers = {
            "Authorization": f"OAuth {self.access_token}",
            "offset": "0",
            "file_size": str(video_file.stat().st_size),
        }

        with video_file.open("rb") as stream:
            data = self._call("post", url, timeout=600, headers=headers, data=stream)

        if data.get("success") is not True:
            raise PublishError("Instagram did not confirm the video upload")

    def _wait_until_finished(self, container_id: str) -> None:
        deadline = self._clock() + self.max_wait

        while True:
            data = self._call(
                "get",
                self._graph_url(container_id),
                headers=self._graph_headers(),
                params={"fields": "status_code"},
            )

            status = data.get("status_code")

            if status == "FINISHED":
                return

            if status in ("ERROR", "EXPIRED"):
                raise PublishError(
                    f"Instagram could not process the video (status {status})"
                )

            if self._clock() >= deadline:
                raise PublishError(
                    "Instagram is still processing the video; try publishing again later"
                )

            self._sleep(self.poll_interval)

    def _publish_container(self, container_id: str) -> str:
        data = self._call(
            "post",
            self._graph_url(f"{self.account_id}/media_publish"),
            headers=self._graph_headers(),
            json={"creation_id": container_id},
        )

        media_id = data.get("id")

        if not media_id:
            raise PublishError("Instagram did not return the published media id")

        return str(media_id)

    def _permalink(self, media_id: str) -> str | None:
        """The public link of the post. Best effort: the reel is already live if this fails."""

        try:
            data = self._call(
                "get",
                self._graph_url(media_id),
                headers=self._graph_headers(),
                params={"fields": "permalink"},
            )
        except PublishError:
            return None

        return data.get("permalink")

    # ------------------------------------------------------------------

    def publish(self, video_file: Path, title: str, caption: str) -> PublishResult:
        if not video_file.is_file():
            raise PublishError(f"Video file not found: {video_file.name}")

        if len(caption) > MAX_CAPTION_LENGTH:
            raise PublishError(
                f"The caption is {len(caption)} characters; Instagram allows {MAX_CAPTION_LENGTH}"
            )

        video_url = self._public_url(video_file) if self.upload_mode == "url" else None

        container_id = self._create_container(caption, video_url)

        if self.upload_mode == "resumable":
            self._upload(container_id, video_file)

        self._wait_until_finished(container_id)

        media_id = self._publish_container(container_id)

        return PublishResult(external_id=media_id, external_url=self._permalink(media_id))


def build_instagram_publisher() -> InstagramPublisher:
    """An InstagramPublisher configured from backend/.env."""

    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        raise PublishError(
            "Instagram is not configured: set IG_ACCESS_TOKEN and IG_USER_ID in backend/.env"
        )

    return InstagramPublisher(
        access_token=INSTAGRAM_ACCESS_TOKEN,
        account_id=INSTAGRAM_ACCOUNT_ID,
        api_host=INSTAGRAM_API_HOST,
        api_version=INSTAGRAM_API_VERSION,
        upload_mode=INSTAGRAM_UPLOAD_MODE,
        public_base_url=INSTAGRAM_PUBLIC_VIDEO_BASE_URL,
        ai_label=INSTAGRAM_AI_LABEL,
    )
