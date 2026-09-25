import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_document(filepath):
    doc = docx.Document()
    
    # Page setup: Margins
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Styles
    navy = RGBColor(15, 23, 42)
    accent_blue = RGBColor(2, 132, 199)
    emerald = RGBColor(5, 150, 105)
    dark_text = RGBColor(30, 41, 59)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(2)
    run_title = p_title.add_run("EchoSign AI — Complete Viva & Project Examination Guide")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = navy

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(4)
    run_sub = p_sub.add_run("Real-Time Assistive Communication Bridge | Computer Vision & Deep Learning")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(11)
    run_sub.font.bold = True
    run_sub.font.color.rgb = accent_blue

    # Meta
    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(14)
    run_meta = p_meta.add_run("Bootcamp on Artificial Intelligence by NIELIT Delhi  |  Comprehensive Capstone Notes")
    run_meta.font.name = "Arial"
    run_meta.font.size = Pt(9.5)
    run_meta.font.italic = True
    run_meta.font.color.rgb = RGBColor(100, 116, 139)

    # SECTION 1
    h1 = doc.add_heading(level=1)
    r_h1 = h1.add_run("1. Executive Summary & Problem Statement")
    r_h1.font.name = "Arial"
    r_h1.font.color.rgb = navy

    p1 = doc.add_paragraph()
    p1.add_run("Over ").font.color.rgb = dark_text
    r_bold1 = p1.add_run("466 million people worldwide")
    r_bold1.bold = True
    r_bold1.font.color.rgb = dark_text
    p1.add_run(" suffer from disabling hearing loss or speech impairment. In daily life—such as hospitals, clinics, ticket counters, and educational classrooms—communicating with hearing individuals is a severe hurdle. Conventional sign language software only supports one-way static finger spelling (A–Z). EchoSign AI solves this as a comprehensive, two-way, real-time communication hub:").font.color.rgb = dark_text

    # Bullet points for channels
    bp1 = doc.add_paragraph(style='List Bullet')
    bp1.add_run("Channel A (Deaf → Hearing): ").bold = True
    bp1.add_run("Translates webcam sign gestures & ASL finger spelling into natural spoken English voice using Text-to-Speech (TTS) and visual sentiment indicators.")

    bp2 = doc.add_paragraph(style='List Bullet')
    bp2.add_run("Channel B (Hearing → Deaf): ").bold = True
    bp2.add_run("Transcribes spoken English voice in real time into animated Sign Language Visual Cards with clear instructions so the deaf person can easily understand.")

    bp3 = doc.add_paragraph(style='List Bullet')
    bp3.add_run("Dual Vision Engine: ").bold = True
    bp3.add_run("Combines MediaPipe 21-landmark geometric classification (13 conversational signs like Namaste, Please, Water, Doctor, Pain) with an NVIDIA RTX 4060 GPU-accelerated ASLResNet Deep CNN (99.87% accuracy on 87,000 Kaggle images, <2ms latency).")

    bp4 = doc.add_paragraph(style='List Bullet')
    bp4.add_run("NLP Sentence Smoother: ").bold = True
    bp4.add_run("Reconstructs isolated sign tokens (e.g. PLEASE + WATER) into grammatically polished, polite English sentences ('Could I please get some drinking water?') with emotional tone tags.")

    # SECTION 2
    h2 = doc.add_heading(level=1)
    r_h2 = h2.add_run("2. Complete List of Libraries Used & Viva Justifications")
    r_h2.font.name = "Arial"
    r_h2.font.color.rgb = navy

    p2 = doc.add_paragraph()
    p2.add_run("Examiners frequently ask 'Why did you pick this specific library?' and 'What are the alternatives?'. Below is the complete inventory for Python backend and frontend technologies:")

    # Table of Libraries
    table_libs = doc.add_table(rows=1, cols=3)
    table_libs.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table_libs.rows[0].cells
    hdr_cells[0].text = "Library / API"
    hdr_cells[1].text = "Role in Project"
    hdr_cells[2].text = "Why Chosen Over Alternatives (Viva Reason)"

    for c in hdr_cells:
        set_cell_background(c, "0F172A")
        set_cell_margins(c, 120, 120, 150, 150)
        for p in c.paragraphs:
            for run in p.runs:
                run.font.name = "Arial"
                run.font.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(255, 255, 255)

    lib_data = [
        ("torch (PyTorch 2.6.0 + CUDA)", "Deep learning framework for defining, training, and running inference on ASLResNet.", "Dynamic computation graphs, fine-grained GPU memory management, and native FP16 Automatic Mixed Precision (AMP) on RTX 4060 Tensor Cores."),
        ("torchvision", "Image datasets and transforms pipeline (Resize, Normalize, ToTensor).", "C++ optimized computer vision backend tightly coupled with PyTorch tensors without conversion overhead."),
        ("FastAPI", "Asynchronous backend web server hosting REST endpoints (/predict_frame, /refine_sentence).", "Why not Flask? FastAPI is ASGI-based (3x faster than Flask), handles concurrent frame requests asynchronously, and has built-in Pydantic data validation."),
        ("Uvicorn", "Lightning-fast ASGI server implementation.", "Production-ready asynchronous server with non-blocking I/O event loops for real-time video inference."),
        ("Pydantic", "Request/response schema definition and landmark array data validation.", "Enforces strict typed contracts on 21 3D coordinate inputs, discarding corrupted or malformed payloads before inference."),
        ("NumPy", "21 3D landmark array operations, origin shifting, Euclidean norm distance calculations.", "High-performance C-vectorized math operations (np.linalg.norm) executed in sub-millisecond execution time."),
        ("scikit-learn", "KNeighborsClassifier for conversational word gestures and evaluation metrics.", "Lightweight, instantaneous training, zero GPU VRAM consumption for 13 geometric gestures, highly interpretable."),
        ("OpenCV (cv2)", "Image decoding from base64, color conversions (BGR to RGB), frame flipping & resizing.", "Industry standard computer vision library for manipulating raw pixel buffers with optimized memory layout."),
        ("SQLite (sqlite3)", "Persistent storage of conversation interactions, sentiment labels, urgency scores in echosign.db.", "Why not MongoDB/MySQL? Serverless, zero-config, embedded ACID-compliant database requiring no background daemon."),
        ("re (Regular Expressions)", "Speech recognition transcript tokenization and keyword isolation in nlp_engine.py.", "Deterministic, rapid string parsing without heavy neural NLP library overhead for word-to-sign card mapping."),
        ("MediaPipe Hands & Pose", "Client-side tracking of 21 3D hand joints and upper-body anchor points (lips, chest, head) at 60 FPS.", "Why not full-frame 3D CNN? Offloads heavy joint detection to client browser WebAssembly/WebGL, achieving invariance to background, lighting, and skin tones."),
        ("Web Speech API", "Native browser Text-to-Speech (TTS) and Speech-to-Text (STT) for two-way audio bridge.", "Requires zero paid cloud API keys, zero network latency, functions offline with zero operating costs.")
    ]

    for idx, (lib, role, why) in enumerate(lib_data):
        row = table_libs.add_row()
        cells = row.cells
        cells[0].text = lib
        cells[1].text = role
        cells[2].text = why
        bg = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        for i, c in enumerate(cells):
            set_cell_background(c, bg)
            set_cell_margins(c, 100, 100, 120, 120)
            for p in c.paragraphs:
                for run in p.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8.5)
                    if i == 0:
                        run.font.bold = True
                        run.font.color.rgb = navy
                    else:
                        run.font.color.rgb = dark_text

    doc.add_page_break()

    # SECTION 3
    h3 = doc.add_heading(level=1)
    r_h3 = h3.add_run("3. Mapping 4-Day NIELIT Bootcamp Curriculum to EchoSign")
    r_h3.font.name = "Arial"
    r_h3.font.color.rgb = navy

    p3 = doc.add_paragraph()
    p3.add_run("Here is the explicit proof of how every subject taught across Day 1, Day 2, Day 3, and Day 4 of the NIELIT Delhi Bootcamp was directly engineered into the EchoSign architecture:")

    table_boot = doc.add_table(rows=1, cols=3)
    table_boot.alignment = WD_TABLE_ALIGNMENT.CENTER
    b_hdr = table_boot.rows[0].cells
    b_hdr[0].text = "Bootcamp Day"
    b_hdr[1].text = "Key Curriculum Concepts Taught"
    b_hdr[2].text = "Direct Implementation in EchoSign Project"

    for c in b_hdr:
        set_cell_background(c, "0F172A")
        set_cell_margins(c, 120, 120, 150, 150)
        for p in c.paragraphs:
            for run in p.runs:
                run.font.name = "Arial"
                run.font.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(255, 255, 255)

    boot_data = [
        ("DAY 1:\nPython Basics & Logic Flow",
         "• Variables, data types, arithmetic\n• Lists, slicing, indexing (0 and -1)\n• Loops (for, while) and conditionals\n• Custom functions and string operations",
         "• Consensus Queue: collections.deque(maxlen=7) rolling window in sign_engine.py to filter out frame jitter.\n• Dictionary Metadata: SIGN_DICTIONARY storing keywords, categories, and vector icons.\n• Modular Python Functions: Structured backend in app.py, sign_engine.py, and nlp_engine.py."),
        
        ("DAY 2:\nNumPy, Pandas, Math & Regex",
         "• 2D/3D NumPy arrays & axis aggregations\n• Vector math & Euclidean norms (np.linalg.norm)\n• Missing data, cleaning, regex string matching\n• Pandas DataFrames, summary statistics & GroupBy",
         "• Coordinate Normalization: 21 3D landmarks converted to (21, 3) array. Hand origin translated to wrist (Landmark 0) and divided by palm Euclidean norm: pts / np.linalg.norm(pts[9]).\n• Regex Tokenization: re.findall(r'\\b[A-Za-z\']+\\b') in nlp_engine.py for parsing voice input.\n• Database Aggregations: Summary counts and sentiment breakdowns in database.py."),

        ("DAY 3:\nMachine Learning & Deep Learning",
         "• Supervised classification & evaluation (Accuracy, Confusion Matrix, Classification Report)\n• Decision Trees, KNN, Train-Test Split\n• Neural Network layers, ReLU, Loss functions\n• SQLite database queries and schema creation",
         "• Machine Learning: KNeighborsClassifier in sign_engine.py for classifying 13 conversational signs from engineered landmark vectors.\n• Deep Learning: ASLResNet CNN with Residual Skip Connections, BatchNorm, and Dropout, trained on RTX 4060 GPU with 99.87% accuracy.\n• SQLite Database: echosign.db with tables, parameterized queries, and analytics."),

        ("DAY 4:\nComputer Vision & NLP",
         "• OpenCV (cv2) image reading, resizing, flipping, cropping\n• Real-time webcam capture loop\n• Object detection concepts (YOLO/Haar)\n• NLP text preprocessing (tokenization, stop words)\n• Sentiment analysis & text generation",
         "• Computer Vision: Webcam stream captured, mirrored horizontally, converted BGR to RGB, decoded from base64, resized to 128x128, and normalized for PyTorch.\n• Landmark Keypoint Tracking: MediaPipe 21 hand joints & upper body pose.\n• NLP Sentence Reconstruction: Rule-based intent templates convert raw tokens (PLEASE WATER) into polite sentences.\n• Sentiment & Urgency: Categorizes urgency and emotional tone.")
    ]

    for idx, (day, taught, used) in enumerate(boot_data):
        row = table_boot.add_row()
        cells = row.cells
        cells[0].text = day
        cells[1].text = taught
        cells[2].text = used
        bg = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        for i, c in enumerate(cells):
            set_cell_background(c, bg)
            set_cell_margins(c, 100, 100, 120, 120)
            for p in c.paragraphs:
                for run in p.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8.5)
                    if i == 0:
                        run.font.bold = True
                        run.font.color.rgb = navy
                    else:
                        run.font.color.rgb = dark_text

    # SECTION 4
    h4 = doc.add_heading(level=1)
    r_h4 = h4.add_run("4. Core Algorithmic Logic & Engineering Solutions")
    r_h4.font.name = "Arial"
    r_h4.font.color.rgb = navy

    h4_a = doc.add_heading(level=2)
    h4_a.add_run("A. Distance Normalization (Invariance to Camera Distance & Hand Size)").font.color.rgb = accent_blue
    doc.add_paragraph("Problem: If the user stands close to the camera, their hand is large in pixel space; if they stand far, it is tiny. A raw pixel coordinate model would fail immediately.\n"
                      "Mathematical Solution (sign_engine.py):\n"
                      "1. Translation Invariance: Shift all 21 points so the wrist (Landmark 0) is centered at origin: pts = pts - wrist.\n"
                      "2. Scale Invariance: Measure the Euclidean distance from wrist to Middle Finger Knuckle (MCP, Landmark 9): palm_size = ||pts[9]||_2.\n"
                      "3. Divide all coordinates by palm_size: pts = pts / palm_size. Now, whether a small child or adult signs, coordinates remain strictly standardized.")

    h4_b = doc.add_heading(level=2)
    h4_b.add_run("B. Dual-Hand Detection Logic (NAMASTE)").font.color.rgb = accent_blue
    doc.add_paragraph("MediaPipe extracts 21 landmarks for both primary and secondary hands. In sign_engine.py, we compute the Euclidean distance between left and right wrists:\n"
                      "    d_wrists = sqrt((x_left - x_right)^2 + (y_left - y_right)^2)\n"
                      "If d_wrists < 0.28, both hands are pointing upwards (y_tip < y_wrist), and fingertips touch, the system triggers NAMASTE with 99% confidence.")

    h4_c = doc.add_heading(level=2)
    h4_c.add_run("C. Multi-Modal Body Anchors (Chest, Lips, Head)").font.color.rgb = accent_blue
    doc.add_paragraph("Hand shapes alone can be ambiguous. EchoSign incorporates upper-body pose landmarks:\n"
                      "• PLEASE: Flat palm placed on Chest (chest anchor distance d < 0.24).\n"
                      "• WATER / FOOD / THANK YOU: Hand touches or approaches Lips/Chin (mouth anchor distance d < 0.18).\n"
                      "• HELLO: Hand elevated at Temple/Head level.")

    h4_d = doc.add_heading(level=2)
    h4_d.add_run("D. ASLResNet Residual Skip Connections (Solving Vanishing Gradients)").font.color.rgb = accent_blue
    doc.add_paragraph("In deep CNNs, repeated matrix multiplications during backpropagation cause gradients to vanish (dL/dw → 0). ASLResNet uses Skip Connections: y = F(x) + x. The input x bypasses convolution layers and adds directly to the output. Gradients flow unimpeded through the identity path, enabling fast training and 99.87% validation accuracy with only ~1.2M parameters.")

    doc.add_page_break()

    # SECTION 5: TOP VIVA QUESTIONS
    h5 = doc.add_heading(level=1)
    r_h5 = h5.add_run("5. Top 12 Viva Questions & Model Answers")
    r_h5.font.name = "Arial"
    r_h5.font.color.rgb = navy

    viva_qa = [
        ("Q1. What is the fundamental problem your project solves?",
         "EchoSign AI bridges the communication gap between 466M+ deaf/speech-impaired individuals and hearing society. Unlike standard projects that only recognize static alphabet letters, EchoSign provides a real-time two-way communication bridge: translating conversational signs into natural spoken voice (with Text-to-Speech and NLP sentence smoothing) and transcribing spoken voice into animated Sign Language Cards."),
        
        ("Q2. Why did you choose FastAPI over Flask or Django?",
         "FastAPI is an asynchronous ASGI framework running on Uvicorn. Since our system processes live video frames and AI predictions in real-time, Flask's synchronous WSGI model would easily bottleneck and drop frames under concurrent requests. FastAPI is 3x faster, integrates Pydantic for automated payload validation, and automatically creates OpenAPI documentation."),

        ("Q3. Why did you train a custom ASLResNet instead of using a standard heavy model like ResNet-50?",
         "Standard models like ResNet-50 have over 25 million parameters, requiring high GPU memory bandwidth and adding latency. Our custom ASLResNet is optimized with ~1.2 million parameters. It achieves an outstanding 99.87% validation accuracy while processing each frame in less than 2 milliseconds on the NVIDIA RTX 4060 GPU (>500 FPS throughput), making it ideal for edge deployment."),

        ("Q4. How do you prevent false positives and camera jitter?",
         "We employ a temporal consensus filter using a rolling queue (deque of size 7). Instead of acting on a single noisy frame, the system checks predictions across the last 7 consecutive frames. A sign is only displayed and spoken once a consistent majority consensus is achieved."),

        ("Q5. Why use MediaPipe for hand tracking instead of feeding raw video frames to a CNN?",
         "MediaPipe offloads 21 3D joint landmark extraction directly to the client browser at 60 FPS using WebAssembly/WebGL. By extracting geometric vectors, our machine learning classifier is completely immune to variations in skin tone, background clutter, and ambient room lighting."),

        ("Q6. How does your model handle users standing at different distances from the camera?",
         "We perform mathematical coordinate normalization in NumPy. We shift all 21 landmarks relative to the wrist (origin 0,0,0) and divide by the Euclidean distance between the wrist and middle finger knuckle (palm scale). This makes the feature vector scale-invariant and distance-invariant."),

        ("Q7. How does the NLP Sentence Reconstruction engine work?",
         "Sign language grammar differs from spoken English; signers communicate root concepts like 'PLEASE' and 'WATER'. Our NLP engine uses multi-token intent templates and category grammar to convert disconnected tokens into polite, natural spoken English: 'Could I please get some drinking water?' with emotional sentiment tags."),

        ("Q8. How does Channel B (Hearing to Deaf) work in reverse?",
         "In Channel B, the Web Speech Recognition API transcribes the hearing person's spoken audio into text. The NLP engine tokenizes the sentence using regular expressions and matches words against our sign dictionary. It then renders animated visual Sign Language Cards on screen for the deaf individual."),

        ("Q9. Why did you use SQLite for conversation logging instead of MongoDB?",
         "SQLite is serverless, zero-configuration, and embedded directly into Python. It maintains all conversation history, sentiment labels, and urgency scores in a single self-contained file (echosign.db) with full ACID compliance and zero administrative overhead."),

        ("Q10. What is the role of Batch Normalization in your ASLResNet model?",
         "Batch Normalization normalizes the activations of each layer across the mini-batch, reducing internal covariate shift. This stabilizes training, allows higher learning rates, acts as a mild regularizer, and accelerates convergence."),

        ("Q11. What is the purpose of the Cosine Annealing Learning Rate scheduler?",
         "Cosine Annealing smoothly reduces the learning rate following a cosine curve as training progresses. This helps the optimizer escape shallow local minima in early epochs and settle into a sharp, optimal global minimum in later epochs, reaching 99.87% accuracy."),

        ("Q12. How does the system recognize dual-hand signs like Namaste?",
         "MediaPipe detects landmarks for both the primary and secondary hands. Our sign engine calculates the Euclidean distance between both wrists and index fingertips. When the wrists are adjacent (distance < 0.28) and fingers are pointing upward, it triggers Namaste with 99% confidence.")
    ]

    for q, a in viva_qa:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(6)
        p_q.paragraph_format.space_after = Pt(2)
        r_q = p_q.add_run(q)
        r_q.font.name = "Arial"
        r_q.font.bold = True
        r_q.font.size = Pt(10)
        r_q.font.color.rgb = accent_blue

        p_a = doc.add_paragraph()
        p_a.paragraph_format.left_indent = Inches(0.2)
        p_a.paragraph_format.space_after = Pt(6)
        r_a = p_a.add_run(a)
        r_a.font.name = "Arial"
        r_a.font.size = Pt(9.5)
        r_a.font.color.rgb = dark_text

    # SECTION 6
    h6 = doc.add_heading(level=1)
    r_h6 = h6.add_run("6. Quick Revision Cheat Sheet & Guaranteed Demo Script")
    r_h6.font.name = "Arial"
    r_h6.font.color.rgb = navy

    table_cheat = doc.add_table(rows=1, cols=2)
    table_cheat.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_cells = table_cheat.rows[0].cells
    c_cells[0].text = "• Architecture: Custom ASLResNet (~1.2M params)\n• Hardware: NVIDIA GeForce RTX 4060 GPU\n• Validation Accuracy: 99.87%\n• Inference Speed: < 2 ms per frame (>500 FPS)"
    c_cells[1].text = "• Backend Server: FastAPI + Uvicorn (ASGI)\n• Database: SQLite (echosign.db)\n• Vision Pipeline: MediaPipe Hands & Pose (60 FPS)\n• Audio Bridge: Web Speech API (TTS & STT)"

    for c in c_cells:
        set_cell_background(c, "F8FAFC")
        set_cell_margins(c, 100, 100, 150, 150)
        for p in c.paragraphs:
            for run in p.runs:
                run.font.name = "Arial"
                run.font.size = Pt(9)
                run.font.color.rgb = dark_text

    p_demo = doc.add_paragraph()
    p_demo.paragraph_format.space_before = Pt(10)
    p_demo.add_run("Recommended 3-Step Live Demo for Evaluators:").bold = True

    d1 = doc.add_paragraph(style='List Bullet')
    d1.add_run("1. Showstopper Dual-Hand NAMASTE: ").bold = True
    d1.add_run("Bring both palms together in front of the chest. Show how both hands are tracked in Neon Cyan and Neon Emerald, and the system speaks: 'Namaste! Warm greetings and respect to everyone.'")

    d2 = doc.add_paragraph(style='List Bullet')
    d2.add_run("2. NLP Sentence Smoothing (PLEASE + WATER): ").bold = True
    d2.add_run("Place a flat hand on your chest (PLEASE) then make a 'W' sign at your lips (WATER). Highlight how the NLP engine combines them into: 'Could I please get some drinking water?'")

    d3 = doc.add_paragraph(style='List Bullet')
    d3.add_run("3. Reverse Hearing-to-Deaf Channel (Voice → Sign): ").bold = True
    d3.add_run("Switch to the Voice-to-Sign tab. Click the mic and say: 'Hello, do you need water or food?' Show the animated Sign Language Cards generated in real time!")

    doc.save(filepath)
    print(f"Successfully generated DOCX: {filepath}")

if __name__ == "__main__":
    out_docx = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EchoSign_AI_Viva_and_Project_Notes.docx")
    create_document(out_docx)
