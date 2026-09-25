/* ==========================================================================
   AirCanvas AI — Touchless Hand Gesture Whiteboard Engine
   ========================================================================== */

// --- Global State ---
const state = {
  // Tools & Drawing
  tool: 'pen', // 'pen' or 'eraser'
  color: '#00f2fe',
  size: 8,
  eraserSize: 36,
  magicShape: false,
  
  // Tracking & Gestures
  activeGesture: 'NONE',
  isDrawing: false,
  lastPoint: null,
  currentStroke: [],
  history: [], // For undo
  strokesCount: 0,
  colorsUsed: new Set(['#00f2fe']),
  
  // Fist Clear timer
  fistStartTime: null,
  fistHoldDuration: 1400, // ms
  
  // Thumbs Up Save timer
  thumbsStartTime: null,
  thumbsHoldDuration: 1200, // ms
  thumbsTriggered: false,

  // Hover virtual palette debounce
  hoveredPaletteItem: null,
  hoverPaletteStartTime: null,

  // Voice
  voiceActive: false,
  speechRecognizer: null
};

// --- DOM References ---
const videoElem = document.getElementById('webcam');
const canvasDraw = document.getElementById('canvasDraw');
const canvasHud = document.getElementById('canvasHud');
const pipCanvas = document.getElementById('pipCanvas');
const ctxDraw = canvasDraw.getContext('2d');
const ctxHud = canvasHud.getContext('2d');
const ctxPip = pipCanvas.getContext('2d');

const hudGesture = document.getElementById('hudGesture');
const fistClearProgress = document.getElementById('fistClearProgress');
const fistCircle = document.querySelector('.progress-ring-circle');
const circumference = 2 * Math.PI * 32;
if (fistCircle) {
  fistCircle.style.strokeDasharray = `${circumference} ${circumference}`;
  fistCircle.style.strokeDashoffset = circumference;
}

const voiceToast = document.getElementById('voiceToast');
const voiceToastText = document.getElementById('voiceToastText');
const btnVoiceToggle = document.getElementById('btnVoiceToggle');
const btnGalleryToggle = document.getElementById('btnGalleryToggle');
const galleryModal = document.getElementById('galleryModal');
const btnCloseGallery = document.getElementById('btnCloseGallery');
const galleryGrid = document.getElementById('galleryGrid');

// --- Sound Synthesizer (Web Audio API) ---
let audioCtx = null;
function playSound(type) {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    const now = audioCtx.currentTime;
    if (type === 'pop') {
      osc.frequency.setValueAtTime(520, now);
      osc.frequency.exponentialRampToValueAtTime(840, now + 0.08);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.linearRampToValueAtTime(0.01, now + 0.08);
      osc.start(now);
      osc.stop(now + 0.08);
    } else if (type === 'clear') {
      osc.frequency.setValueAtTime(400, now);
      osc.frequency.exponentialRampToValueAtTime(150, now + 0.25);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.linearRampToValueAtTime(0.01, now + 0.25);
      osc.start(now);
      osc.stop(now + 0.25);
    } else if (type === 'save') {
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(440, now); // A4
      osc.frequency.setValueAtTime(554.37, now + 0.1); // C#5
      osc.frequency.setValueAtTime(659.25, now + 0.2); // E5
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.linearRampToValueAtTime(0.01, now + 0.4);
      osc.start(now);
      osc.stop(now + 0.4);
    }
  } catch (e) {
    // Audio context policy fallback
  }
}

// --- Window Resize & Canvas Initialization ---
function resizeCanvases() {
  const rect = canvasDraw.parentElement.getBoundingClientRect();
  
  // Save current drawing image before resize
  const tempCanvas = document.createElement('canvas');
  tempCanvas.width = canvasDraw.width;
  tempCanvas.height = canvasDraw.height;
  const tempCtx = tempCanvas.getContext('2d');
  tempCtx.drawImage(canvasDraw, 0, 0);

  canvasDraw.width = rect.width;
  canvasDraw.height = rect.height;
  canvasHud.width = rect.width;
  canvasHud.height = rect.height;

  // Restore drawing content
  if (tempCanvas.width > 0) {
    ctxDraw.drawImage(tempCanvas, 0, 0, rect.width, rect.height);
  }
}
window.addEventListener('resize', resizeCanvases);
resizeCanvases();

