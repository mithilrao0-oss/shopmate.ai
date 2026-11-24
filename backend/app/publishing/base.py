"""Shared pieces for every publisher (dry-run now; Instagram and YouTube later)."""

from dataclasses import dataclass
from pathlib import Path


class PublishError(Exception):
    """A post could not be published. The message is saved on the post."""


@dataclass
class PublishResult:
    external_id: str
    external_url: str | None = None


class Publisher:
    """One publisher per platform. Each implements publish()."""

    platform: str = ""

    def publish(self, video_file: Path, title: str, caption: str) -> PublishResult:
        raise NotImplementedError
