import sqlite3

from app.config import DATABASE_PATH


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db_connection()

    # Products table: store products with their metadata and image path.
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT,
            cost REAL,
            price REAL,
            rating REAL,
            status TEXT,
            supplier TEXT,
            highlights TEXT,
            image_path TEXT,
            createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Reviews table: AI-generated drafts awaiting human review.
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            productName TEXT NOT NULL,
            contentType TEXT NOT NULL,
            tone TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            payload TEXT
        )
        """
    )

    # Databases created before structured reel scripts have no payload column.
    columns = [
        row["name"]
        for row in connection.execute("PRAGMA table_info(reviews)").fetchall()
    ]

    if "payload" not in columns:
        connection.execute("ALTER TABLE reviews ADD COLUMN payload TEXT")

    if "video_path" not in columns:
        connection.execute("ALTER TABLE reviews ADD COLUMN video_path TEXT")

    # Posts table: one row per reel per platform (Instagram, YouTube).
    # Status: Queued -> Publishing -> Posted, or Failed / Cancelled.
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Queued',
            title TEXT,
            caption TEXT,
            video_path TEXT NOT NULL,
            mode TEXT,
            external_id TEXT,
            external_url TEXT,
            error TEXT,
            postedAt TEXT,
            createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (review_id) REFERENCES reviews (id)
        )
        """
    )

    connection.commit()
    connection.close()