// Save state for Undo
function pushState() {
  const snapshot = ctxDraw.getImageData(0, 0, canvasDraw.width, canvasDraw.height);
  state.history.push(snapshot);
  if (state.history.length > 20) state.history.shift(); // Limit undo steps
}
pushState();

function undo() {
  if (state.history.length > 1) {
    state.history.pop(); // Remove current state
    const previous = state.history[state.history.length - 1];
    ctxDraw.putImageData(previous, 0, 0);
    showVoiceToast("↩️ Undone last action");
    playSound('pop');
  } else {
    showVoiceToast("⚠️ Nothing to undo");
  }
}

function clearCanvas() {
  ctxDraw.clearRect(0, 0, canvasDraw.width, canvasDraw.height);
  pushState();
  state.strokesCount = 0;
  playSound('clear');
  showVoiceToast("🗑️ Canvas Cleared!");
}

// --- Snapshot & Save to Gallery ---
async function saveArtworkSnapshot() {
  playSound('save');
  showVoiceToast("💾 Saving artwork to Gallery...");

  // Create merged image with dark background
  const exportCanvas = document.createElement('canvas');
  exportCanvas.width = canvasDraw.width;
  exportCanvas.height = canvasDraw.height;
  const expCtx = exportCanvas.getContext('2d');
  
  // Dark canvas backdrop
  expCtx.fillStyle = '#080c14';
  expCtx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
  expCtx.drawImage(canvasDraw, 0, 0);

  // Watermark
  expCtx.fillStyle = 'rgba(255, 255, 255, 0.4)';
  expCtx.font = '14px Outfit, sans-serif';
  expCtx.fillText('Created with AirCanvas AI', 24, exportCanvas.height - 24);

  const base64Data = exportCanvas.toDataURL('image/png');

  try {
    const res = await fetch('/api/save_artwork', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: base64Data,
        title: `AirCanvas Art ${new Date().toLocaleTimeString()}`,
        strokes_count: state.strokesCount,
        colors_used: Array.from(state.colorsUsed).join(', ')
      })
    });
    const data = await res.json();
    showVoiceToast("✅ Saved to Gallery!");
    
    // Also trigger browser download
    const a = document.createElement('a');
    a.href = base64Data;
    a.download = `AirCanvas_${Date.now()}.png`;
    a.click();
  } catch (err) {
    showVoiceToast("❌ Error saving snapshot");
  }
}

// --- Gesture Detection Logic ---
function detectGesture(landmarks) {
  // landmarks is an array of 21 {x, y, z} points normalized 0.0 to 1.0
  const pts = landmarks;

  // Finger extended checks (tip y < pip y for upright hand)
  const isIndexUp = pts[8].y < pts[6].y;
  const isMiddleUp = pts[12].y < pts[10].y;
  const isRingUp = pts[16].y < pts[14].y;
  const isPinkyUp = pts[20].y < pts[18].y;
  
  // Thumb extended (check x displacement from base)
  const isThumbUp = pts[4].y < pts[3].y && pts[4].y < pts[2].y;

  const upFingersCount = (isIndexUp ? 1 : 0) + (isMiddleUp ? 1 : 0) + (isRingUp ? 1 : 0) + (isPinkyUp ? 1 : 0);

  // 1. CLEAR: Closed Fist (0 fingers up, thumb tucked)
  if (upFingersCount === 0 && pts[4].y > pts[8].y) {
    return 'FIST_CLEAR';
  }

  // 2. SAVE: Thumbs Up (Thumb up, other 4 fingers curled down)
  if (isThumbUp && upFingersCount === 0) {
    return 'THUMBS_UP_SAVE';
  }

  // 3. ERASER: Open Palm (4 or 5 fingers extended)
  if (upFingersCount >= 4) {
    return 'ERASER';
  }

  // 4. HOVER / SELECT: Peace Sign (Index + Middle Up, Ring and Pinky Down)
  if (isIndexUp && isMiddleUp && !isRingUp && !isPinkyUp) {
    return 'HOVER_SELECT';
  }

  // 5. DRAW: Only Index Up (Middle, Ring, Pinky Down)
  if (isIndexUp && !isMiddleUp && !isRingUp && !isPinkyUp) {
    return 'DRAW';
  }

  return 'NEUTRAL';
}

