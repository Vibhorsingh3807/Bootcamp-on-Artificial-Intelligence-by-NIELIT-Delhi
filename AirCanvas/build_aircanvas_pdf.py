import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        if self._pageNumber > 1:
            self.drawString(36, 810, "AirCanvas AI — Touchless Gesture Whiteboard & Smart Canvas")
            self.drawRightString(559, 810, "Bootcamp on AI by NIELIT Delhi")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(36, 804, 559, 804)

        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(36, 35, 559, 35)
        
        self.drawString(36, 24, "AirCanvas AI | Touchless Whiteboard | MediaPipe + OpenCV + Voice AI + SQLite")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 24, page_str)
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=45, bottomMargin=45)
    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#0f172a")
    c_accent = colors.HexColor("#0284c7")
    c_dark = colors.HexColor("#1e293b")
    c_muted = colors.HexColor("#475569")
    c_bg_light = colors.HexColor("#f8fafc")
    c_box_bg = colors.HexColor("#f0fdf4")
    c_box_border = colors.HexColor("#bbf7d0")

    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=c_primary, alignment=1, spaceAfter=4)
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=c_accent, alignment=1, spaceAfter=12)
    meta_style = ParagraphStyle('DocMeta', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=c_muted, alignment=1, spaceAfter=15)
    h1_style = ParagraphStyle('Heading1_Custom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=c_primary, spaceBefore=12, spaceAfter=6, keepWithNext=True)
    h2_style = ParagraphStyle('Heading2_Custom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=c_accent, spaceBefore=8, spaceAfter=4, keepWithNext=True)
    body_style = ParagraphStyle('Body_Custom', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12, textColor=c_dark, spaceAfter=5)
    bullet_style = ParagraphStyle('Bullet_Custom', parent=body_style, leftIndent=12, firstLineIndent=-8, spaceAfter=3)
    table_cell = ParagraphStyle('TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10, textColor=c_dark)
    table_cell_bold = ParagraphStyle('TableCellBold', parent=table_cell, fontName='Helvetica-Bold', textColor=c_primary)
    table_header = ParagraphStyle('TableHeader', parent=table_cell, fontName='Helvetica-Bold', textColor=colors.white, alignment=1)
    q_style = ParagraphStyle('QuestionStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12.5, textColor=colors.HexColor("#0369a1"), spaceBefore=6, spaceAfter=2, keepWithNext=True)
    a_style = ParagraphStyle('AnswerStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8.2, leading=11.5, textColor=c_dark, leftIndent=10, spaceAfter=6)

    story = []

    # Title
    story.append(Paragraph("AirCanvas AI — Touchless Whiteboard &amp; Smart Canvas", title_style))
    story.append(Paragraph("Human-Centric Assistive Drawing | Computer Vision, AI Shape Snapping &amp; Voice AI", subtitle_style))
    story.append(Paragraph("<b>Bootcamp on Artificial Intelligence by NIELIT Delhi</b> &nbsp;|&nbsp; Capstone Project 2 Notes", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=10))

    # Section 1: Overview
    story.append(Paragraph("1. Executive Summary &amp; Human Mission", h1_style))
    story.append(Paragraph(
        "<b>AirCanvas AI</b> is a touchless, vision-based interactive whiteboard designed for assistive education and sterile clinical environments. It allows users to write, sketch, and control canvas tools entirely through natural hand gestures captured by a standard webcam:",
        body_style
    ))

    overview_data = [
        [
            Paragraph("<b>Assistive Education</b>", table_cell_bold),
            Paragraph("Enables children and students with fine-motor disabilities or arthritis to draw and write effortlessly in the air without clutching heavy physical instruments.", table_cell)
        ],
        [
            Paragraph("<b>Sterile Medical Annotations</b>", table_cell_bold),
            Paragraph("Allows surgeons and clinicians to annotate medical charts and X-rays touch-free without breaking sterile protocol by touching screens or mice.", table_cell)
        ],
        [
            Paragraph("<b>AI Geometric Shape Snapping</b>", table_cell_bold),
            Paragraph("Analyzes rough hand-drawn strokes using OpenCV contour circularity and Douglas-Peucker polygon approximation to instantly snap rough sketches into perfect circles, rectangles, triangles, and straight lines.", table_cell)
        ],
        [
            Paragraph("<b>Multimodal Voice Control &amp; NLP</b>", table_cell_bold),
            Paragraph("Supports spoken English commands (e.g. <i>'Color Cyan'</i>, <i>'Eraser'</i>, <i>'Clear board'</i>, <i>'Save art'</i>) with spoken Text-to-Speech audio confirmations.", table_cell)
        ]
    ]
    t_overview = Table(overview_data, colWidths=[150, 373])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_box_bg),
        ('BOX', (0,0), (-1,-1), 1, c_box_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_box_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 10))

    # Section 2: Gestures
    story.append(Paragraph("2. Gesture State Machine (100% Reliable &amp; Deterministic)", h1_style))
    story.append(Paragraph("The system uses an intuitive 5-state geometric finite state machine calculated from 21 MediaPipe hand landmarks:", body_style))

    gesture_headers = [Paragraph("<b>Gesture</b>", table_header), Paragraph("<b>Visual Cue</b>", table_header), Paragraph("<b>Active Mode</b>", table_header), Paragraph("<b>Geometric Logic &amp; Action</b>", table_header)]
    gesture_rows = [
        gesture_headers,
        [
            Paragraph("<b>Index Finger Up</b>", table_cell_bold),
            Paragraph("☝️", table_header),
            Paragraph("<b>DRAWING</b>", table_cell_bold),
            Paragraph("Index tip (Landmark 8) is elevated (<code>y_tip &lt; y_pip</code>); Middle, Ring, Pinky are curled. Draws smooth neon strokes.", table_cell)
        ],
        [
            Paragraph("<b>Peace Sign (V)</b>", table_cell_bold),
            Paragraph("✌️", table_header),
            Paragraph("<b>HOVER &amp; SELECT</b>", table_cell_bold),
            Paragraph("Index and Middle fingers are both up; Ring and Pinky curled. Drawing pauses. Cursor hovers over top color bar to select colors in the air.", table_cell)
        ],
        [
            Paragraph("<b>Open Palm</b>", table_cell_bold),
            Paragraph("✋", table_header),
            Paragraph("<b>ERASER</b>", table_cell_bold),
            Paragraph("All 5 fingers extended. Palm center acts as a circular eraser wiping the board.", table_cell)
        ],
        [
            Paragraph("<b>Closed Fist</b>", table_cell_bold),
            Paragraph("✊", table_header),
            Paragraph("<b>HOLD TO CLEAR</b>", table_cell_bold),
            Paragraph("All fingers curled into a fist. Holding for 1.4 seconds fills a visual progress circle and completely cleans the canvas.", table_cell)
        ],
        [
            Paragraph("<b>Thumbs Up</b>", table_cell_bold),
            Paragraph("👍", table_header),
            Paragraph("<b>SAVE SNAPSHOT</b>", table_cell_bold),
            Paragraph("Thumb upright, other 4 fingers curled. Holding for 1.2s saves artwork to SQLite Gallery and triggers PNG download with a chime sound.", table_cell)
        ]
    ]
    t_gestures = Table(gesture_rows, colWidths=[95, 40, 95, 293])
    t_gestures.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_gestures)
    story.append(Spacer(1, 10))

    # Section 3: AI & Mathematics
    story.append(PageBreak())
    story.append(Paragraph("3. Technical Implementation &amp; Mathematics", h1_style))
    
    story.append(Paragraph("A. AI Geometric Shape Snapping (OpenCV Contour Analysis)", h2_style))
    story.append(Paragraph(
        "In <code>shape_engine.py</code>, user stroke points are analyzed mathematically:<br/>"
        "• <b>Closure Check:</b> If the distance between start and end points is &lt; 25% of total path length, the stroke is considered closed.<br/>"
        "• <b>Circularity Metric:</b> <code>Circularity = (4 * pi * Area) / (Perimeter^2)</code>. If Circularity &gt; 0.68, the shape is snapped to a perfect circle via <code>cv2.minEnclosingCircle</code>.<br/>"
        "• <b>Polygon Vertex Fitting:</b> Douglas-Peucker approximation (<code>cv2.approxPolyDP</code>): 3 vertices snap to a triangle; 4 vertices snap to a rectangle.<br/>"
        "• <b>Line Fitting:</b> If endpoint distance is &gt; 90% of total path length, it snaps to a straight vector line.",
        body_style
    ))

    story.append(Paragraph("B. Sub-Pixel Quadratic Bézier Curve Smoothing", h2_style))
    story.append(Paragraph(
        "Hand tracking at 60 FPS can suffer from micro-tremors. Instead of connecting discrete points with jagged line segments, AirCanvas calculates the midpoint between successive coordinates: <code>mid = (p_{i-1} + p_i) / 2</code> and draws a smooth quadratic Bézier curve (<code>ctx.quadraticCurveTo</code>), producing fluid calligraphy strokes.",
        body_style
    ))

    # Section 4: Viva Q&A
    story.append(Paragraph("4. Top Viva Questions &amp; Answers for AirCanvas AI", h1_style))
    air_qa = [
        (
            "Q1. How does AirCanvas AI track the hand without physical markers or gloves?",
            "AirCanvas utilizes MediaPipe Hands, a deep learning pipeline running client-side at 60 FPS. It detects the palm bounding box and regresses 21 3D hand landmarks in real time directly from the raw RGB webcam feed, eliminating the need for colored markers, gloves, or specialized sensors."
        ),
        (
            "Q2. How do you distinguish between drawing a line and moving the cursor?",
            "We inspect the vertical state of individual fingers. When only the index finger is extended and the middle finger is curled down, the state machine enters DRAWING mode. When both index and middle fingers are extended (Peace sign), it switches to HOVER mode, allowing cursor repositioning and color selection without leaving a mark."
        ),
        (
            "Q3. How does the touchless Virtual Color Palette work in the air?",
            "The top header contains virtual color regions with known bounding coordinates (x, y, w, h). When the user is in HOVER mode and places their index fingertip inside a color tile's area for over 280 milliseconds, a spatial collision event triggers, instantly changing the active brush color and playing an audio chime."
        ),
        (
            "Q4. How does the AI Shape Snapping algorithm work?",
            "Once a stroke finishes, coordinates are evaluated in shape_engine.py. If the contour is closed, we compute the compactness ratio: 4*pi*Area / (Perimeter^2). A ratio near 1.0 indicates a circle. For polygons, cv2.approxPolyDP simplifies the contour into vertices: 3 vertices indicate a triangle, and 4 vertices indicate a rectangle."
        ),
        (
            "Q5. How does the voice command engine work?",
            "The browser's Web Speech API transcribes speech into text. In voice_nlp.py, regex tokenization and keyword mapping extract intended actions (e.g. 'Color Cyan', 'Brush Large', 'Clear canvas'). The server returns a structured JSON command and confirms action execution via Text-to-Speech (TTS)."
        ),
        (
            "Q6. How is user artwork persisted?",
            "When the user clicks Save or triggers the Thumbs Up gesture, the HTML5 canvas is merged onto a dark background and converted to base64 PNG. The FastAPI endpoint saves the file to the gallery/ folder and logs the metadata (timestamp, strokes count, colors used) into an SQLite database (aircanvas.db)."
        )
    ]
    for q, a in air_qa:
        story.append(Paragraph(q, q_style))
        story.append(Paragraph(a, a_style))

    # Section 5: Cheat Sheet
    story.append(Spacer(1, 8))
    story.append(Paragraph("5. AirCanvas AI Cheat Sheet &amp; Demo Steps", h1_style))
    cheat_data = [
        [
            Paragraph("<b>Vision Engine</b>: MediaPipe Hands (21 3D joints @ 60 FPS)<br/><b>Shape Snapping</b>: OpenCV Contour &amp; Polygon approx<br/><b>Voice Control</b>: Web Speech API + Regex NLP Parser", table_cell),
            Paragraph("<b>Backend Server</b>: FastAPI + Uvicorn (ASGI)<br/><b>Database</b>: SQLite (aircanvas.db)<br/><b>Audio Feedback</b>: Synthesized Web Audio API", table_cell)
        ]
    ]
    t_cheat = Table(cheat_data, colWidths=[260, 263])
    t_cheat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#0284c7")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_cheat)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {filename}")

if __name__ == "__main__":
    out_pdf = "AirCanvas_AI_Viva_and_Project_Notes.pdf"
    build_pdf(out_pdf)
