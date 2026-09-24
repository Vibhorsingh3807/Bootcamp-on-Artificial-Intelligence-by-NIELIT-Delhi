import sqlite3
import os
from datetime import datetime

# Local SQLite database file ka path
DB_PATH = os.path.join(os.path.dirname(__file__), "echosign.db")

def get_connection():
    # SQLite connection banate hain aur row_factory set karte hain taaki dict jaisa data mile
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initial database tables create karta hai agar pehle se nahi bani hain."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Conversations table: Har gesture ya speech interaction ka record
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        channel TEXT NOT NULL,
        input_raw TEXT NOT NULL,
        output_text TEXT NOT NULL,
        sentiment TEXT NOT NULL,
        urgency TEXT NOT NULL,
        urgency_score REAL DEFAULT 0.0
    );
    """)

    conn.commit()
    conn.close()

def log_conversation(channel, input_raw, output_text, sentiment, urgency, urgency_score=0.0):
    """Nayi conversation entry SQLite database mein save karta hai."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO conversations (timestamp, channel, input_raw, output_text, sentiment, urgency, urgency_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (now_str, channel, input_raw, output_text, sentiment, urgency, urgency_score))
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id

def get_recent_conversations(limit=50):
    """Pichli interactions ko fetch karke UI table mein dikhane ke liye."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM conversations
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_analytics_summary():
    """Dashboard metrics: Total count aur sentiment breakdown nikalte hain."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM conversations")
    total_convs = cursor.fetchone()["total"]

    cursor.execute("SELECT sentiment, COUNT(*) as count FROM conversations GROUP BY sentiment")
    sentiment_counts = {row["sentiment"]: row["count"] for row in cursor.fetchall()}

    cursor.execute("SELECT urgency, COUNT(*) as count FROM conversations GROUP BY urgency")
    urgency_counts = {row["urgency"]: row["count"] for row in cursor.fetchall()}

    conn.close()
    return {
        "total_conversations": total_convs,
        "sentiments": sentiment_counts,
        "urgencies": urgency_counts
    }

init_db()
