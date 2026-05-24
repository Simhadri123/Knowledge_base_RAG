import sqlite3
import os

db_path = os.path.join("app.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE kb_articles ADD COLUMN source_document_url VARCHAR(1024)")
    print("Added source_document_url to kb_articles")
except sqlite3.OperationalError as e:
    print(f"Column might already exist or error: {e}")

conn.commit()
conn.close()
