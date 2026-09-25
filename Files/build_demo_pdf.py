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

        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 810, "EchoSign AI — Live Stage Demo & Failsafe Sign Language Guide")
            self.drawRightString(559, 810, "Presentation Handout | NIELIT Delhi")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(36, 804, 559, 804)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(36, 35, 559, 35)
        
        self.drawString(36, 24, "EchoSign AI | Presentation Playbook | Gestures, Sentences & Stage Script")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(559, 24, page_str)
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#0f172a")     # Slate dark
    c_accent = colors.HexColor("#0284c7")      # Ocean cyan
    c_emerald = colors.HexColor("#059669")     # Emerald green
    c_rose = colors.HexColor("#e11d48")        # Rose red
    c_dark = colors.HexColor("#1e293b")        # Text dark
    c_muted = colors.HexColor("#475569")       # Text secondary
    c_bg_light = colors.HexColor("#f8fafc")    # Table alt row
    c_box_bg = colors.HexColor("#eff6ff")      # Callout bg
    c_box_border = colors.HexColor("#bfdbfe")  # Callout border

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=19,
        leading=23,
        textColor=c_primary,
        alignment=1,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_accent,
        alignment=1,
        spaceAfter=10
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=c_muted,
        alignment=1,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13.5,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=c_primary
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=1
    )

    story = []

    # Title & Header
    story.append(Paragraph("EchoSign AI — Live Stage Demo &amp; Sign Guide", title_style))
    story.append(Paragraph("Failsafe Hand Gestures, Sentence Reconstruction &amp; Presentation Playbook", subtitle_style))
    story.append(Paragraph("<b>Bootcamp on Artificial Intelligence by NIELIT Delhi</b> &nbsp;|&nbsp; Stage Ready Handout", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=8))

    # Section 1: Golden Rules
    story.append(Paragraph("1. The 3 Stage Golden Rules (Zero Failure Guarantee)", h1_style))
    rules_data = [
        [
            Paragraph("<b>1. Camera Distance</b>", table_cell_bold),
            Paragraph("Sit <b>2.5 to 3 feet</b> away from your webcam. Ensure your <b>Face and Chest</b> are both clearly framed on screen so body anchors (chest, lips) trigger accurately.", table_cell)
        ],
        [
            Paragraph("<b>2. Room Lighting</b>", table_cell_bold),
            Paragraph("Ensure ambient light falls on the front of your face and hands. Avoid strong backlight (e.g. sitting with a bright window behind you).", table_cell)
        ],
        [
            Paragraph("<b>3. Hold for 1–2 Seconds</b>", table_cell_bold),
            Paragraph("EchoSign uses a <code>deque(maxlen=7)</code> consensus filter to eliminate camera jitter. <b>Hold each gesture steady for 1.5 seconds</b> until the HUD locks and speaks!", table_cell)
        ]
    ]
    t_rules = Table(rules_data, colWidths=[130, 393])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_box_bg),
        ('BOX', (0,0), (-1,-1), 1, c_box_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_box_border),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_rules)
    story.append(Spacer(1, 8))

    # Section 2: Catalog of Gestures
    story.append(Paragraph("2. Complete Catalog of Failsafe Signs &amp; Spoken Sentences", h1_style))

    # TABLE 1: Healthcare & Emergency
    story.append(Paragraph("Category A: Healthcare &amp; Medical Urgency (Hospital / Pain / Doctor)", h2_style))
    med_headers = [Paragraph("<b>Gesture / Combo</b>", table_header), Paragraph("<b>Physical Hand Movement</b>", table_header), Paragraph("<b>AI Spoken Output Sentence</b>", table_header), Paragraph("<b>Emotion &amp; Urgency</b>", table_header)]
    med_rows = [
        med_headers,
        [
            Paragraph("<b>PAIN + DOCTOR</b><br/>(Emergency)", table_cell_bold),
            Paragraph("1. Point index finger to chest/stomach (<code>PAIN</code>).<br/>2. Tap 2 fingers on opposite wrist pulse (<code>DOCTOR</code>).", table_cell),
            Paragraph("<i>'I am experiencing pain and would like to see a medical professional.'</i>", table_cell),
            Paragraph("<b>Medical Attention</b><br/>Urgency: <b>0.50</b> (Moderate)", table_cell)
        ],
        [
            Paragraph("<b>PLEASE + DOCTOR</b><br/>(Care Request)", table_cell_bold),
            Paragraph("1. Flat open hand across chest (<code>PLEASE</code>).<br/>2. Tap opposite wrist or neck pulse (<code>DOCTOR</code>).", table_cell),
            Paragraph("<i>'Could you please assist me in seeing a doctor?'</i>", table_cell),
            Paragraph("<b>Care Requested</b><br/>Urgency: <b>0.40</b>", table_cell)
        ],
        [
            Paragraph("<b>DOCTOR</b><br/>(Single Sign)", table_cell_bold),
            Paragraph("Index &amp; Middle fingers tap opposite wrist pulse or neck pulse.", table_cell),
            Paragraph("<i>'Could you please connect me with a doctor or medical professional?'</i>", table_cell),
            Paragraph("<b>Medical Attention</b><br/>Urgency: <b>0.40</b>", table_cell)
        ],
        [
            Paragraph("<b>PAIN</b><br/>(Single Sign)", table_cell_bold),
            Paragraph("Index finger points directly towards chest/stomach area.", table_cell),
            Paragraph("<i>'I am experiencing some physical discomfort or pain.'</i>", table_cell),
            Paragraph("<b>Care Requested</b><br/>Urgency: <b>0.40</b>", table_cell)
        ]
    ]
    t_med = Table(med_rows, colWidths=[90, 160, 185, 88])
    t_med.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_med)
    story.append(Spacer(1, 6))

    # TABLE 2: Needs (Food & Water)
    story.append(Paragraph("Category B: Basic Needs (Food, Water, Hunger)", h2_style))
    need_headers = [Paragraph("<b>Gesture / Combo</b>", table_header), Paragraph("<b>Physical Hand Movement</b>", table_header), Paragraph("<b>AI Spoken Output Sentence</b>", table_header), Paragraph("<b>Emotion &amp; Urgency</b>", table_header)]
    need_rows = [
        need_headers,
        [
            Paragraph("<b>PLEASE + WATER</b><br/>(Drink Request)", table_cell_bold),
            Paragraph("1. Flat hand on chest (<code>PLEASE</code>).<br/>2. 'W' shape (3 fingers up) touches lips/chin (<code>WATER</code>).", table_cell),
            Paragraph("<i>'Could I please get some drinking water?'</i>", table_cell),
            Paragraph("<b>Polite Request</b><br/>Urgency: <b>0.20</b>", table_cell)
        ],
        [
            Paragraph("<b>PLEASE + FOOD</b><br/>(Meal Request)", table_cell_bold),
            Paragraph("1. Flat hand on chest (<code>PLEASE</code>).<br/>2. Pinch 5 fingertips together touching lips/mouth (<code>FOOD</code>).", table_cell),
            Paragraph("<i>'Could I please have some food?'</i>", table_cell),
            Paragraph("<b>Polite Request</b><br/>Urgency: <b>0.20</b>", table_cell)
        ],
        [
            Paragraph("<b>WATER + FOOD</b><br/>(Complete Need)", table_cell_bold),
            Paragraph("1. 'W' shape at lips (<code>WATER</code>).<br/>2. Pinch cluster touching lips (<code>FOOD</code>).", table_cell),
            Paragraph("<i>'Could I please get some drinking water and food?'</i>", table_cell),
            Paragraph("<b>Polite Request</b><br/>Urgency: <b>0.20</b>", table_cell)
        ],
        [
            Paragraph("<b>FOOD</b><br/>(Single Sign)", table_cell_bold),
            Paragraph("Pinch all 5 fingertips together and touch lips/mouth repeatedly.", table_cell),
            Paragraph("<i>'I am feeling hungry, could you please provide some food?'</i>", table_cell),
            Paragraph("<b>Request / Need</b><br/>Urgency: <b>0.20</b>", table_cell)
        ],
        [
            Paragraph("<b>WATER</b><br/>(Single Sign)", table_cell_bold),
            Paragraph("'W' shape (Index, Middle, Ring up) tapped near chin/lips.", table_cell),
            Paragraph("<i>'Could I please have a glass of drinking water?'</i>", table_cell),
            Paragraph("<b>Request / Need</b><br/>Urgency: <b>0.20</b>", table_cell)
        ]
    ]
    t_need = Table(need_rows, colWidths=[90, 160, 185, 88])
    t_need.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_need)

    # PAGE 2: Greetings, Agreements & Social
    story.append(PageBreak())
    story.append(Paragraph("Category C: Greetings &amp; Politeness (Respect &amp; Gratitude)", h2_style))
    greet_headers = [Paragraph("<b>Gesture / Combo</b>", table_header), Paragraph("<b>Physical Hand Movement</b>", table_header), Paragraph("<b>AI Spoken Output Sentence</b>", table_header), Paragraph("<b>Emotion &amp; Urgency</b>", table_header)]
    greet_rows = [
        greet_headers,
        [
            Paragraph("<b>NAMASTE</b><br/>(Dual Hand)", table_cell_bold),
            Paragraph("Bring both palms together at chest level with fingers pointing upward.", table_cell),
            Paragraph("<i>'Namaste! Welcome and heartfelt greetings to you.'</i>", table_cell),
            Paragraph("<b>Warm &amp; Grateful</b><br/>Confidence: <b>0.98</b>", table_cell)
        ],
        [
            Paragraph("<b>HELLO</b><br/>(Single Hand)", table_cell_bold),
            Paragraph("Open 5 fingers upright facing camera, wave near temple height.", table_cell),
            Paragraph("<i>'Hello! Wishing you a peaceful and pleasant day.'</i>", table_cell),
            Paragraph("<b>Conversational</b><br/>Confidence: <b>0.97</b>", table_cell)
        ],
        [
            Paragraph("<b>NAMASTE + PLEASE</b>", table_cell_bold),
            Paragraph("1. Both palms together (<code>NAMASTE</code>).<br/>2. Flat open palm on chest (<code>PLEASE</code>).", table_cell),
            Paragraph("<i>'Namaste! Could you please assist me for a moment?'</i>", table_cell),
            Paragraph("<b>Polite Greeting</b>", table_cell)
        ],
        [
            Paragraph("<b>NAMASTE + THANK YOU</b>", table_cell_bold),
            Paragraph("1. Both palms together (<code>NAMASTE</code>).<br/>2. Flat hand moving outward from lips (<code>THANK YOU</code>).", table_cell),
            Paragraph("<i>'Namaste! Thank you very much for your time and kind support.'</i>", table_cell),
            Paragraph("<b>Warm &amp; Grateful</b>", table_cell)
        ],
        [
            Paragraph("<b>THANK YOU</b><br/>(Single Sign)", table_cell_bold),
            Paragraph("Fingers of flat hand touch lips/chin and extend outward towards camera.", table_cell),
            Paragraph("<i>'Thank you so much! Truly appreciate your kind support.'</i>", table_cell),
            Paragraph("<b>Warm &amp; Grateful</b>", table_cell)
        ]
    ]
    t_greet = Table(greet_rows, colWidths=[90, 160, 185, 88])
    t_greet.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_greet)
    story.append(Spacer(1, 6))

    # TABLE 4: Confirmations & Social (OK, Peace, Love)
    story.append(Paragraph("Category D: Confirmation, Social &amp; Agreement (OK / Yes / Love / Peace)", h2_style))
    social_headers = [Paragraph("<b>Gesture / Combo</b>", table_header), Paragraph("<b>Physical Hand Movement</b>", table_header), Paragraph("<b>AI Spoken Output Sentence</b>", table_header), Paragraph("<b>Emotion &amp; Urgency</b>", table_header)]
    social_rows = [
        social_headers,
        [
            Paragraph("<b>OK / GOOD</b><br/>(👌 Sign)", table_cell_bold),
            Paragraph("Thumb and Index finger tips touch forming a circle; Middle, Ring, Pinky upright.", table_cell),
            Paragraph("<i>'All is well, everything is completely okay.'</i>", table_cell),
            Paragraph("<b>Positive</b><br/>Confidence: <b>0.96</b>", table_cell)
        ],
        [
            Paragraph("<b>YES</b><br/>(Thumbs Up 👍)", table_cell_bold),
            Paragraph("Closed fist with thumb upright pointing to the ceiling.", table_cell),
            Paragraph("<i>'Yes, absolutely correct.'</i>", table_cell),
            Paragraph("<b>Agreement</b><br/>Confidence: <b>0.95</b>", table_cell)
        ],
        [
            Paragraph("<b>YES + THANK YOU</b>", table_cell_bold),
            Paragraph("1. Thumbs Up (<code>YES</code>).<br/>2. Flat hand extending from lips (<code>THANK YOU</code>).", table_cell),
            Paragraph("<i>'Yes, that is correct! Thank you so much.'</i>", table_cell),
            Paragraph("<b>Warm &amp; Grateful</b>", table_cell)
        ],
        [
            Paragraph("<b>NO + THANK YOU</b>", table_cell_bold),
            Paragraph("1. Index &amp; Middle finger snap down (<code>NO</code>).<br/>2. Flat hand lips outward (<code>THANK YOU</code>).", table_cell),
            Paragraph("<i>'No, thank you, but I appreciate your offer.'</i>", table_cell),
            Paragraph("<b>Polite Refusal</b>", table_cell)
        ],
        [
            Paragraph("<b>I LOVE YOU</b><br/>(🤟 Sign)", table_cell_bold),
            Paragraph("Thumb, Index, and Pinky fingers open simultaneously (Middle &amp; Ring curled).", table_cell),
            Paragraph("<i>'I love and appreciate you deeply!'</i>", table_cell),
            Paragraph("<b>Social / Affection</b><br/>Confidence: <b>0.96</b>", table_cell)
        ],
        [
            Paragraph("<b>PEACE</b><br/>(✌️ V-Sign)", table_cell_bold),
            Paragraph("Index and Middle finger spread wide in 'V' shape (Ring, Pinky, Thumb tucked).", table_cell),
            Paragraph("<i>'Peace, calmness, and goodwill to all!'</i>", table_cell),
            Paragraph("<b>Calmness</b><br/>Confidence: <b>0.96</b>", table_cell)
        ]
    ]
    t_social = Table(social_rows, colWidths=[90, 160, 185, 88])
    t_social.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_social)

    # TABLE 5: ASL Fingerspelling & Dynamic Words
    story.append(Paragraph("Category E: ASL Fingerspelling &amp; Dynamic Word/Name Pronunciation", h2_style))
    story.append(Paragraph("When in <b>ASL Alphabet Mode (RTX 4060 GPU)</b>, fingerspelling individual letters triggers real-time GPU inference + geometric verification, automatically assembled into spoken words or custom names by our NLP Engine:", body_style))

    alpha_headers = [Paragraph("<b>Letter</b>", table_header), Paragraph("<b>ASL Hand Pose Description</b>", table_header), Paragraph("<b>Key Finger Landmark Configuration</b>", table_header)]
    alpha_rows = [
        alpha_headers,
        [
            Paragraph("<b>A</b>", table_cell_bold),
            Paragraph("Make a closed fist with knuckles facing front; thumb stands upright beside the index finger.", table_cell),
            Paragraph("All 4 fingers curled (<code>ext=False</code>), Thumb upright beside index (<code>pts[4].y &lt; pts[3].y</code>).", table_cell)
        ],
        [
            Paragraph("<b>Y</b>", table_cell_bold),
            Paragraph("The classic 'Hang Loose' / 'Shaka' sign. Thumb &amp; Pinky extended outward; middle 3 fingers curled.", table_cell),
            Paragraph("Pinky &amp; Thumb extended outward (<code>ext_pinky &amp; ext_thumb</code>), Index, Middle, Ring curled.", table_cell)
        ],
        [
            Paragraph("<b>U</b>", table_cell_bold),
            Paragraph("Index and Middle fingers pointing straight UP and touching together (glued together); Ring &amp; Pinky tucked.", table_cell),
            Paragraph("Index &amp; Middle extended upright with tip distance <code>d &lt; 0.20</code>; Ring &amp; Pinky curled.", table_cell)
        ],
        [
            Paragraph("<b>S</b>", table_cell_bold),
            Paragraph("Tight closed fist with thumb folded horizontally across the front of the curled fingers (like a punch).", table_cell),
            Paragraph("All 4 fingers curled into fist, Thumb folded across the front of the fingers.", table_cell)
        ],
        [
            Paragraph("<b>H</b>", table_cell_bold),
            Paragraph("Index and Middle fingers extended horizontally to the side (pointing sideways); Ring &amp; Pinky curled.", table_cell),
            Paragraph("Index &amp; Middle pointing sideways (<code>dx &gt; dy</code>); Ring &amp; Pinky curled.", table_cell)
        ],
        [
            Paragraph("<b>B</b>", table_cell_bold),
            Paragraph("All 4 fingers (Index, Middle, Ring, Pinky) upright together; thumb folded across the palm.", table_cell),
            Paragraph("All 4 fingers extended upright together; Thumb tucked across the palm.", table_cell)
        ],
        [
            Paragraph("<b>I</b>", table_cell_bold),
            Paragraph("Only Pinky finger pointing straight UP; all other 4 fingers curled into a fist.", table_cell),
            Paragraph("Pinky extended straight UP; Index, Middle, Ring, Thumb curled into fist.", table_cell)
        ]
    ]
    t_alpha = Table(alpha_rows, colWidths=[40, 260, 223])
    t_alpha.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_alpha)
    story.append(Spacer(1, 6))

    # Synthesis Outcome Box
    fingerspell_box = [
        [
            Paragraph("<b>Dynamic NLP Fingerspelling Assembly</b>: Individual letters are continuously streamed and assembled into complete words or custom names.<br/>"
                      "🔊 <b>Text-to-Speech Output</b>: The voice smoothly pronounces the assembled word/name as complete, natural speech (e.g., custom names, technical terms, or unlisted vocabulary).<br/>"
                      "<b>Control Tokens Supported</b>: <code>SPACE</code> (open flat hand to separate words) &bull; <code>DEL</code> (backspace to remove last letter).", table_cell)
        ]
    ]
    t_fingerspell_box = Table(fingerspell_box, colWidths=[523])
    t_fingerspell_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#10b981")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_fingerspell_box)
    story.append(Spacer(1, 10))

    # PAGE 3: Reverse Channel & Stage Playbook
    story.append(PageBreak())
    story.append(Paragraph("3. Reverse Channel (Voice &rarr; Sign) Demonstration Phrases", h1_style))
    story.append(Paragraph(
        "To showcase Channel B (Hearing to Deaf), switch to the <b>'Voice &rarr; Sign'</b> tab, click the microphone, and speak any of these realistic phrases. The NLP tokenizer isolates keywords and pops up animated visual Sign Cards:",
        body_style
    ))

    voice_phrases = [
        ("Hospital Urgency", "<b>'Please call a doctor, I have pain.'</b>", "Triggers 3 Sign Cards: <b>PLEASE</b> (Heart), <b>DOCTOR</b> (Cross), <b>PAIN</b> (Activity)"),
        ("Meal / Hospitality", "<b>'Are you hungry? Do you need food and water?'</b>", "Triggers 2 Sign Cards: <b>FOOD</b> (Utensils), <b>WATER</b> (Droplet)"),
        ("Social Respect", "<b>'Namaste, thank you for coming today.'</b>", "Triggers 2 Sign Cards: <b>NAMASTE</b> (Pranam), <b>THANK YOU</b> (Handshake)"),
        ("Polite Check", "<b>'Hello, is everything okay with you?'</b>", "Triggers 2 Sign Cards: <b>HELLO</b> (Wave), <b>OK</b> (Checkmark)")
    ]
    v_rows = [[Paragraph("<b>Scenario</b>", table_header), Paragraph("<b>Spoken English Line (Speak into Mic)</b>", table_header), Paragraph("<b>Visual Sign Cards Displayed</b>", table_header)]]
    for scn, spk, crd in voice_phrases:
        v_rows.append([Paragraph(scn, table_cell_bold), Paragraph(spk, table_cell), Paragraph(crd, table_cell)])

    t_voice = Table(v_rows, colWidths=[100, 210, 213])
    t_voice.setStyle(TableStyle([
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
    story.append(t_voice)
    story.append(Spacer(1, 10))

    # Section 4: Stage Playbook
    story.append(Paragraph("4. Minute-by-Minute Stage Presentation Script", h1_style))
    story.append(Paragraph(
        "Follow this exact script when presenting before evaluators to deliver a captivating 4-minute presentation:",
        body_style
    ))

    script_points = [
        ("00:00 - 00:45", "Introduction & Problem Statement",
         "<i>'Good morning respected evaluators. Over 466 million people face disabling hearing and speech impairments. Most academic sign projects only recognize static alphabet letters one-way. Today, we present EchoSign AI—a real-time, two-way assistive communication bridge powered by Computer Vision, NLP, and NVIDIA RTX 4060 GPU Deep Learning.'</i>"),
        
        ("00:45 - 01:45", "Channel A: Dual-Hand Namaste & Daily Needs Demo",
         "<i>'First, I demonstrate Channel A: Deaf to Hearing. I bring both hands together in front of the chest. Notice the dual-hand tracking highlighting primary hand in Neon Cyan and secondary in Emerald, speaking Namaste! Next, I place a flat hand on my chest for PLEASE, followed by W-shape at my lips for WATER. Our NLP engine seamlessly reconstructs: 'Could I please get some drinking water?' with polite request sentiment.'</i>"),

        ("01:45 - 02:45", "Medical Triage Intent & Social Confirmation",
         "<i>'In emergency medical scenarios, pointing to pain and tapping my wrist pulse reconstructs: 'I am experiencing pain and would like to see a medical professional' and tags a moderate urgency score. For confirmations, making the OK circle sign or I Love You gesture is classified with over 96% confidence.'</i>"),

        ("02:45 - 03:30", "Channel B: Voice to Sign & RTX 4060 GPU Showcase",
         "<i>'Now, I demonstrate our reverse channel for hearing individuals. I speak into the mic: 'Please call a doctor, I have pain.' Instantly, animated visual Sign Cards appear for the deaf person. Finally, in ASL Alphabet Mode, our custom ASLResNet neural network classifies fingerspelled letters L and V directly on the RTX 4060 GPU in under 2 milliseconds with 99.87% accuracy.'</i>"),

        ("03:30 - 04:00", "Conclusion & Q&A Invitation",
         "<i>'All conversation logs are stored in our SQLite database for health analytics. EchoSign AI bridges human communication through accessible edge AI. Thank you, we are now ready for your questions.'</i>")
    ]

    s_rows = [[Paragraph("<b>Time</b>", table_header), Paragraph("<b>Section Phase</b>", table_header), Paragraph("<b>Spoken Stage Lines &amp; Live Actions</b>", table_header)]]
    for tm, ph, sc in script_points:
        s_rows.append([Paragraph(tm, table_cell_bold), Paragraph(ph, table_cell_bold), Paragraph(sc, table_cell)])

    t_script = Table(s_rows, colWidths=[65, 140, 318])
    t_script.setStyle(TableStyle([
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
    story.append(t_script)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {filename}")

if __name__ == "__main__":
    out_pdf = "EchoSign_Live_Demo_and_Sign_Language_Guide.pdf"
    build_pdf(out_pdf)