// --- MediaPipe Hands Processing Loop ---
function onResults(results) {
  // Draw Webcam to PIP
  if (results.image) {
    ctxPip.save();
    ctxPip.clearRect(0, 0, pipCanvas.width, pipCanvas.height);
    ctxPip.drawImage(results.image, 0, 0, pipCanvas.width, pipCanvas.height);
    ctxPip.restore();
  }

  // Clear HUD overlay canvas each frame
  ctxHud.clearRect(0, 0, canvasHud.width, canvasHud.height);

  if (!results.multiHandLandmarks || results.multiHandLandmarks.length === 0) {
    updateHudGestureBadge('WAITING FOR HAND', '✋', '#94a3b8');
    fistClearProgress.style.display = 'none';
    state.fistStartTime = null;
    state.thumbsStartTime = null;
    state.thumbsTriggered = false;
    finishCurrentStroke();
    return;
  }

  const landmarks = results.multiHandLandmarks[0];
  const gesture = detectGesture(landmarks);
  state.activeGesture = gesture;

  // Convert index fingertip Landmark 8 to canvas pixel coords (Mirrored horizontally: 1 - x)
  const indexTip = {
    x: (1 - landmarks[8].x) * canvasDraw.width,
    y: landmarks[8].y * canvasDraw.height
  };

  // Palm center (Landmark 9 middle MCP) for eraser
  const palmCenter = {
    x: (1 - landmarks[9].x) * canvasDraw.width,
    y: landmarks[9].y * canvasDraw.height
  };

  // Draw hand skeleton on HUD
  drawHandSkeleton(landmarks);

  // Check top Virtual Palette hover collision
  checkVirtualPaletteHover(indexTip);

  // --- Handle Gestures ---

  // 1. FIST CLEAR
  if (gesture === 'FIST_CLEAR') {
    finishCurrentStroke();
    updateHudGestureBadge('HOLDING FIST (CLEARING)', '✊', '#f43f5e');
    fistClearProgress.style.display = 'flex';

    if (!state.fistStartTime) state.fistStartTime = Date.now();
    const elapsed = Date.now() - state.fistStartTime;
    const progress = Math.min(1.0, elapsed / state.fistHoldDuration);

    if (fistCircle) {
      const offset = circumference - progress * circumference;
      fistCircle.style.strokeDashoffset = offset;
    }

    if (elapsed >= state.fistHoldDuration) {
      clearCanvas();
      state.fistStartTime = null;
      fistClearProgress.style.display = 'none';
    }
    return;
  } else {
    fistClearProgress.style.display = 'none';
    state.fistStartTime = null;
  }

  // 2. THUMBS UP (SAVE)
  if (gesture === 'THUMBS_UP_SAVE') {
    finishCurrentStroke();
    updateHudGestureBadge('THUMBS UP (SAVING ART)', '👍', '#00f2fe');

    if (!state.thumbsStartTime) {
      state.thumbsStartTime = Date.now();
      state.thumbsTriggered = false;
    }

    const elapsed = Date.now() - state.thumbsStartTime;
    if (elapsed > state.thumbsHoldDuration && !state.thumbsTriggered) {
      state.thumbsTriggered = true;
      saveArtworkSnapshot();
    }
    return;
  } else {
    state.thumbsStartTime = null;
    state.thumbsTriggered = false;
  }

  // 3. ERASER (Open Palm)
  if (gesture === 'ERASER' || state.tool === 'eraser') {
    finishCurrentStroke();
    updateHudGestureBadge('ERASER MODE (PALM)', '🧹', '#ec4899');
    
    // Draw Eraser Circle on HUD
    ctxHud.save();
    ctxHud.beginPath();
    ctxHud.arc(palmCenter.x, palmCenter.y, state.eraserSize, 0, Math.PI * 2);
    ctxHud.strokeStyle = '#ec4899';
    ctxHud.lineWidth = 3;
    ctxHud.setLineDash([6, 6]);
    ctxHud.stroke();
    ctxHud.fillStyle = 'rgba(236, 72, 153, 0.15)';
    ctxHud.fill();
    ctxHud.restore();

    // Erase on canvasDraw
    ctxDraw.save();
    ctxDraw.globalCompositeOperation = 'destination-out';
    ctxDraw.beginPath();
    ctxDraw.arc(palmCenter.x, palmCenter.y, state.eraserSize, 0, Math.PI * 2);
    ctxDraw.fill();
    ctxDraw.restore();
    return;
  }

  // 4. HOVER / SELECT (Peace Sign)
  if (gesture === 'HOVER_SELECT') {
    finishCurrentStroke();
    updateHudGestureBadge('HOVER / SELECT COLOR', '✌️', '#10b981');

    // Draw glowing crosshair cursor on HUD
    ctxHud.save();
    ctxHud.beginPath();
    ctxHud.arc(indexTip.x, indexTip.y, 14, 0, Math.PI * 2);
    ctxHud.strokeStyle = '#10b981';
    ctxHud.lineWidth = 2.5;
    ctxHud.stroke();
    ctxHud.fillStyle = 'rgba(16, 185, 129, 0.2)';
    ctxHud.fill();
    ctxHud.restore();
    return;
  }

  // 5. DRAW (Index Finger Up)
  if (gesture === 'DRAW') {
    updateHudGestureBadge('DRAWING MODE', '✏️', state.color);

    // Draw glowing pen pointer on HUD
    ctxHud.save();
    ctxHud.beginPath();
    ctxHud.arc(indexTip.x, indexTip.y, state.size * 0.9, 0, Math.PI * 2);
    ctxHud.fillStyle = state.color;
    ctxHud.shadowColor = state.color;
    ctxHud.shadowBlur = 15;
    ctxHud.fill();
    ctxHud.restore();

    // Draw on canvas
    if (!state.isDrawing) {
      state.isDrawing = true;
      state.lastPoint = indexTip;
      state.currentStroke = [indexTip];
      state.strokesCount++;
      state.colorsUsed.add(state.color);
    } else {
      ctxDraw.save();
      ctxDraw.beginPath();
      ctxDraw.moveTo(state.lastPoint.x, state.lastPoint.y);
      
      // Quadratic curve midpoint for buttery smooth lines
      const midPoint = {
        x: (state.lastPoint.x + indexTip.x) / 2,
        y: (state.lastPoint.y + indexTip.y) / 2
      };
      ctxDraw.quadraticCurveTo(state.lastPoint.x, state.lastPoint.y, midPoint.x, midPoint.y);
      
      ctxDraw.lineCap = 'round';
      ctxDraw.lineJoin = 'round';
      ctxDraw.strokeStyle = state.color;
      ctxDraw.lineWidth = state.size;
      ctxDraw.shadowColor = state.color;
      ctxDraw.shadowBlur = state.size * 1.5;
      ctxDraw.stroke();
      ctxDraw.restore();

      state.lastPoint = indexTip;
      state.currentStroke.push(indexTip);
    }
  } else {
    finishCurrentStroke();
  }
}

