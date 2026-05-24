import sqlite3
import os
import uuid

db_path = os.path.join("app.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE chat_histories ADD COLUMN session_id VARCHAR(255)")
    print("Added session_id to chat_histories")
except sqlite3.OperationalError as e:
    print(f"Column might already exist or error: {e}")

# Assign a unique session ID to any existing chats so they don't break
cursor.execute("SELECT id FROM chat_histories WHERE session_id IS NULL")
rows = cursor.fetchall()
for row in rows:
    new_uuid = str(uuid.uuid4())
    cursor.execute("UPDATE chat_histories SET session_id = ? WHERE id = ?", (new_uuid, row[0]))

if rows:
    print(f"Updated {len(rows)} old chat histories with unique session IDs.")

conn.commit()
conn.close()
