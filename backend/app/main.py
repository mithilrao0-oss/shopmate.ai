import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


DATABASE = "shopmate.db"


app = FastAPI(
    title="ShopMate.ai API",
    description="Backend API for the ShopMate.ai AIOT project",
    version="1.0.0"
)


# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Database ----------

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            productName TEXT NOT NULL,
            contentType TEXT NOT NULL,
            tone TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


initialize_database()


# ---------- Request model ----------

class ReviewCreate(BaseModel):
    productName: str
    contentType: str
    tone: str
    content: str


class ReviewStatusUpdate(BaseModel):
    status: str

# ---------- Health ----------

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "ShopMate.ai FastAPI backend is running"
    }


# ---------- Review Queue ----------

@app.get("/api/reviews")
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


@app.post("/api/reviews")
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


@app.patch("/api/reviews/{review_id}")
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