// --- Finish Stroke & Smart Shape Snapping ---
async function finishCurrentStroke() {
  if (state.isDrawing) {
    state.isDrawing = false;
    state.lastPoint = null;
    pushState();

    // If Magic Shape is enabled and stroke is substantial
    if (state.magicShape && state.currentStroke.length >= 12) {
      try {
        const strokePoints = state.currentStroke.map(p => [p.x, p.y]);
        const res = await fetch('/api/snap_shape', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ points: strokePoints })
        });
        const shapeData = await res.json();

        if (shapeData.shape && shapeData.shape !== 'FREEHAND') {
          // Replace last stroke with snapped shape!
          if (state.history.length > 1) {
            state.history.pop();
            const prev = state.history[state.history.length - 1];
            ctxDraw.putImageData(prev, 0, 0);
          }

          drawSnappedShape(shapeData);
          pushState();
          showVoiceToast(`✨ Snapped to ${shapeData.shape}!`);
          playSound('pop');
        }
      } catch (err) {
        // Fallback to normal stroke
      }
    }
    state.currentStroke = [];
  }
}

function drawSnappedShape(data) {
  ctxDraw.save();
  ctxDraw.strokeStyle = state.color;
  ctxDraw.lineWidth = state.size;
  ctxDraw.lineCap = 'round';
  ctxDraw.lineJoin = 'round';
  ctxDraw.shadowColor = state.color;
  ctxDraw.shadowBlur = state.size * 1.5;

  if (data.shape === 'CIRCLE') {
    const { center, radius } = data.params;
    ctxDraw.beginPath();
    ctxDraw.arc(center[0], center[1], radius, 0, Math.PI * 2);
    ctxDraw.stroke();
  } else if (data.shape === 'RECTANGLE') {
    const { x, y, width, height } = data.params;
    ctxDraw.beginPath();
    ctxDraw.strokeRect(x, y, width, height);
  } else if (data.shape === 'TRIANGLE') {
    const v = data.params.vertices;
    ctxDraw.beginPath();
    ctxDraw.moveTo(v[0][0], v[0][1]);
    ctxDraw.lineTo(v[1][0], v[1][1]);
    ctxDraw.lineTo(v[2][0], v[2][1]);
    ctxDraw.closePath();
    ctxDraw.stroke();
  } else if (data.shape === 'LINE') {
    const { start, end } = data.params;
    ctxDraw.beginPath();
    ctxDraw.moveTo(start[0], start[1]);
    ctxDraw.lineTo(end[0], end[1]);
    ctxDraw.stroke();
  }
  ctxDraw.restore();
}

