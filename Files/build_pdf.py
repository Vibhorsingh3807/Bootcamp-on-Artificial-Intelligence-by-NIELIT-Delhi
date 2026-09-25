import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
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
            self.drawString(36, 810, "EchoSign AI — Complete Viva & Project Examination Guide")
            self.drawRightString(559, 810, "Bootcamp on AI by NIELIT Delhi")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(36, 804, 559, 804)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(36, 35, 559, 35)
        
        self.drawString(36, 24, "EchoSign AI | Assistive Communication Bridge | PyTorch + FastAPI + MediaPipe")
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

    # Custom styles
    c_primary = colors.HexColor("#0f172a")    # Dark slate navy
    c_accent = colors.HexColor("#0284c7")     # Ocean cyan blue
    c_emerald = colors.HexColor("#059669")    # Forest emerald
    c_dark = colors.HexColor("#1e293b")       # Text dark
    c_muted = colors.HexColor("#475569")      # Text secondary
    c_bg_light = colors.HexColor("#f8fafc")   # Table alternate row
    c_box_bg = colors.HexColor("#f0f9ff")     # Light blue box
    c_box_border = colors.HexColor("#bae6fd") # Border light blue

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        alignment=1, # Center
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
        spaceAfter=12
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=c_muted,
        alignment=1,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=4,
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

    body_bold = ParagraphStyle(
        'Body_Bold_Custom',
        parent=body_style,
        fontName='Helvetica-Bold'
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
        leading=10,
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

    q_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#0369a1"),
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )

    a_style = ParagraphStyle(
        'AnswerStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.5,
        textColor=c_dark,
        leftIndent=10,
        spaceAfter=6
    )

    story = []

    # =========================================================================
    # COVER / HEADER BANNER
    # =========================================================================
    story.append(Paragraph("EchoSign AI — Viva &amp; Project Examination Guide", title_style))
    story.append(Paragraph("Real-Time Assistive Communication Bridge | Computer Vision &amp; Deep Learning", subtitle_style))
    story.append(Paragraph("<b>Bootcamp on Artificial Intelligence by NIELIT Delhi</b> &nbsp;|&nbsp; Capstone Project Comprehensive Notes", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=10))

    # =========================================================================
    # SECTION 1: PROJECT OVERVIEW
    # =========================================================================
    story.append(Paragraph("1. Executive Summary &amp; Problem Statement", h1_style))
    story.append(Paragraph(
        "Over <b>466 million people worldwide</b> suffer from disabling hearing loss or speech impairment. In daily settings—such as hospitals, ticket counters, and educational institutions—communicating with hearing individuals is a severe barrier. Conventional sign language software only supports one-way static finger spelling (A–Z). <b>EchoSign AI</b> solves this as a comprehensive, two-way, real-time communication hub:",
        body_style
    ))

    # Key highlights table
    overview_data = [
        [
            Paragraph("<b>Channel A (Deaf &rarr; Hearing)</b>", table_cell_bold),
            Paragraph("Translates webcam sign gestures &amp; ASL finger spelling into natural spoken English voice using <b>Text-to-Speech (TTS)</b> and visual sentiment indicators.", table_cell)
        ],
        [
            Paragraph("<b>Channel B (Hearing &rarr; Deaf)</b>", table_cell_bold),
            Paragraph("Transcribes spoken English voice in real time into animated <b>Sign Language Visual Cards</b> with clear instructions so the deaf person can easily understand.", table_cell)
        ],
        [
            Paragraph("<b>Dual Vision Engine</b>", table_cell_bold),
            Paragraph("Combines <b>MediaPipe 21-landmark geometric classification</b> (13 conversational signs like <i>Namaste, Please, Water, Doctor, Pain</i>) with an <b>NVIDIA RTX 4060 GPU-accelerated ASLResNet Deep CNN</b> (99.87% accuracy on 87,000 images, &lt;2ms latency).", table_cell)
        ],
        [
            Paragraph("<b>NLP Sentence Smoother</b>", table_cell_bold),
            Paragraph("Reconstructs isolated sign tokens (e.g. <i>PLEASE + WATER</i>) into grammatically polished, polite English sentences (<i>'Could I please get some drinking water?'</i>) with emotional tone tags.", table_cell)
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

    # =========================================================================
    # SECTION 2: LIBRARIES USED & WHY
    # =========================================================================
    story.append(Paragraph("2. Complete List of Libraries Used &amp; Viva Justifications", h1_style))
    story.append(Paragraph(
        "Examiners frequently ask <i>'Why did you pick this specific library?'</i> and <i>'What are the alternatives?'</i>. Below is the detailed inventory for Python backend and frontend technologies:",
        body_style
    ))

    lib_headers = [Paragraph("<b>Library / API</b>", table_header), Paragraph("<b>Role in Project</b>", table_header), Paragraph("<b>Why Chosen Over Alternatives (Viva Reason)</b>", table_header)]
    lib_rows = [
        lib_headers,
        [
            Paragraph("<b>torch (PyTorch 2.6.0 + CUDA)</b>", table_cell_bold),
            Paragraph("Deep learning framework for defining, training, and running inference on <code>ASLResNet</code>.", table_cell),
            Paragraph("Dynamic computation graphs, fine-grained GPU memory management, and native FP16 Automatic Mixed Precision (AMP) on RTX 4060 Tensor Cores.", table_cell)
        ],
        [
            Paragraph("<b>torchvision</b>", table_cell_bold),
            Paragraph("Image datasets and transforms pipeline (Resize, Normalize, ToTensor).", table_cell),
            Paragraph("C++ optimized computer vision backend tightly coupled with PyTorch tensors without conversion overhead.", table_cell)
        ],
        [
            Paragraph("<b>FastAPI</b>", table_cell_bold),
            Paragraph("Asynchronous backend web server hosting REST endpoints (/predict_frame, /refine_sentence).", table_cell),
            Paragraph("<b>Why not Flask?</b> FastAPI is ASGI-based (3x faster than Flask), handles concurrent frame requests asynchronously, and has built-in Pydantic data validation.", table_cell)
        ],
        [
            Paragraph("<b>Uvicorn</b>", table_cell_bold),
            Paragraph("Lightning-fast ASGI server implementation.", table_cell),
            Paragraph("Production-ready asynchronous server with non-blocking I/O event loops for real-time video inference.", table_cell)
        ],
        [
            Paragraph("<b>Pydantic</b>", table_cell_bold),
            Paragraph("Request/response schema definition and landmark array data validation.", table_cell),
            Paragraph("Enforces strict typed contracts on 21 3D coordinate inputs, discarding corrupted or malformed payloads before inference.", table_cell)
        ],
        [
            Paragraph("<b>NumPy</b>", table_cell_bold),
            Paragraph("21 3D landmark array operations, origin shifting, Euclidean norm distance calculations.", table_cell),
            Paragraph("High-performance C-vectorized math operations (<code>np.linalg.norm</code>) executed in sub-millisecond execution time.", table_cell)
        ],
        [
            Paragraph("<b>scikit-learn</b>", table_cell_bold),
            Paragraph("<code>KNeighborsClassifier</code> for conversational word gestures and evaluation metrics.", table_cell),
            Paragraph("Lightweight, instantaneous training, zero GPU VRAM consumption for 13 geometric gestures, highly interpretable.", table_cell)
        ],
        [
            Paragraph("<b>OpenCV (cv2)</b>", table_cell_bold),
            Paragraph("Image decoding from base64, color conversions (BGR to RGB), frame flipping &amp; resizing.", table_cell),
            Paragraph("Industry standard computer vision library for manipulating raw pixel buffers with optimized memory layout.", table_cell)
        ],
        [
            Paragraph("<b>SQLite (sqlite3)</b>", table_cell_bold),
            Paragraph("Persistent storage of conversation interactions, sentiment labels, urgency scores in <code>echosign.db</code>.", table_cell),
            Paragraph("<b>Why not MongoDB/MySQL?</b> Serverless, zero-config, embedded ACID-compliant database requiring no background daemon.", table_cell)
        ],
        [
            Paragraph("<b>re (Regular Expressions)</b>", table_cell_bold),
            Paragraph("Speech recognition transcript tokenization and keyword isolation in <code>nlp_engine.py</code>.", table_cell),
            Paragraph("Deterministic, rapid string parsing without heavy neural NLP library overhead for word-to-sign card mapping.", table_cell)
        ],
        [
            Paragraph("<b>MediaPipe Hands &amp; Pose</b>", table_cell_bold),
            Paragraph("Client-side tracking of 21 3D hand joints and upper-body anchor points (lips, chest, head) at 60 FPS.", table_cell),
            Paragraph("<b>Why not full-frame 3D CNN?</b> Offloads heavy joint detection to client browser WebAssembly/WebGL, achieving invariance to background, lighting, and skin tones.", table_cell)
        ],
        [
            Paragraph("<b>Web Speech API</b>", table_cell_bold),
            Paragraph("Native browser Text-to-Speech (TTS) and Speech-to-Text (STT) for two-way audio bridge.", table_cell),
            Paragraph("Requires zero paid cloud API keys, zero network latency, functions offline with zero operating costs.", table_cell)
        ]
    ]

    t_libs = Table(lib_rows, colWidths=[105, 185, 233])
    t_libs.setStyle(TableStyle([
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
    story.append(t_libs)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: MAPPING OF 4-DAY NIELIT CURRICULUM INTO ECHOSIGN
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Mapping 4-Day NIELIT Bootcamp Curriculum to EchoSign", h1_style))
    story.append(Paragraph(
        "Here is the explicit proof of how every subject taught across Day 1, Day 2, Day 3, and Day 4 of the NIELIT Delhi Bootcamp was directly engineered into the EchoSign architecture:",
        body_style
    ))

    bootcamp_headers = [Paragraph("<b>Bootcamp Day</b>", table_header), Paragraph("<b>Key Curriculum Concepts Taught</b>", table_header), Paragraph("<b>Direct Implementation in EchoSign Project</b>", table_header)]
    bootcamp_rows = [
        bootcamp_headers,
        [
            Paragraph("<b>DAY 1:<br/>Python Basics &amp; Logic Flow</b>", table_cell_bold),
            Paragraph("• Variables, data types, arithmetic<br/>• Lists, slicing, indexing (0 and -1)<br/>• Loops (<code>for</code>, <code>while</code>) and conditionals<br/>• Custom functions and string operations", table_cell),
            Paragraph("• <b>Consensus Queue:</b> <code>collections.deque(maxlen=7)</code> rolling window in <code>sign_engine.py</code> to filter out frame jitter.<br/>• <b>Dictionary Metadata:</b> <code>SIGN_DICTIONARY</code> storing keywords, categories, and vector icons.<br/>• <b>Modular Python Functions:</b> Structured backend in <code>app.py</code>, <code>sign_engine.py</code>, and <code>nlp_engine.py</code>.", table_cell)
        ],
        [
            Paragraph("<b>DAY 2:<br/>NumPy, Pandas, Math &amp; Regex</b>", table_cell_bold),
            Paragraph("• 2D/3D NumPy arrays &amp; axis aggregations<br/>• Vector math &amp; Euclidean norms (<code>np.linalg.norm</code>)<br/>• Missing data, cleaning, regex string matching<br/>• Pandas DataFrames, summary statistics &amp; GroupBy", table_cell),
            Paragraph("• <b>Coordinate Normalization:</b> 21 3D landmarks converted to <code>(21, 3)</code> array. Hand origin translated to wrist (Landmark 0) and divided by palm Euclidean norm: <code>pts / np.linalg.norm(pts[9])</code>.<br/>• <b>Regex Tokenization:</b> <code>re.findall(r'\\b[A-Za-z\']+\\b')</code> in <code>nlp_engine.py</code> for parsing voice input.<br/>• <b>Database Aggregations:</b> Summary counts and sentiment breakdowns in <code>database.py</code>.", table_cell)
        ],
        [
            Paragraph("<b>DAY 3:<br/>Machine Learning &amp; Deep Learning</b>", table_cell_bold),
            Paragraph("• Supervised classification &amp; evaluation (Accuracy, Confusion Matrix, Classification Report)<br/>• Decision Trees, KNN, Train-Test Split<br/>• Neural Network layers, ReLU, Loss functions<br/>• SQLite database queries and schema creation", table_cell),
            Paragraph("• <b>Machine Learning:</b> <code>KNeighborsClassifier</code> in <code>sign_engine.py</code> for classifying 13 conversational signs from engineered landmark vectors.<br/>• <b>Deep Learning:</b> <code>ASLResNet</code> CNN with Residual Skip Connections, BatchNorm, and Dropout, trained on RTX 4060 GPU with <b>99.87% accuracy</b>.<br/>• <b>SQLite Database:</b> <code>echosign.db</code> with tables, parameterized queries, and analytics.", table_cell)
        ],
        [
            Paragraph("<b>DAY 4:<br/>Computer Vision &amp; NLP</b>", table_cell_bold),
            Paragraph("• OpenCV (cv2) image reading, resizing, flipping, cropping<br/>• Real-time webcam capture loop<br/>• Object detection concepts (YOLO/Haar)<br/>• NLP text preprocessing (tokenization, stop words)<br/>• Sentiment analysis &amp; text generation", table_cell),
            Paragraph("• <b>Computer Vision:</b> Webcam stream captured, mirrored horizontally, converted BGR to RGB, decoded from base64, resized to 128x128, and normalized for PyTorch.<br/>• <b>Landmark Keypoint Tracking:</b> MediaPipe 21 hand joints &amp; upper body pose.<br/>• <b>NLP Sentence Reconstruction:</b> Rule-based intent templates convert raw tokens (<i>PLEASE WATER</i>) into polite sentences.<br/>• <b>Sentiment &amp; Urgency:</b> Categorizes urgency and emotional tone.", table_cell)
        ]
    ]

    t_bootcamp = Table(bootcamp_rows, colWidths=[95, 205, 223])
    t_bootcamp.setStyle(TableStyle([
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
    story.append(t_bootcamp)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 4: CORE ALGORITHMIC LOGIC
    # =========================================================================
    story.append(Paragraph("4. Core Algorithmic Logic &amp; Engineering Solutions", h1_style))

    story.append(Paragraph("A. Distance Normalization (Invariance to Camera Distance &amp; Hand Size)", h2_style))
    story.append(Paragraph(
        "<b>Problem:</b> If the user stands close to the camera, their hand is large in pixel space; if they stand far, it is tiny. A raw pixel coordinate model would fail immediately.<br/>"
        "<b>Mathematical Solution (sign_engine.py):</b><br/>"
        "1. <i>Translation Invariance:</i> Shift all 21 points so the wrist (Landmark 0) is centered at origin: <code>pts = pts - wrist</code>.<br/>"
        "2. <i>Scale Invariance:</i> Measure the Euclidean distance from wrist to Middle Finger Knuckle (MCP, Landmark 9): <code>palm_size = ||pts[9]||_2</code>.<br/>"
        "3. Divide all coordinates by <code>palm_size</code>: <code>pts = pts / palm_size</code>. Now, whether a small child or adult signs, coordinates remain strictly standardized.",
        body_style
    ))

    story.append(Paragraph("B. Dual-Hand Detection Logic (NAMASTE)", h2_style))
    story.append(Paragraph(
        "MediaPipe extracts 21 landmarks for both primary and secondary hands. In <code>sign_engine.py</code>, we compute the Euclidean distance between left and right wrists:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>d_wrists = sqrt((x_left - x_right)^2 + (y_left - y_right)^2)</code><br/>"
        "If <code>d_wrists &lt; 0.28</code>, both hands are pointing upwards (<code>y_tip &lt; y_wrist</code>), and fingertips touch, the system triggers <b>NAMASTE</b> with 99% confidence.",
        body_style
    ))

    story.append(Paragraph("C. Multi-Modal Body Anchors (Chest, Lips, Head)", h2_style))
    story.append(Paragraph(
        "Hand shapes alone can be ambiguous. EchoSign incorporates upper-body pose landmarks:<br/>"
        "• <b>PLEASE:</b> Flat palm placed on <b>Chest</b> (chest anchor distance <code>d &lt; 0.24</code>).<br/>"
        "• <b>WATER / FOOD / THANK YOU:</b> Hand touches or approaches <b>Lips/Chin</b> (mouth anchor distance <code>d &lt; 0.18</code>).<br/>"
        "• <b>HELLO:</b> Hand elevated at <b>Temple/Head</b> level.",
        body_style
    ))

    story.append(Paragraph("D. ASLResNet Residual Skip Connections (Solving Vanishing Gradients)", h2_style))
    story.append(Paragraph(
        "In deep CNNs, repeated matrix multiplications during backpropagation cause gradients to vanish (<code>dL/dw &rarr; 0</code>). <code>ASLResNet</code> uses <b>Skip Connections:</b> <code>y = F(x) + x</code>. The input <code>x</code> bypasses convolution layers and adds directly to the output. Gradients flow unimpeded through the identity path, enabling fast training and <b>99.87% validation accuracy</b> with only ~1.2M parameters.",
        body_style
    ))

    # =========================================================================
    # SECTION 5: TOP VIVA QUESTIONS & ANSWERS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("5. Top 12 Viva Questions &amp; Model Answers", h1_style))
    story.append(Paragraph(
        "These are the most common and challenging questions examiners ask during presentations. Memorize these concise, professional model answers:",
        body_style
    ))

    viva_qa = [
        (
            "Q1. What is the fundamental problem your project solves?",
            "EchoSign AI bridges the communication gap between 466M+ deaf/speech-impaired individuals and hearing society. Unlike standard projects that only recognize static alphabet letters, EchoSign provides a real-time two-way communication bridge: translating conversational signs into natural spoken voice (with Text-to-Speech and NLP sentence smoothing) and transcribing spoken voice into animated Sign Language Cards."
        ),
        (
            "Q2. Why did you choose FastAPI over Flask or Django?",
            "FastAPI is an asynchronous ASGI framework running on Uvicorn. Since our system processes live video frames and AI predictions in real-time, Flask's synchronous WSGI model would easily bottleneck and drop frames under concurrent requests. FastAPI is 3x faster, integrates Pydantic for automated payload validation, and automatically creates OpenAPI documentation."
        ),
        (
            "Q3. Why did you train a custom ASLResNet instead of using a standard heavy model like ResNet-50?",
            "Standard models like ResNet-50 have over 25 million parameters, requiring high GPU memory bandwidth and adding latency. Our custom ASLResNet is optimized with ~1.2 million parameters. It achieves an outstanding 99.87% validation accuracy while processing each frame in less than 2 milliseconds on the NVIDIA RTX 4060 GPU (>500 FPS throughput), making it ideal for edge deployment."
        ),
        (
            "Q4. How do you prevent false positives and camera jitter?",
            "We employ a temporal consensus filter using a rolling queue (deque of size 7). Instead of acting on a single noisy frame, the system checks predictions across the last 7 consecutive frames. A sign is only displayed and spoken once a consistent majority consensus is achieved."
        ),
        (
            "Q5. Why use MediaPipe for hand tracking instead of feeding raw video frames to a CNN?",
            "MediaPipe offloads 21 3D joint landmark extraction directly to the client browser at 60 FPS using WebAssembly/WebGL. By extracting geometric vectors, our machine learning classifier is completely immune to variations in skin tone, background clutter, and ambient room lighting."
        ),
        (
            "Q6. How does your model handle users standing at different distances from the camera?",
            "We perform mathematical coordinate normalization in NumPy. We shift all 21 landmarks relative to the wrist (origin 0,0,0) and divide by the Euclidean distance between the wrist and middle finger knuckle (palm scale). This makes the feature vector scale-invariant and distance-invariant."
        ),
        (
            "Q7. How does the NLP Sentence Reconstruction engine work?",
            "Sign language grammar differs from spoken English; signers communicate root concepts like 'PLEASE' and 'WATER'. Our NLP engine uses multi-token intent templates and category grammar to convert disconnected tokens into polite, natural spoken English: 'Could I please get some drinking water?' with emotional sentiment tags."
        ),
        (
            "Q8. How does Channel B (Hearing to Deaf) work in reverse?",
            "In Channel B, the Web Speech Recognition API transcribes the hearing person's spoken audio into text. The NLP engine tokenizes the sentence using regular expressions and matches words against our sign dictionary. It then renders animated visual Sign Language Cards on screen for the deaf individual."
        ),
        (
            "Q9. Why did you use SQLite for conversation logging instead of MongoDB?",
            "SQLite is serverless, zero-configuration, and embedded directly into Python. It maintains all conversation history, sentiment labels, and urgency scores in a single self-contained file (echosign.db) with full ACID compliance and zero administrative overhead."
        ),
        (
            "Q10. What is the role of Batch Normalization in your ASLResNet model?",
            "Batch Normalization normalizes the activations of each layer across the mini-batch, reducing internal covariate shift. This stabilizes training, allows higher learning rates, acts as a mild regularizer, and accelerates convergence."
        ),
        (
            "Q11. What is the purpose of the Cosine Annealing Learning Rate scheduler?",
            "Cosine Annealing smoothly reduces the learning rate following a cosine curve as training progresses. This helps the optimizer escape shallow local minima in early epochs and settle into a sharp, optimal global minimum in later epochs, reaching 99.87% accuracy."
        ),
        (
            "Q12. How does the system recognize dual-hand signs like Namaste?",
            "MediaPipe detects landmarks for both the primary and secondary hands. Our sign engine calculates the Euclidean distance between both wrists and index fingertips. When the wrists are adjacent (distance < 0.28) and fingers are pointing upward, it triggers Namaste with 99% confidence."
        )
    ]

    for q, a in viva_qa:
        story.append(Paragraph(q, q_style))
        story.append(Paragraph(a, a_style))

    # =========================================================================
    # SECTION 6: CHEAT SHEET & DEMO TIPS
    # =========================================================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("6. Quick Revision Cheat Sheet &amp; Guaranteed Demo Script", h1_style))

    cheat_data = [
        [
            Paragraph("<b>Architecture</b>: Custom ASLResNet (~1.2M params)<br/><b>Hardware</b>: NVIDIA GeForce RTX 4060 GPU<br/><b>Validation Accuracy</b>: <b>99.87%</b><br/><b>Inference Speed</b>: &lt; 2 ms per frame (&gt;500 FPS)", table_cell),
            Paragraph("<b>Backend Server</b>: FastAPI + Uvicorn (ASGI)<br/><b>Database</b>: SQLite (echosign.db)<br/><b>Vision Pipeline</b>: MediaPipe Hands &amp; Pose (60 FPS)<br/><b>Audio Bridge</b>: Web Speech API (TTS &amp; STT)", table_cell)
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
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Recommended 3-Step Live Demo for Evaluators:</b>", body_bold))
    story.append(Paragraph("1. <b>Showstopper Dual-Hand NAMASTE:</b> Bring both palms together in front of the chest. Show how both hands are tracked in Neon Cyan and Neon Emerald, and the system speaks: <i>'Namaste! Warm greetings and respect to everyone.'</i>", bullet_style))
    story.append(Paragraph("2. <b>NLP Sentence Smoothing (PLEASE + WATER):</b> Place a flat hand on your chest (<code>PLEASE</code>) then make a 'W' sign at your lips (<code>WATER</code>). Highlight how the NLP engine combines them into: <i>'Could I please get some drinking water?'</i>", bullet_style))
    story.append(Paragraph("3. <b>Reverse Hearing-to-Deaf Channel (Voice &rarr; Sign):</b> Switch to the Voice-to-Sign tab. Click the mic and say: <i>'Hello, do you need water or food?'</i> Show the animated Sign Language Cards generated in real time!", bullet_style))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {filename}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EchoSign_AI_Viva_and_Project_Notes.pdf")
    build_pdf(out_path)
