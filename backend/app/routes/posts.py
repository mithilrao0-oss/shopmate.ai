"""
Publish queue: queue an approved reel for Instagram and/or YouTube, then publish it.

While PUBLISH_MODE is "dry-run" (the default) nothing is sent anywhere: a post is
simply recorded as published, so the whole flow can be tested safely.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import BACKEND_DIR, MEDIA_DIR, PUBLISH_MODE
from app.database import get_db_connection
from app.publishing.base import PublishError, Publisher
from app.publishing.dry_run import DryRunPublisher
from app.publishing.instagram import build_instagram_publisher


router = APIRouter(prefix="/api/posts", tags=["Posts"])

Platform = Literal["instagram", "youtube"]

# A reel cannot be queued again for a platform while a post is open or done.
BLOCKING_STATUSES = ("Queued", "Publishing", "Posted")


class QueuePostsRequest(BaseModel):
    review_id: int
    platforms: list[Platform] = Field(min_length=1)


def _now() -> str:
    # Same format and timezone (UTC) as SQLite's CURRENT_TIMESTAMP.
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _mode() -> str:
    return "live" if PUBLISH_MODE == "live" else "dry-run"


def _video_file(video_path: str | None) -> Path | None:
    """The video file inside the media folder, or None if missing or outside it."""

    if not video_path:
        return None

    candidate = (BACKEND_DIR / video_path).resolve()

    try:
        candidate.relative_to(MEDIA_DIR.resolve())
    except ValueError:
        return None

    return candidate if candidate.is_file() else None


def _publisher_for(platform: str) -> Publisher:
    if _mode() != "live":
        return DryRunPublisher(platform)

    if platform == "instagram":
        return build_instagram_publisher()

    # The YouTube publisher comes later.
    raise PublishError(f"Live publishing to {platform} is not set up yet")


def _post_text(product_name: str, payload: dict, platform: str) -> tuple[str, str]:
    """The title and caption that will be posted, built from the approved script."""

    caption = (payload.get("caption") or "").strip()
    hashtags = [tag for tag in (payload.get("hashtags") or []) if isinstance(tag, str)]
    hashtag_text = " ".join(hashtags)

    parts = [caption, hashtag_text]

    if platform == "youtube":
        title = f"{product_name[:90]} #Shorts"

        if "#shorts" not in hashtag_text.lower():
            parts.append("#Shorts")
    else:
        title = product_name[:100]

    return title, "\n\n".join(part for part in parts if part)


def _get_post(connection, post_id: int):
    post = connection.execute(
        "SELECT * FROM posts WHERE id = ?", (post_id,)
    ).fetchone()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.get("/mode")
def get_mode():
    """Whether posts are only recorded (dry-run) or really sent (live)."""

    return {"mode": _mode()}


@router.post("", status_code=201)
def queue_posts(request: QueuePostsRequest):
    """
    Queue an approved reel with a rendered final video for one or more platforms.
    """

    platforms = list(dict.fromkeys(request.platforms))

    connection = get_db_connection()

    try:
        review = connection.execute(
            "SELECT id, productName, contentType, status, payload, video_path "
            "FROM reviews WHERE id = ?",
            (request.review_id,),
        ).fetchone()

        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        if review["contentType"] != "Reel Script":
            raise HTTPException(status_code=400, detail="Only reel scripts can be posted")

        if review["status"] != "Approved":
            raise HTTPException(
                status_code=400, detail="Only approved reels can be queued for posting"
            )

        if _video_file(review["video_path"]) is None:
            raise HTTPException(
                status_code=400,
                detail="Render a final video for this reel before posting it",
            )

        try:
            payload = json.loads(review["payload"] or "{}")
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid reel script payload")

        placeholders = ",".join("?" for _ in BLOCKING_STATUSES)

        existing = connection.execute(
            f"SELECT platform, status FROM posts "
            f"WHERE review_id = ? AND platform IN ({','.join('?' for _ in platforms)}) "
            f"AND status IN ({placeholders})",
            (request.review_id, *platforms, *BLOCKING_STATUSES),
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"This reel is already {existing['status']} for {existing['platform']}",
            )

        created_ids = []

        for platform in platforms:
            title, caption = _post_text(review["productName"], payload, platform)

            cursor = connection.execute(
                "INSERT INTO posts (review_id, platform, title, caption, video_path) "
                "VALUES (?, ?, ?, ?, ?)",
                (request.review_id, platform, title, caption, review["video_path"]),
            )

            created_ids.append(cursor.lastrowid)

        connection.commit()

        return {
            "posts": [dict(_get_post(connection, post_id)) for post_id in created_ids]
        }

    finally:
        connection.close()


@router.get("")
def list_posts(status: str | None = None, review_id: int | None = None):
    """List posts, newest first. Optionally filter by status or review."""

    query = "SELECT * FROM posts WHERE 1 = 1"
    values: list = []

    if status:
        query += " AND status = ?"
        values.append(status)

    if review_id is not None:
        query += " AND review_id = ?"
        values.append(review_id)

    query += " ORDER BY id DESC"

    connection = get_db_connection()

    try:
        return [dict(row) for row in connection.execute(query, values).fetchall()]
    finally:
        connection.close()


@router.get("/{post_id}")
def get_post(post_id: int):
    connection = get_db_connection()

    try:
        return dict(_get_post(connection, post_id))
    finally:
        connection.close()


@router.post("/{post_id}/publish")
def publish_post(post_id: int):
    """
    Publish a queued post now. The result is saved on the post: check its
    status (Posted or Failed) and its error message.
    """

    connection = get_db_connection()

    try:
        post = _get_post(connection, post_id)

        # Claim the post first, so a double click can never publish it twice.
        claimed = connection.execute(
            "UPDATE posts SET status = 'Publishing', updatedAt = ? "
            "WHERE id = ? AND status = 'Queued'",
            (_now(), post_id),
        ).rowcount

        connection.commit()

        if claimed == 0:
            raise HTTPException(
                status_code=409,
                detail=f"This post is {post['status']}; only Queued posts can be published",
            )

        mode = _mode()

        try:
            # Re-check at the last moment: the reel may have been rejected since queueing.
            review = connection.execute(
                "SELECT status FROM reviews WHERE id = ?", (post["review_id"],)
            ).fetchone()

            if not review or review["status"] != "Approved":
                raise PublishError("The reel is no longer approved")

            video_file = _video_file(post["video_path"])

            if video_file is None:
                raise PublishError("The video file is missing")

            result = _publisher_for(post["platform"]).publish(
                video_file, post["title"] or "", post["caption"] or ""
            )

        except Exception as error:
            connection.execute(
                "UPDATE posts SET status = 'Failed', error = ?, mode = ?, updatedAt = ? "
                "WHERE id = ?",
                (str(error)[:500], mode, _now(), post_id),
            )
        else:
            connection.execute(
                "UPDATE posts SET status = 'Posted', mode = ?, external_id = ?, "
                "external_url = ?, error = NULL, postedAt = ?, updatedAt = ? WHERE id = ?",
                (mode, result.external_id, result.external_url, _now(), _now(), post_id),
            )

        connection.commit()

        return dict(_get_post(connection, post_id))

    finally:
        connection.close()


@router.post("/{post_id}/cancel")
def cancel_post(post_id: int):
    """Cancel a post that has not been published yet."""

    connection = get_db_connection()

    try:
        post = _get_post(connection, post_id)

        cancelled = connection.execute(
            "UPDATE posts SET status = 'Cancelled', updatedAt = ? "
            "WHERE id = ? AND status = 'Queued'",
            (_now(), post_id),
        ).rowcount

        connection.commit()

        if cancelled == 0:
            raise HTTPException(
                status_code=409,
                detail=f"This post is {post['status']}; only Queued posts can be cancelled",
            )

        return dict(_get_post(connection, post_id))

    finally:
        connection.close()