// --- Virtual Air Color Bar Collision Detection ---
function checkVirtualPaletteHover(point) {
  const paletteElem = document.getElementById('virtualPalette');
  const rect = paletteElem.getBoundingClientRect();

  if (point.x >= rect.left && point.x <= rect.right && point.y >= rect.top && point.y <= rect.bottom) {
    const items = paletteElem.querySelectorAll('.palette-item');
    items.forEach(item => {
      const iRect = item.getBoundingClientRect();
      if (point.x >= iRect.left && point.x <= iRect.right && point.y >= iRect.top && point.y <= iRect.bottom) {
        item.classList.add('hovered-air');

        // Select color if hovered for ~300ms
        if (state.hoveredPaletteItem !== item) {
          state.hoveredPaletteItem = item;
          state.hoverPaletteStartTime = Date.now();
        } else if (Date.now() - state.hoverPaletteStartTime > 280) {
          triggerPaletteSelect(item);
          state.hoverPaletteStartTime = Date.now() + 10000; // prevent repeat trigger
        }
      } else {
        item.classList.remove('hovered-air');
      }
    });
  } else {
    state.hoveredPaletteItem = null;
    document.querySelectorAll('.palette-item').forEach(i => i.classList.remove('hovered-air'));
  }
}

function triggerPaletteSelect(item) {
  document.querySelectorAll('.palette-item').forEach(i => i.classList.remove('active'));
  item.classList.add('active');

  const toolType = item.getAttribute('data-tool');
  if (toolType === 'eraser') {
    state.tool = 'eraser';
    showVoiceToast('🧹 Switched to Eraser');
  } else {
    state.tool = 'pen';
    state.color = item.getAttribute('data-color');
    showVoiceToast(`🎨 Color: ${item.querySelector('.color-label').innerText}`);
  }
  playSound('pop');
}

