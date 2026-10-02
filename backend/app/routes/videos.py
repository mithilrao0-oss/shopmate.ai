import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database import get_db_connection
from app.video.tts import TextToSpeech
from app.video.renderer import VideoRenderer


router = APIRouter(prefix="/api/videos", tags=["Videos"])

# Media directory for outputs.
MEDIA_DIR = Path(__file__).resolve().parent.parent.parent / "media"
MEDIA_DIR.mkdir(exist_ok=True)


class RenderRequest(BaseModel):
    review_id: int
    product_image_path: str | None = None


@router.post("/render")
def render_video(request: RenderRequest):
    """
    Render a reel script from a review into an MP4 video.
    """

    connection = get_db_connection()

    # Get the review.
    review = connection.execute(
        "SELECT id, productName, payload FROM reviews WHERE id = ?",
        (request.review_id,),
    ).fetchone()

    if not review:
        connection.close()
        raise HTTPException(status_code=404, detail="Review not found")

    payload_str = review["payload"]

    if not payload_str:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="This review does not have a reel script payload",
        )

    import json

    try:
        payload = json.loads(payload_str)
    except (ValueError, TypeError):
        connection.close()
        raise HTTPException(status_code=400, detail="Invalid reel script payload")

    # Get product image.
    product_image_path = request.product_image_path

    if not product_image_path or not os.path.exists(product_image_path):
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Product image path is required and must exist",
        )

    # Generate voiceover.
    try:
        tts = TextToSpeech(rate=140)

        temp_audio = MEDIA_DIR / f"voiceover_{request.review_id}.wav"

        voiceover_text = " ".join(
            scene.get("voiceover", "") for scene in payload.get("scenes", [])
        )

        tts.synthesize_to_file(voiceover_text, str(temp_audio))
    except Exception as e:
        connection.close()
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

    # Render video.
    try:
        renderer = VideoRenderer()

        output_video = (
            MEDIA_DIR / f"reel_{request.review_id}_{Path(product_image_path).stem}.mp4"
        )

        renderer.render(
            str(product_image_path),
            payload,
            str(temp_audio),
            str(output_video),
        )

        renderer.cleanup()

        # Store video path in the database.
        relative_path = f"media/reel_{request.review_id}_{Path(product_image_path).stem}.mp4"

        connection.execute(
            "UPDATE reviews SET video_path = ? WHERE id = ?",
            (relative_path, request.review_id),
        )

        connection.commit()
        connection.close()

        return {
            "review_id": request.review_id,
            "video_path": relative_path,
            "message": "Video rendered successfully",
        }

    except Exception as e:
        connection.close()
        raise HTTPException(status_code=500, detail=f"Video rendering failed: {e}")


@router.get("/{review_id}")
def get_video(review_id: int):
    """
    Get the video path for a review (if it exists).
    """

    connection = get_db_connection()

    review = connection.execute(
        "SELECT id, video_path FROM reviews WHERE id = ?",
        (review_id,),
    ).fetchone()

    connection.close()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if not review["video_path"]:
        raise HTTPException(status_code=404, detail="No video has been rendered yet")

    return {"review_id": review_id, "video_path": review["video_path"]}
