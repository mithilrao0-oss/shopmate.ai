"""A publisher that contacts nobody: used to test the whole flow safely."""

import uuid
from pathlib import Path

from app.publishing.base import PublishError, PublishResult, Publisher


class DryRunPublisher(Publisher):
    def __init__(self, platform: str):
        self.platform = platform

    def publish(self, video_file: Path, title: str, caption: str) -> PublishResult:
        if not video_file.is_file():
            raise PublishError(f"Video file not found: {video_file.name}")

        return PublishResult(
            external_id=f"dry-run-{self.platform}-{uuid.uuid4().hex[:8]}",
            external_url=None,
        )