// --- Draw Hand Skeleton on HUD ---
function drawHandSkeleton(landmarks) {
  ctxHud.save();
  ctxHud.lineWidth = 1.5;
  ctxHud.strokeStyle = 'rgba(0, 242, 254, 0.4)';
  ctxHud.fillStyle = '#00f2fe';

  const CONNECTIONS = [
    [0,1],[1,2],[2,3],[3,4],
    [0,5],[5,6],[6,7],[7,8],
    [5,9],[9,10],[10,11],[11,12],
    [9,13],[13,14],[14,15],[15,16],
    [13,17],[17,18],[18,19],[19,20],[0,17]
  ];

  CONNECTIONS.forEach(([i, j]) => {
    const x1 = (1 - landmarks[i].x) * canvasHud.width;
    const y1 = landmarks[i].y * canvasHud.height;
    const x2 = (1 - landmarks[j].x) * canvasHud.width;
    const y2 = landmarks[j].y * canvasHud.height;

    ctxHud.beginPath();
    ctxHud.moveTo(x1, y1);
    ctxHud.lineTo(x2, y2);
    ctxHud.stroke();
  });

  landmarks.forEach((p, idx) => {
    const x = (1 - p.x) * canvasHud.width;
    const y = p.y * canvasHud.height;
    ctxHud.beginPath();
    ctxHud.arc(x, y, idx === 8 ? 5 : 2.5, 0, Math.PI * 2);
    ctxHud.fill();
  });
  ctxHud.restore();
}

function updateHudGestureBadge(name, emoji, color) {
  hudGesture.querySelector('.gesture-name').innerText = name;
  hudGesture.querySelector('.gesture-name').style.color = color;
  hudGesture.querySelector('.gesture-icon').innerText = emoji;
}

function showVoiceToast(msg) {
  voiceToastText.innerText = msg;
  voiceToast.style.display = 'flex';
  clearTimeout(voiceToast.timeout);
  voiceToast.timeout = setTimeout(() => {
    voiceToast.style.display = 'none';
  }, 2500);
}

// --- Web Speech API & NLP Voice Control ---
function initVoiceCommands() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showVoiceToast("Voice control not supported in this browser.");
    return;
  }

  const recognizer = new SpeechRecognition();
  recognizer.continuous = true;
  recognizer.interimResults = false;
  recognizer.lang = 'en-US';

  recognizer.onresult = async (event) => {
    const transcript = event.results[event.results.length - 1][0].transcript;
    showVoiceToast(`🎙️ "${transcript}"`);

    try {
      const res = await fetch('/api/parse_voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: transcript })
      });
      const data = await res.json();
      executeVoiceAction(data);
    } catch (err) {
      console.error(err);
    }
  };

  recognizer.onerror = () => {
    // Auto restart if active
    if (state.voiceActive) {
      setTimeout(() => recognizer.start(), 1000);
    }
  };

  recognizer.onend = () => {
    if (state.voiceActive) {
      recognizer.start();
    }
  };

  state.speechRecognizer = recognizer;
}

function executeVoiceAction(data) {
  if (data.action === 'CLEAR_CANVAS') {
    clearCanvas();
  } else if (data.action === 'SAVE_CANVAS') {
    saveArtworkSnapshot();
  } else if (data.action === 'UNDO') {
    undo();
  } else if (data.action === 'SET_TOOL') {
    state.tool = data.tool;
    document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
    if (data.tool === 'pen') document.getElementById('toolPen').classList.add('active');
    if (data.tool === 'eraser') document.getElementById('toolEraser').classList.add('active');
  } else if (data.action === 'SET_COLOR') {
    state.color = data.color;
    state.tool = 'pen';
    document.querySelectorAll('.palette-item').forEach(i => {
      if (i.getAttribute('data-color') === data.color) i.classList.add('active');
      else i.classList.remove('active');
    });
  } else if (data.action === 'SET_SIZE') {
    state.size = data.size;
  } else if (data.action === 'TOGGLE_SHAPE') {
    toggleMagicShape();
  }

  if (data.message) {
    showVoiceToast(data.message);
    speakVoice(data.message);
  }
}

function speakVoice(text) {
  if ('speechSynthesis' in window) {
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1.1;
    window.speechSynthesis.speak(utter);
  }
}

// --- UI Event Handlers ---
document.querySelectorAll('.palette-item').forEach(item => {
  item.addEventListener('click', () => triggerPaletteSelect(item));
});

