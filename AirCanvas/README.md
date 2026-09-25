# 🎨 AirCanvas AI — Touchless Gesture Whiteboard & Smart Interactive Canvas

> **Human-Centric AI Project for Touchless Education, Healthcare & Creative Expression**  
> *Transforming freehand air gestures into digital neon art using Computer Vision, AI Shape Snapping, Voice AI, and Geometric Landmark Analytics.*

---

## 🌟 1. Overview & Human Mission

In traditional classrooms, meeting rooms, and hospitals:
1. **Disabled Children & Students with Fine Motor Impairments** often struggle to hold heavy physical chalk or pens. AirCanvas allows them to express creativity effortlessly by simply moving their hand in the air.
2. **Sterile Medical Environments:** Doctors and surgeons can take notes, annotate X-rays, or draw diagrams without physically touching germ-carrying keyboards or screens.
3. **Touchless Interactive Teaching:** Educators can teach and draw live equations in front of a webcam with zero hardware costs.

---

## ⚡ 2. How to Run (One-Click Launch)

### Method 1: The One-Click Batch Launcher
Double click:
```bat
START_AIRCANVAS.bat
```
*(Available both in the root directory and inside the `AirCanvas/` folder)*.

This will automatically:
1. Initialize the FastAPI server on `http://127.0.0.1:8050`.
2. Resolve any port conflicts.
3. Automatically launch your default web browser!

### Method 2: Python Command Line
```bash
python AirCanvas/run.py
```

---

## 🖐️ 3. Gesture Controls Guide (100% Reliable & Easy)

| Gesture | Visual Sign | Mode Activated | Description & Action |
| :--- | :---: | :--- | :--- |
| **Index Finger Up** | ☝️ | **`DRAWING MODE`** | Only the index fingertip acts as a neon pen. Smooth glowing lines are drawn on screen. |
| **Peace Sign (V)** | ✌️ | **`HOVER & SELECT`** | Index + Middle fingers up. Drawing pauses. Move cursor to the top color bar to select colors in the air! |
| **Open Palm** | ✋ | **`ERASER MODE`** | All 5 fingers extended. Palm acts as a circular eraser wiping the board. |
| **Closed Fist** | ✊ | **`HOLD TO CLEAR`** | Curl all fingers into a fist for 1.4 seconds. A visual circular progress ring fills, then clears the canvas! |
| **Thumbs Up** | 👍 | **`SAVE SNAPSHOT`** | Thumb pointing up, other 4 fingers curled. Holds for 1 second, saves artwork to SQLite Gallery, and downloads PNG. |

---

## 🧠 4. How the AI Stack Works (Bootcamp Concepts Applied)

### A. Computer Vision & Landmark Geometry (Day 2 & Day 4)
- **MediaPipe Hands:** Client-side tracking of **21 3D joint landmarks** at 60 FPS.
- **Euclidean Vector Math:** Check which fingers are extended using vertical coordinates ($y_{\text{tip}} < y_{\text{pip}}$).
- **Sub-Pixel Line Smoothing:** Real-time quadratic Bézier curve interpolation between consecutive $(x, y)$ coordinates to prevent shaky hand lines.

### B. AI Geometric Shape Snapping (Day 4 OpenCV Contour Analysis)
- When "Magic Shape" is enabled:
  - If a drawn stroke has closed endpoints ($d_{\text{endpoints}} / \text{path\_len} < 0.25$), the contour area and perimeter are computed:
    $$\text{Circularity} = 4\pi \frac{\text{Area}}{\text{Perimeter}^2}$$
  - If $\text{Circularity} > 0.70$, it snaps to a **perfect circle** (`cv2.minEnclosingCircle`).
  - If polygon approximation (`cv2.approxPolyDP`) yields 4 vertices, it snaps to a **clean rectangle**.
  - If 3 vertices, it snaps to a **clean triangle**.
  - If endpoints distance $\approx$ path length, it snaps to a **straight line**.

### C. Voice AI & NLP Command Engine (Day 4 NLP)
- Integrates the **Web Speech API** (`SpeechRecognition`):
  - Spoken commands (*"Color Cyan"*, *"Eraser"*, *"Brush thick"*, *"Clear canvas"*, *"Save art"*) are parsed using regex tokenization in `voice_nlp.py`.
  - The AI responds via **Text-to-Speech (TTS)**: *"Switched to Neon Cyan"* or *"Canvas cleared"*.

### D. SQLite Database & Art Gallery (Day 3 Database)
- File `aircanvas.db` persistently logs all drawing sessions with timestamps, strokes count, colors used, and file paths.
- View and download past artworks anytime in the **Gallery modal**.

---

## 📁 5. Project File Structure

```
AirCanvas/
├── START_AIRCANVAS.bat       # One-click Windows launcher
├── run.py                    # Server runner with automatic port handling & browser opening
├── app.py                    # FastAPI backend with REST endpoints
├── database.py               # SQLite storage (aircanvas.db)
├── shape_engine.py           # AI Geometric shape detection (Circle, Rect, Triangle, Line)
├── voice_nlp.py              # NLP speech command parsing & TTS feedback
├── gallery/                  # Saved PNG artwork files
└── static/
    ├── index.html            # Futuristic UI dashboard with virtual color header
    ├── style.css             # Glassmorphic dark theme with glowing neon pen trails
    └── canvas.js             # 60 FPS MediaPipe tracking, gesture state machine, dual canvas
```

---

## 🎯 6. Top Viva Questions & Answers for AirCanvas AI

#### Q1: What is the real-world application of AirCanvas AI?
> **Answer:** "AirCanvas AI provides a touchless interactive whiteboard. It serves two main human needs:
> 1. **Assistive Education:** Allows children with motor disabilities to draw and write in the air without holding physical tools.
> 2. **Sterile Medical Environments:** Enables doctors and surgeons to annotate medical charts or draw without touching contaminated surfaces."

#### Q2: How do you differentiate between 'Drawing' and 'Hovering'?
> **Answer:** "We use finger state geometry. When only the index finger is extended and the other three fingers are curled, the state machine enters `DRAWING` mode. When both index and middle fingers are extended (Peace sign), it enters `HOVER` mode, allowing the user to move the cursor or select colors without drawing lines."

#### Q3: How does the AI Shape Snapping algorithm work?
> **Answer:** "In `shape_engine.py`, we analyze the $(x, y)$ stroke coordinates using OpenCV. First, we check if the path is closed. Then we compute the contour area and perimeter to calculate circularity: $4\pi \frac{\text{Area}}{\text{Perimeter}^2}$. If it exceeds 0.70, it snaps to a circle. For polygons, we use Douglas-Peucker polygon approximation (`cv2.approxPolyDP`) to count vertices: 3 vertices snap to a triangle, and 4 vertices snap to a rectangle."

#### Q4: How do you prevent hand jitter and shaky lines?
> **Answer:** "We use quadratic Bézier curve midpoint interpolation in HTML5 Canvas. Instead of connecting raw discrete landmark points with sharp straight lines, we calculate the midpoint between the previous coordinate and the current coordinate:
> `mid = (lastPoint + currentPoint) / 2`
> and draw a smooth quadratic curve, producing fluid calligraphy-style strokes."

#### Q5: How do the virtual colors get selected in the air?
> **Answer:** "The top header's virtual palette elements have fixed bounding box coordinates $(x, y, w, h)$. When the user's index fingertip enters this area in `HOVER` mode and remains for 280 milliseconds, a collision detection trigger switches the active drawing color and plays an audio feedback chime."
