import sqlite3


DATABASE = "shopmate.db"


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
    