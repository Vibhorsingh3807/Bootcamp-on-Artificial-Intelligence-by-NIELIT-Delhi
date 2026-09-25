import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "aircanvas.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artworks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        title TEXT NOT NULL,
        strokes_count INTEGER DEFAULT 0,
        colors_used TEXT,
        image_path TEXT NOT NULL,
        thumbnail_base64 TEXT
    );
    """)
    conn.commit()
    conn.close()

def save_artwork(title, strokes_count, colors_used, image_path, thumbnail_base64=""):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO artworks (timestamp, title, strokes_count, colors_used, image_path, thumbnail_base64)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (now_str, title, strokes_count, colors_used, image_path, thumbnail_base64))
    conn.commit()
    art_id = cursor.lastrowid
    conn.close()
    return art_id

def get_gallery(limit=30):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM artworks
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def delete_artwork(artwork_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image_path FROM artworks WHERE id = ?", (artwork_id,))
    row = cursor.fetchone()
    if row and os.path.exists(row["image_path"]):
        try:
            os.remove(row["image_path"])
        except Exception:
            pass
    cursor.execute("DELETE FROM artworks WHERE id = ?", (artwork_id,))
    conn.commit()
    conn.close()
    return True

init_db()
