import sqlite3
import os

db_path = os.path.join("app.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE kb_articles ADD COLUMN source_document VARCHAR(255)")
    print("Added source_document to kb_articles")
except sqlite3.OperationalError as e:
    print(f"Error adding column: {e}")

try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_histories (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        query TEXT NOT NULL,
        answer TEXT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users (id)
    )
    """)
    print("Created chat_histories table")
except sqlite3.OperationalError as e:
    print(f"Error creating table: {e}")

conn.commit()
conn.close()
