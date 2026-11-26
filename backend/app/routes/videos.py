
import json
from pathlib import Path
from typing import Literal

import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import OLLAMA_MODEL, OLLAMA_URL
from app.database import get_db_connection
from app.video.renderer import VideoRenderer
from app.video.tts import TextToSpeech


router = APIRouter(prefix="/api/videos", tags=["Videos"])

# Media directory for outputs.
MEDIA_DIR = Path(__file__).resolve().parent.parent.parent / "media"
MEDIA_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


class RenderRequest(BaseModel):
    review_id: int
    product_image_path: str | None = None
    # "preview" renders a smaller, faster video for checking a script.
    quality: Literal["final", "preview"] = "final"


def _validated_image(path_text: str | None) -> Path:
    """Only real image files are accepted, never an arbitrary file on the machine."""

    if not path_text:
        raise HTTPException(
            status_code=400,
            detail="Product image path is required and must exist",
        )

    path = Path(path_text)

    if path.suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail="Product image must be a .jpg, .jpeg, .png or .webp file",
        )

    if not path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Product image path is required and must exist",
        )

    return path


def _unload_ollama_model() -> None:
    """
    Free RAM before rendering by asking Ollama to unload the model.
    Best effort: if Ollama is not running, rendering just carries on.
    """

    try:
        requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "keep_alive": 0},
            timeout=5,
        )
    except requests.RequestException:
        pass


@router.post("/render")
def render_video(request: RenderRequest):
    """
    Render a reel script from an approved review into an MP4 video.
    """

    image_path = _validated_image(request.product_image_path)

    connection = get_db_connection()
    renderer = None

    try:
        review = connection.execute(
            """
            SELECT id, productName, payload, status, contentType
            FROM reviews
            WHERE id = ?
            """,
            (request.review_id,),
        ).fetchone()

        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        if review["status"] != "Approved":
            raise HTTPException(
                status_code=400,
                detail="Only approved reviews can be rendered",
            )

        if review["contentType"] != "Reel Script":
            raise HTTPException(
                status_code=400,
                detail="Only Reel Script reviews can be rendered",
            )

        if not review["payload"]:
            raise HTTPException(
                status_code=400,
                detail="This review does not have a reel script payload",
            )

        try:
            payload = json.loads(review["payload"])
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid reel script payload",
            )

        scenes = payload.get("scenes") or []

        if not scenes:
            raise HTTPException(
                status_code=400,
                detail="The reel script has no scenes",
            )

        _unload_ollama_model()

        renderer = VideoRenderer()

        # One voiceover per scene, so every scene is timed to its own audio.
        try:
            scene_audio = TextToSpeech(rate=140).synthesize_scenes(
                [scene.get("voiceover", "") for scene in scenes],
                renderer.temp_dir,
                prefix=f"voiceover_{request.review_id}",
            )
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"TTS failed: {error}",
            )

        suffix = "_preview" if request.quality == "preview" else ""
        file_name = f"reel_{request.review_id}_{image_path.stem}{suffix}.mp4"

        try:
            renderer.render(
                str(image_path),
                payload,
                scene_audio,
                str(MEDIA_DIR / file_name),
                quality=request.quality,
            )
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Video rendering failed: {error}",
            )

        relative_path = f"media/{file_name}"

        # A preview does not replace the saved final video.
        if request.quality == "final":
            connection.execute(
                "UPDATE reviews SET video_path = ? WHERE id = ?",
                (relative_path, request.review_id),
            )
            connection.commit()

        return {
            "review_id": request.review_id,
            "video_path": relative_path,
            "quality": request.quality,
            "duration_seconds": round(renderer.duration, 1),
            "warnings": renderer.warnings,
            "message": "Video rendered successfully",
        }

    finally:
        if renderer:
            renderer.cleanup()

        connection.close()


@router.get("/{review_id}/file")
def get_video_file(review_id: int):
    """Stream the rendered MP4 video for browser preview."""

    connection = get_db_connection()

    try:
        review = connection.execute(
            "SELECT id, video_path FROM reviews WHERE id = ?",
            (review_id,),
        ).fetchone()
    finally:
        connection.close()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if not review["video_path"]:
        raise HTTPException(
            status_code=404,
            detail="No video has been rendered yet",
        )

    video_path = (MEDIA_DIR.parent / review["video_path"]).resolve()

    try:
        video_path.relative_to(MEDIA_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid video path",
        )

    if not video_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Video file not found",
        )

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=video_path.name,
    )


@router.get("/{review_id}")
def get_video(review_id: int):
    """Get the video path for a review, if it exists."""

    connection = get_db_connection()

    try:
        review = connection.execute(
            "SELECT id, video_path FROM reviews WHERE id = ?",
            (review_id,),
        ).fetchone()
    finally:
        connection.close()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if not review["video_path"]:
        raise HTTPException(
            status_code=404,
            detail="No video has been rendered yet",
        )

    return {
        "review_id": review_id,
        "video_path": review["video_path"],
    }
