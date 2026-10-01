import sqlite3

from app.config import DATABASE_PATH


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
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

    connection.commit()
    connection.close()
