import os
import base64
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from AirCanvas.database import init_db, save_artwork, get_gallery, delete_artwork
from AirCanvas.shape_engine import recognize_shape
from AirCanvas.voice_nlp import parse_voice_command

app = FastAPI(
    title="AirCanvas AI — Touchless Gesture Whiteboard & Smart Interactive Canvas",
    description="Real-Time Hand Gesture Air-Drawing with AI Smart Shape Recognition and Voice Controls",
    version="1.0.0"
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
GALLERY_DIR = os.path.join(os.path.dirname(__file__), "gallery")
os.makedirs(GALLERY_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/gallery", StaticFiles(directory=GALLERY_DIR), name="gallery")

init_db()

# --- Pydantic Schemas ---
class SaveArtworkPayload(BaseModel):
    image_base64: str
    title: Optional[str] = "Untitled Artwork"
    strokes_count: Optional[int] = 0
    colors_used: Optional[str] = ""

class ShapePayload(BaseModel):
    points: List[List[float]]

class VoicePayload(BaseModel):
    text: str

@app.get("/")
def get_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"status": "AirCanvas AI server is running!"})

@app.post("/api/snap_shape")
def snap_shape_endpoint(payload: ShapePayload):
    """
    Analyzes raw stroke coordinates and recognizes geometric shapes (Circle, Rectangle, Triangle, Line).
    """
    result = recognize_shape(payload.points)
    return JSONResponse(result)

@app.post("/api/parse_voice")
def parse_voice_endpoint(payload: VoicePayload):
    """
    Parses speech transcripts into structured AirCanvas tool commands.
    """
    res = parse_voice_command(payload.text)
    return JSONResponse(res)

@app.post("/api/save_artwork")
def save_artwork_endpoint(payload: SaveArtworkPayload):
    """
    Decodes base64 canvas snapshot, saves PNG file to gallery folder, and records entry in SQLite.
    """
    try:
        raw_b64 = payload.image_base64
        if "," in raw_b64:
            raw_b64 = raw_b64.split(",", 1)[1]
        
        img_bytes = base64.b64decode(raw_b64)
        filename = f"art_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(2).hex()}.png"
        filepath = os.path.join(GALLERY_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(img_bytes)

        art_id = save_artwork(
            title=payload.title,
            strokes_count=payload.strokes_count,
            colors_used=payload.colors_used,
            image_path=filepath,
            thumbnail_base64=""
        )

        return JSONResponse({
            "status": "success",
            "id": art_id,
            "filename": filename,
            "url": f"/gallery/{filename}",
            "message": "Artwork saved to Gallery successfully!"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/gallery")
def get_gallery_endpoint():
    """
    Returns list of saved artworks from SQLite database.
    """
    rows = get_gallery(limit=30)
    for r in rows:
        fn = os.path.basename(r["image_path"])
        r["url"] = f"/gallery/{fn}"
    return JSONResponse(rows)

@app.delete("/api/gallery/{artwork_id}")
def delete_artwork_endpoint(artwork_id: int):
    """
    Deletes an artwork from database and filesystem.
    """
    success = delete_artwork(artwork_id)
    return JSONResponse({"status": "success", "deleted_id": artwork_id})