document.getElementById('toolPen').addEventListener('click', () => {
  state.tool = 'pen';
  document.getElementById('toolPen').classList.add('active');
  document.getElementById('toolEraser').classList.remove('active');
  showVoiceToast('✏️ Pen Tool Selected');
});

document.getElementById('toolEraser').addEventListener('click', () => {
  state.tool = 'eraser';
  document.getElementById('toolEraser').classList.add('active');
  document.getElementById('toolPen').classList.remove('active');
  showVoiceToast('🧹 Eraser Tool Selected');
});

function toggleMagicShape() {
  state.magicShape = !state.magicShape;
  const ind = document.getElementById('shapeIndicator');
  if (state.magicShape) {
    ind.className = 'shape-indicator on';
    ind.innerText = 'ON';
    showVoiceToast('✨ Smart Shape Snapping ON');
  } else {
    ind.className = 'shape-indicator off';
    ind.innerText = 'OFF';
    showVoiceToast('✨ Smart Shape Snapping OFF');
  }
}
document.getElementById('toolMagicShape').addEventListener('click', toggleMagicShape);

document.querySelectorAll('.size-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    state.size = parseInt(btn.getAttribute('data-size'));
    showVoiceToast(`Size: ${btn.innerText}`);
  });
});

document.getElementById('btnUndo').addEventListener('click', undo);
document.getElementById('btnClear').addEventListener('click', clearCanvas);
document.getElementById('btnSave').addEventListener('click', saveArtworkSnapshot);

// Voice button toggle
btnVoiceToggle.addEventListener('click', () => {
  if (!state.speechRecognizer) initVoiceCommands();
  state.voiceActive = !state.voiceActive;
  if (state.voiceActive) {
    btnVoiceToggle.classList.add('active');
    state.speechRecognizer.start();
    showVoiceToast('🎙️ Voice AI Active! Speak commands.');
  } else {
    btnVoiceToggle.classList.remove('active');
    state.speechRecognizer.stop();
    showVoiceToast('🎙️ Voice AI Paused');
  }
});

// Gallery Modal Handlers
btnGalleryToggle.addEventListener('click', async () => {
  galleryModal.style.display = 'flex';
  try {
    const res = await fetch('/api/gallery');
    const rows = await res.json();
    if (!rows || rows.length === 0) {
      galleryGrid.innerHTML = '<p class="empty-gallery">No artworks saved yet. Draw something and save!</p>';
    } else {
      galleryGrid.innerHTML = rows.map(r => `
        <div class="gallery-card" data-id="${r.id}">
          <img src="${r.url}" alt="${r.title}">
          <div class="gallery-card-info">
            <div>
              <div style="font-weight: 600; font-size: 0.85rem;">${r.title}</div>
              <div class="gallery-card-time">${r.timestamp}</div>
            </div>
            <div class="gallery-card-actions">
              <a href="${r.url}" download="AirCanvas_${r.id}.png" class="btn-card-action">⬇️</a>
              <button class="btn-card-action btn-del" onclick="deleteArt(${r.id})">🗑️</button>
            </div>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    galleryGrid.innerHTML = '<p class="empty-gallery">Error loading gallery.</p>';
  }
});

window.deleteArt = async function(id) {
  await fetch(`/api/gallery/${id}`, { method: 'DELETE' });
  const card = document.querySelector(`.gallery-card[data-id="${id}"]`);
  if (card) card.remove();
  showVoiceToast('Deleted artwork.');
};

btnCloseGallery.addEventListener('click', () => {
  galleryModal.style.display = 'none';
});

// --- Initialize MediaPipe Hands & Camera ---
async function startCamera() {
  const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
  });

  hands.setOptions({
    maxNumHands: 1,
    modelComplexity: 1,
    minDetectionConfidence: 0.7,
    minTrackingConfidence: 0.7
  });

  hands.onResults(onResults);

  const camera = new Camera(videoElem, {
    onFrame: async () => {
      await hands.send({ image: videoElem });
    },
    width: 640,
    height: 480
  });

  camera.start();
  showVoiceToast("✨ AirCanvas AI Ready! Show your hand to start drawing.");
}

window.addEventListener('DOMContentLoaded', () => {
  startCamera();
  initVoiceCommands();
});
