from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database import get_db_connection


router = APIRouter(
    prefix="/api/reviews",
    tags=["Review Queue"]
)


# ---------- Request Models ----------

class ReviewCreate(BaseModel):
    productName: str
    contentType: str
    tone: str
    content: str


class ReviewStatusUpdate(BaseModel):
    status: str


# ---------- Get Reviews ----------

@router.get("")
def get_reviews():
    connection = get_db_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            productName,
            contentType,
            tone,
            content,
            status,
            createdAt
        FROM reviews
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


# ---------- Create Review ----------

@router.post("")
def create_review(review: ReviewCreate):
    connection = get_db_connection()

    cursor = connection.execute(
        """
        INSERT INTO reviews (
            productName,
            contentType,
            tone,
            content,
            status
        )
        VALUES (?, ?, ?, ?, 'Pending')
        """,
        (
            review.productName,
            review.contentType,
            review.tone,
            review.content
        )
    )

    connection.commit()

    review_id = cursor.lastrowid

    row = connection.execute(
        """
        SELECT
            id,
            productName,
            contentType,
            tone,
            content,
            status,
            createdAt
        FROM reviews
        WHERE id = ?
        """,
        (review_id,)
    ).fetchone()

    connection.close()

    return dict(row)


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
        """
        SELECT
            id,
            productName,
            contentType,
            tone,
            content,
            status,
            createdAt
        FROM reviews
        WHERE id = ?
        """,
        (review_id,)
    ).fetchone()

    connection.close()

    return dict(row)