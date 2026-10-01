import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.reel_script import normalize_reel, render_reel_text, validate_reel
from app.database import get_db_connection
from app.responsible_ai import check_content


router = APIRouter(
    prefix="/api/reviews",
    tags=["Review Queue"]
)


REEL_CONTENT_TYPE = "reel script"

COLUMNS = "id, productName, contentType, tone, content, status, createdAt, payload"


# ---------- Request Models ----------

class ReviewCreate(BaseModel):
    productName: str = Field(min_length=1)
    contentType: str = Field(min_length=1)
    tone: str = Field(min_length=1)
    content: str = ""

    # Structured script (reel scripts only) and the product price used to
    # validate it. The price comes from the client for now; it will be read
    # from the database once products are stored there.
    payload: dict | None = None
    price: float | int | None = None


class ReviewStatusUpdate(BaseModel):
    status: str


# ---------- Helpers ----------

def _row_to_dict(row):
    item = dict(row)

    raw_payload = item.get("payload")

    if raw_payload:
        try:
            item["payload"] = json.loads(raw_payload)
        except ValueError:
            item["payload"] = None
    else:
        item["payload"] = None

    return item


# ---------- Get Reviews ----------

@router.get("")
def get_reviews():
    connection = get_db_connection()

    rows = connection.execute(
        f"SELECT {COLUMNS} FROM reviews ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return [_row_to_dict(row) for row in rows]


# ---------- Create Review ----------

@router.post("")
def create_review(review: ReviewCreate):
    # Server-side gate: content that fails validation cannot enter the
    # review queue, whatever the frontend does.
    payload_json = None

    if review.contentType.strip().lower() == REEL_CONTENT_TYPE:
        if review.payload is None:
            raise HTTPException(
                status_code=422,
                detail="Reel scripts must include the structured script."
            )

        reel = normalize_reel(review.payload)
        check = validate_reel(reel, review.productName, review.price)

        if not check["passed"]:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Script check failed: "
                    + "; ".join(check["issues"])
                    + ". Please edit the script and try again."
                )
            )

        content = render_reel_text(review.productName, reel)
        payload_json = json.dumps(reel, ensure_ascii=False)

    else:
        content = review.content.strip()

        if not content:
            raise HTTPException(
                status_code=422,
                detail="Content must not be empty."
            )

        check = check_content(content)

        if not check["passed"]:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Responsible AI check failed: "
                    + ", ".join(check["issues"])
                    + ". Please edit the content and try again."
                )
            )

    connection = get_db_connection()

    cursor = connection.execute(
        """
        INSERT INTO reviews (
            productName,
            contentType,
            tone,
            content,
            status,
            payload
        )
        VALUES (?, ?, ?, ?, 'Pending', ?)
        """,
        (
            review.productName,
            review.contentType,
            review.tone,
            content,
            payload_json
        )
    )

    connection.commit()

    review_id = cursor.lastrowid

    row = connection.execute(
        f"SELECT {COLUMNS} FROM reviews WHERE id = ?",
        (review_id,)
    ).fetchone()

    connection.close()

    return _row_to_dict(row)


# ---------- Update Review Status ----------

@router.patch("/{review_id}")
def update_review_status(
    review_id: int,
    review_update: ReviewStatusUpdate
):
    allowed_statuses = {
        "Pending",
        "Approved",
        "Rejected"
    }

    status = review_update.status

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Status must be Pending, Approved, or Rejected"
        )

    connection = get_db_connection()

    cursor = connection.execute(
        """
        UPDATE reviews
        SET status = ?
        WHERE id = ?
        """,
        (status, review_id)
    )

    connection.commit()

    if cursor.rowcount == 0:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    row = connection.execute(
        f"SELECT {COLUMNS} FROM reviews WHERE id = ?",
        (review_id,)
    ).fetchone()

    connection.close()

    return _row_to_dict(row)
