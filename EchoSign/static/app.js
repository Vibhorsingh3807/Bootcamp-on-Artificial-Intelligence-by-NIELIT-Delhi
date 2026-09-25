/* ==========================================================================
   EchoSign AI — Frontend Application Logic
   ========================================================================== */

// --- Global State ---
const state = {
  activeTab: 'tab-sign-to-voice',
  cameraRunning: true,
  cameraMirrored: true,
  webcamStream: null,
  handsDetector: null,
  cameraController: null,
  isHandPresent: false,
  fps: 60,
  lastFrameTime: performance.now(),
  
  recognitionMode: 'words', // 'words' or 'alphabet'
  activeSignBuffer: [],
  currentGesture: '—',
  currentConfidence: 0.0,
  stableGesture: '—',
  gestureHoldTimer: null,
  lastAddedSign: null,
  consecutiveFrames: 0,
  candidateSign: null,

  // TTS
  speechVoices: [],
  selectedVoice: null,
  autoSpeak: true,
  isSpeaking: false,

  // Voice recognition
  speechRecognizer: null,
  isListening: false,

  // Trainer
  dictionary: {},
  currentPracticeIndex: 0,
  signKeys: [],

  // SOS
  sosActive: false
};

// --- Procedural SVG Sign Icons Dictionary ---
// Har sign ke liye crisp vector illustrations
const SIGN_SVGS = {
  "NAMASTE": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #f59e0b;">
      <path d="M26 44V18a3 3 0 0 1 6 0v26" fill="#f59e0b" fill-opacity="0.15" />
      <path d="M38 44V18a3 3 0 0 0-6 0v26" fill="#f59e0b" fill-opacity="0.15" />
      <path d="M20 46c0 6 5 10 12 10s12-4 12-10" />
      <circle cx="32" cy="12" r="3" fill="#f59e0b" />
      <path d="M32 18v26" stroke-width="2.5" />
    </svg>`,
  "HELLO": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #00f2fe;">
      <path d="M22 28V12a3 3 0 0 1 6 0v14" />
      <path d="M28 26V8a3 3 0 0 1 6 0v18" />
      <path d="M34 26V10a3 3 0 0 1 6 0v16" />
      <path d="M40 26V16a3 3 0 0 1 6 0v18c0 10-8 18-18 18s-16-6-16-14V26a3 3 0 0 1 6 0v8" />
      <path d="M12 24c2-4 6-6 10-6" stroke-dasharray="2 2" />
      <path d="M44 14c4 2 6 6 6 10" stroke-dasharray="2 2" />
    </svg>`,
  "THANK YOU": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #ec4899;">
      <path d="M18 36c4-12 12-16 28-16v12" />
      <path d="M16 46c10 4 22 2 32-4" />
      <path d="M42 22l6-4-2 8" fill="#ec4899" />
      <circle cx="32" cy="20" r="4" fill="#ec4899" fill-opacity="0.2" />
      <path d="M28 14l2 4 4-2" />
    </svg>`,
  "YES": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #10b981;">
      <path d="M24 38c0 8 4 14 12 14s12-6 12-14v-8c0-3-2-5-5-5h-8" />
      <path d="M24 38c-4 0-8-3-8-8s3-8 8-8c2 0 4-4 4-10a4 4 0 0 1 8 0v16" fill="#10b981" fill-opacity="0.2" />
      <path d="M42 16l4 4-4 4" />
      <path d="M46 20H36" stroke-dasharray="2 2" />
    </svg>`,
  "NO": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #f59e0b;">
      <path d="M20 24l16 16M36 24L20 40" stroke-width="3" stroke="#ef4444" />
      <path d="M22 30V18a3 3 0 0 1 6 0v10" />
      <path d="M28 28V16a3 3 0 0 1 6 0v12" />
      <path d="M34 32c2 4 6 6 12 6" />
    </svg>`,
  "PLEASE": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #ec4899;">
      <path d="M20 32c0-8 6-14 14-14s14 6 14 14-6 14-14 14" stroke-dasharray="3 3" />
      <path d="M22 28V14a2.5 2.5 0 0 1 5 0v14" />
      <path d="M27 26V12a2.5 2.5 0 0 1 5 0v14" />
      <path d="M32 26V14a2.5 2.5 0 0 1 5 0v12" />
      <path d="M37 26V18a2.5 2.5 0 0 1 5 0v12" />
      <circle cx="32" cy="32" r="3" fill="#ec4899" />
    </svg>`,
  "WATER": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #38bdf8;">
      <path d="M20 34V14a3 3 0 0 1 6 0v18" />
      <path d="M28 32V10a3 3 0 0 1 6 0v22" />
      <path d="M36 32V16a3 3 0 0 1 6 0v18" />
      <path d="M44 42c0 6-5 10-12 10s-14-4-14-12" />
      <path d="M48 20c0 4-4 8-4 8s-4-4-4-8a4 4 0 0 1 8 0z" fill="#38bdf8" />
    </svg>`,
  "FOOD": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #f97316;">
      <circle cx="32" cy="32" r="18" fill="#f97316" fill-opacity="0.1" />
      <path d="M24 20v24M20 20h8M40 20v24M36 20c0 4 8 4 8 0" stroke-width="2" />
      <circle cx="32" cy="22" r="3" fill="#f97316" />
    </svg>`,
  "PAIN": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #dc2626;">
      <path d="M14 32h10l4-8 6 16 6-12 4 6h8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
      <circle cx="32" cy="32" r="24" stroke="#dc2626" stroke-dasharray="3 3" />
      <path d="M32 10v4M32 50v4M10 32h4M50 32h4" />
    </svg>`,
  "DOCTOR": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #3b82f6;">
      <circle cx="32" cy="32" r="22" fill="#3b82f6" fill-opacity="0.1" />
      <path d="M32 20v24M20 32h24" stroke-width="4.5" stroke-linecap="round" stroke="#3b82f6" />
    </svg>`,
  "PEACE": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #a855f7;">
      <path d="M24 38V16a3 3 0 0 1 6 0v16" />
      <path d="M32 32V14a3 3 0 0 1 6 0v18" />
      <path d="M22 38c0 8 5 14 14 14s12-6 12-14v-8c0-3-2-5-5-5H34" />
      <path d="M18 16c2-4 8-6 14-4" stroke-dasharray="2 2" />
    </svg>`,
  "I LOVE YOU": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #ec4899;">
      <path d="M20 36V14a3 3 0 0 1 6 0v18" />
      <path d="M42 34V18a3 3 0 0 1 6 0v18" />
      <path d="M22 38c-4 0-8-3-8-8s3-8 8-8c2 0 4-4 4-10a4 4 0 0 1 8 0" />
      <path d="M22 42c0 6 6 10 14 10s14-5 14-14V34" />
      <path d="M32 20c-3-3-8-2-8 3 0 4 8 9 8 9s8-5 8-9c0-5-5-6-8-3z" fill="#ec4899" />
    </svg>`,
  "OK": `
    <svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" class="sign-card-svg" style="stroke: #10b981;">
      <circle cx="26" cy="26" r="10" stroke-width="2.5" fill="#10b981" fill-opacity="0.15" />
      <path d="M36 28V12a2.5 2.5 0 0 1 5 0v16" />
      <path d="M41 28V14a2.5 2.5 0 0 1 5 0v14" />
      <path d="M46 28V18a2.5 2.5 0 0 1 5 0v14c0 8-6 14-16 14s-14-6-14-14" />
    </svg>`
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initVoices();
  initSpeechRecognition();
  initCamera();
  initBufferControls();
  loadDictionary();
  loadAnalytics();

  // Polling / auto-refresh stats every 15s
  setInterval(() => {
    if (state.activeTab === 'tab-history') {
      loadAnalytics();
    }
  }, 15000);
});

// --- Tab Switching ---
function initTabs() {
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      const targetId = tab.getAttribute('data-tab');
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        targetEl.classList.add('active');
      }
      state.activeTab = targetId;

      if (targetId === 'tab-history') {
        loadAnalytics();
      }
    });
  });
}

// --- Text-to-Speech (TTS) Engine ---
function initVoices() {
  const voiceSelect = document.getElementById('voiceSelect');
  const toggleAuto = document.getElementById('toggleAutoSpeak');
  const btnSpeak = document.getElementById('btnSpeakNow');

  toggleAuto.addEventListener('change', (e) => {
    state.autoSpeak = e.target.checked;
  });

  btnSpeak.addEventListener('click', () => {
    const text = document.getElementById('reconstructedSentence').innerText;
    speakText(text);
  });

  function populateVoiceList() {
    if (!('speechSynthesis' in window)) return;
    state.speechVoices = window.speechSynthesis.getVoices();
    voiceSelect.innerHTML = '';
    
    state.speechVoices.forEach((v, idx) => {
      const opt = document.createElement('option');
      opt.value = idx;
      opt.textContent = `${v.name} (${v.lang})${v.default ? ' [Default]' : ''}`;
      voiceSelect.appendChild(opt);
    });

    // Prefer smooth English voices (Google US English, Samantha, Natural)
    const naturalVoiceIdx = state.speechVoices.findIndex(v => 
      v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('Female'))
    );
    if (naturalVoiceIdx !== -1) {
      voiceSelect.selectedIndex = naturalVoiceIdx;
      state.selectedVoice = state.speechVoices[naturalVoiceIdx];
    } else if (state.speechVoices.length > 0) {
      state.selectedVoice = state.speechVoices[0];
    }
  }

  populateVoiceList();
  if ('speechSynthesis' in window && window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = populateVoiceList;
  }

  voiceSelect.addEventListener('change', () => {
    state.selectedVoice = state.speechVoices[voiceSelect.value];
  });
}

function speakText(text) {
  if (!('speechSynthesis' in window) || !text) return;
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  if (state.selectedVoice) {
    utterance.voice = state.selectedVoice;
  }
  const speed = parseFloat(document.getElementById('voiceRate').value) || 1.0;
  utterance.rate = speed;
  utterance.pitch = 1.0;

  const visualizer = document.getElementById('audioVisualizer');
  utterance.onstart = () => {
    state.isSpeaking = true;
    visualizer.classList.add('playing');
  };
  utterance.onend = () => {
    state.isSpeaking = false;
    visualizer.classList.remove('playing');
  };
  utterance.onerror = () => {
    state.isSpeaking = false;
    visualizer.classList.remove('playing');
  };

  window.speechSynthesis.speak(utterance);
}

// --- Speech Recognition (Voice ➔ Sign) ---
function initSpeechRecognition() {
  const btnMic = document.getElementById('btnToggleMic');
  const micHalo = document.getElementById('micHalo');
  const micStatusTag = document.getElementById('micStatusTag');
  const liveTranscription = document.getElementById('liveTranscription');
  const manualInput = document.getElementById('manualTextInput');
  const btnTranslate = document.getElementById('btnTranslateText');

  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRec) {
    micStatusTag.textContent = 'Web Speech not supported (use text box)';
    btnMic.disabled = true;
    btnMic.style.opacity = '0.5';
  } else {
    state.speechRecognizer = new SpeechRec();
    state.speechRecognizer.continuous = true;
    state.speechRecognizer.interimResults = true;
    state.speechRecognizer.lang = 'en-US';

    state.speechRecognizer.onstart = () => {
      state.isListening = true;
      micHalo.classList.add('active');
      micStatusTag.textContent = 'Listening Live...';
      micStatusTag.classList.add('listening');
    };

    state.speechRecognizer.onend = () => {
      state.isListening = false;
      micHalo.classList.remove('active');
      micStatusTag.textContent = 'Ready to Listen';
      micStatusTag.classList.remove('listening');
    };

    state.speechRecognizer.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      const activeText = finalTranscript || interimTranscript;
      liveTranscription.textContent = activeText;

      if (finalTranscript.trim().length > 0) {
        fetchTextToSigns(finalTranscript.trim());
      }
    };

    state.speechRecognizer.onerror = (e) => {
      console.warn('Speech recognition error:', e.error);
    };

    btnMic.addEventListener('click', () => {
      if (state.isListening) {
        state.speechRecognizer.stop();
      } else {
        liveTranscription.textContent = 'Listening for speech...';
        state.speechRecognizer.start();
      }
    });
  }

  btnTranslate.addEventListener('click', () => {
    const text = manualInput.value.trim();
    if (text) {
      liveTranscription.textContent = text;
      fetchTextToSigns(text);
      manualInput.value = '';
    }
  });

  manualInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      btnTranslate.click();
    }
  });
}

async function fetchTextToSigns(text) {
  try {
    const resp = await fetch('/api/text_to_signs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text, auto_log: true })
    });
    const data = await resp.json();
    renderVisualSignStream(data.signs);
  } catch (err) {
    console.error('Error in text to signs:', err);
  }
}

function renderVisualSignStream(signs) {
  const container = document.getElementById('visualSignStream');
  const countBadge = document.getElementById('signCountBadge');

  if (!signs || signs.length === 0) {
    countBadge.textContent = '0 Signs Detected';
    container.innerHTML = `
      <div class="empty-signs-state">
        <div class="empty-icon">🤷</div>
        <p>No direct sign words found in the sentence. Try words like "Hello", "Water", "Food", "Help", "Doctor", "Thanks", etc.</p>
      </div>`;
    return;
  }

  countBadge.textContent = `${signs.length} Sign${signs.length > 1 ? 's' : ''} Rendered`;
  container.innerHTML = '';

  signs.forEach(s => {
    const card = document.createElement('div');
    card.className = 'sign-card';
    const svgIcon = SIGN_SVGS[s.id] || `<div style="font-size: 2rem;">🤟</div>`;
    card.innerHTML = `
      <span class="sign-card-badge">${s.category}</span>
      <div class="sign-card-svg-wrap">
        ${svgIcon}
      </div>
      <div class="sign-card-title">${s.label}</div>
      <div class="sign-card-desc">${s.description}</div>
    `;
    container.appendChild(card);
  });
}

// --- Computer Vision & MediaPipe Hands Integration ---
function initCamera() {
  const video = document.getElementById('webcamVideo');
  state.videoElement = video;
  const canvas = document.getElementById('landmarkCanvas');
  const ctx = canvas.getContext('2d');
  const btnToggleCam = document.getElementById('btnToggleCam');
  const btnFlipCam = document.getElementById('btnFlipCam');
  const camStatusDot = document.getElementById('camStatusDot');

  const btnToggleMode = document.getElementById('btnToggleMode');
  if (btnToggleMode) {
    btnToggleMode.addEventListener('click', () => {
      state.recognitionMode = state.recognitionMode === 'words' ? 'alphabet' : 'words';
      const isAlpha = state.recognitionMode === 'alphabet';
      document.getElementById('modeLabel').textContent = isAlpha ? 'ASL Alphabet (RTX 4060)' : 'Words Mode';
      document.getElementById('modeIcon').textContent = isAlpha ? '⚡' : '🔤';
      const spotLabel = document.querySelector('.spotlight-label');
      if (spotLabel) spotLabel.textContent = isAlpha ? 'ASL ALPHABET (RTX 4060 GPU)' : 'DETECTED SIGN';
    });
  }

  // Toggle Camera
  btnToggleCam.addEventListener('click', () => {
    state.cameraRunning = !state.cameraRunning;
    if (state.cameraRunning) {
      if (state.cameraController) state.cameraController.start();
      btnToggleCam.innerHTML = `<span>📹</span><span>Stop Cam</span>`;
      camStatusDot.style.background = 'var(--accent-emerald)';
    } else {
      if (state.cameraController) state.cameraController.stop();
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      btnToggleCam.innerHTML = `<span>▶️</span><span>Start Cam</span>`;
      camStatusDot.style.background = 'var(--text-dim)';
    }
  });

  btnFlipCam.addEventListener('click', () => {
    state.cameraMirrored = !state.cameraMirrored;
    video.style.transform = state.cameraMirrored ? 'scaleX(-1)' : 'scaleX(1)';
    canvas.style.transform = state.cameraMirrored ? 'scaleX(-1)' : 'scaleX(1)';
  });

  // MediaPipe Hands + Pose initialization for full body-anchored gesture recognition
  let poseDetector = null;
  let currentBodyAnchors = null;
  let frameCounter = 0;

  function onPoseResults(results) {
    if (results.poseLandmarks && results.poseLandmarks.length >= 13) {
      const lm = results.poseLandmarks;
      const nose = lm[0];
      const mouth = {
        x: (lm[9].x + lm[10].x) / 2,
        y: (lm[9].y + lm[10].y) / 2,
        z: (lm[9].z + lm[10].z) / 2
      };
      const leftShoulder = lm[11];
      const rightShoulder = lm[12];
      const chest = {
        x: (leftShoulder.x + rightShoulder.x) / 2,
        y: (leftShoulder.y + rightShoulder.y) / 2 + 0.08,
        z: (leftShoulder.z + rightShoulder.z) / 2
      };
      const neck = {
        x: (leftShoulder.x + rightShoulder.x) / 2,
        y: (mouth.y + (leftShoulder.y + rightShoulder.y) / 2) / 2,
        z: (leftShoulder.z + rightShoulder.z) / 2
      };

      currentBodyAnchors = {
        nose: [nose.x, nose.y, nose.z || 0.0],
        mouth: [mouth.x, mouth.y, mouth.z || 0.0],
        left_shoulder: [leftShoulder.x, leftShoulder.y, leftShoulder.z || 0.0],
        right_shoulder: [rightShoulder.x, rightShoulder.y, rightShoulder.z || 0.0],
        chest: [chest.x, chest.y, chest.z || 0.0],
        neck: [neck.x, neck.y, neck.z || 0.0]
      };

      const anchorBadge = document.getElementById('bodyAnchorBadge');
      if (anchorBadge) {
        anchorBadge.textContent = '🎯 Body Anchors: Active (Chest, Lips, Head)';
        anchorBadge.classList.add('active');
      }
    }
  }

  if (typeof Hands !== 'undefined' && typeof Camera !== 'undefined') {
    const hands = new Hands({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
    });

    hands.setOptions({
      maxNumHands: 2, // Dono haath track honge (Namaste etc.)
      modelComplexity: 1,
      minDetectionConfidence: 0.65,
      minTrackingConfidence: 0.65
    });

    // Initialize MediaPipe Pose if available for Chest, Lips, Neck, Head tracking
    if (typeof Pose !== 'undefined') {
      try {
        poseDetector = new Pose({
          locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
        });
        poseDetector.setOptions({
          modelComplexity: 0, // Lite model for extreme 60FPS smoothness
          smoothLandmarks: true,
          enableSegmentation: false,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5
        });
        poseDetector.onResults(onPoseResults);
      } catch (e) {
        console.warn('Pose init notice:', e);
      }
    }

    hands.onResults((results) => {
      onHandsResults(results, canvas, ctx, currentBodyAnchors);
    });

    const camera = new Camera(video, {
      onFrame: async () => {
        if (state.cameraRunning) {
          frameCounter++;
          await hands.send({ image: video });
          // Update body pose every 2nd frame for maximum 60FPS fluid rendering
          if (poseDetector && frameCounter % 2 === 0) {
            try {
              await poseDetector.send({ image: video });
            } catch (err) {
              // frame drop tolerance
            }
          }
        }
      },
      width: 640,
      height: 480
    });

    camera.start().catch((err) => {
      console.warn('Camera start error:', err);
      setupMockSimulator(canvas, ctx);
    });

    state.handsDetector = hands;
    state.cameraController = camera;
  } else {
    console.warn('MediaPipe library not loaded from CDN, setting up simulator mode.');
    setupMockSimulator(canvas, ctx);
  }
}

// Draw body anchors and proximity feedback on the canvas HUD
function drawBodyAnchors(ctx, w, h, handLandmarks, bodyAnchors) {
  if (!bodyAnchors) return;

  const chest = bodyAnchors.chest;
  const mouth = bodyAnchors.mouth;
  const nose = bodyAnchors.nose;
  const leftSh = bodyAnchors.left_shoulder;
  const rightSh = bodyAnchors.right_shoulder;
  const neck = bodyAnchors.neck;

  const chestX = chest[0] * w;
  const chestY = chest[1] * h;
  const mouthX = mouth[0] * w;
  const mouthY = mouth[1] * h;
  const leftShX = leftSh[0] * w;
  const leftShY = leftSh[1] * h;
  const rightShX = rightSh[0] * w;
  const rightShY = rightSh[1] * h;
  const neckX = neck[0] * w;
  const neckY = neck[1] * h;

  ctx.save();

  // 1. Draw subtle torso guide lines
  ctx.strokeStyle = 'rgba(168, 85, 247, 0.35)';
  ctx.lineWidth = 2;
  ctx.setLineDash([4, 4]);

  ctx.beginPath();
  ctx.moveTo(leftShX, leftShY);
  ctx.lineTo(rightShX, rightShY);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(neckX, neckY);
  ctx.lineTo(chestX, chestY);
  ctx.stroke();
  ctx.setLineDash([]);

  // Check proximity to hand
  let isHandOnChest = false;
  let isHandOnLips = false;

  if (handLandmarks && handLandmarks.length === 21) {
    const wrist = handLandmarks[0];
    const indexTip = handLandmarks[8];
    const middleTip = handLandmarks[12];
    const palmX = (wrist.x + handLandmarks[9].x) / 2;
    const palmY = (wrist.y + handLandmarks[9].y) / 2;

    const dPalmChest = Math.hypot(palmX - chest[0], palmY - chest[1]);
    const dWristChest = Math.hypot(wrist.x - chest[0], wrist.y - chest[1]);
    if (Math.min(dPalmChest, dWristChest) < 0.24) {
      isHandOnChest = true;
    }

    const dIndexMouth = Math.hypot(indexTip.x - mouth[0], indexTip.y - mouth[1]);
    const dMidMouth = Math.hypot(middleTip.x - mouth[0], middleTip.y - mouth[1]);
    if (Math.min(dIndexMouth, dMidMouth) < 0.18) {
      isHandOnLips = true;
    }
  }

  // 2. Chest Target Anchor
  ctx.beginPath();
  ctx.arc(chestX, chestY, isHandOnChest ? 26 : 16, 0, 2 * Math.PI);
  ctx.strokeStyle = isHandOnChest ? '#00f2fe' : 'rgba(168, 85, 247, 0.55)';
  ctx.lineWidth = isHandOnChest ? 3.5 : 1.5;
  ctx.shadowColor = isHandOnChest ? '#00f2fe' : '#a855f7';
  ctx.shadowBlur = isHandOnChest ? 16 : 8;
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(chestX, chestY, isHandOnChest ? 6 : 3, 0, 2 * Math.PI);
  ctx.fillStyle = isHandOnChest ? '#ffffff' : '#c084fc';
  ctx.fill();

  if (isHandOnChest) {
    ctx.font = '600 12px "Space Grotesk", monospace';
    ctx.fillStyle = '#00f2fe';
    ctx.shadowBlur = 12;
    ctx.fillText('✨ CHEST CONTACT (PLEASE)', chestX + 32, chestY + 5);
  }

  // 3. Lips / Mouth Target Anchor
  ctx.beginPath();
  ctx.arc(mouthX, mouthY, isHandOnLips ? 22 : 13, 0, 2 * Math.PI);
  ctx.strokeStyle = isHandOnLips ? '#f59e0b' : 'rgba(236, 72, 153, 0.5)';
  ctx.lineWidth = isHandOnLips ? 3.5 : 1.5;
  ctx.shadowColor = isHandOnLips ? '#f59e0b' : '#ec4899';
  ctx.shadowBlur = isHandOnLips ? 16 : 8;
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(mouthX, mouthY, isHandOnLips ? 5 : 3, 0, 2 * Math.PI);
  ctx.fillStyle = isHandOnLips ? '#ffffff' : '#f472b6';
  ctx.fill();

  if (isHandOnLips) {
    ctx.font = '600 12px "Space Grotesk", monospace';
    ctx.fillStyle = '#f59e0b';
    ctx.shadowBlur = 12;
    ctx.fillText('✨ LIPS TOUCHED (WATER / FOOD / THANK YOU)', mouthX + 28, mouthY + 5);
  }

  ctx.restore();
}

// MediaPipe Results Callback
function onHandsResults(results, canvas, ctx, bodyAnchors = null) {
  // Update canvas size
  canvas.width = results.image.width || 640;
  canvas.height = results.image.height || 480;

  // Compute FPS
  const now = performance.now();
  const delta = (now - state.lastFrameTime) / 1000;
  state.lastFrameTime = now;
  if (delta > 0) {
    state.fps = Math.round(1 / delta);
    document.getElementById('fpsDisplay').textContent = `${state.fps} FPS`;
  }

  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const handStateBadge = document.getElementById('handStateBadge');
  const numHands = results.multiHandLandmarks ? results.multiHandLandmarks.length : 0;
  const raw1 = (numHands > 0) ? results.multiHandLandmarks[0] : null;

  // Render upper body anchors (Lips, Chest, Shoulders, Neck)
  drawBodyAnchors(ctx, canvas.width, canvas.height, raw1, bodyAnchors);

  if (numHands > 0) {
    state.isHandPresent = true;
    handStateBadge.textContent = numHands > 1 ? 'Both Hands Detected (Dual-Hand Mode)' : '1 Hand Detected';
    handStateBadge.classList.add('active');

    // 1st Hand skeleton (Cyan color)
    drawLandmarkSkeleton(ctx, raw1, canvas.width, canvas.height, '#00f2fe');

    // 2nd Hand skeleton (Emerald Green color) agar doosra haath bhi dikh raha hai
    let raw2 = null;
    if (numHands > 1) {
      raw2 = results.multiHandLandmarks[1];
      drawLandmarkSkeleton(ctx, raw2, canvas.width, canvas.height, '#10b981');
    }

    if (state.recognitionMode === 'alphabet') {
      const activeVideo = state.videoElement || document.getElementById('webcamVideo');
      sendFrameToAslGpu(activeVideo, raw1);
    } else {
      const formatted1 = raw1.map(p => [p.x, p.y, p.z || 0.0]);
      const formatted2 = raw2 ? raw2.map(p => [p.x, p.y, p.z || 0.0]) : null;
      sendLandmarksToBackend(formatted1, formatted2, bodyAnchors);
    }
  } else {
    state.isHandPresent = false;
    state.lastAddedSign = null;
    state.candidateSign = null;
    state.consecutiveFrames = 0;
    handStateBadge.textContent = 'Searching Hand...';
    handStateBadge.classList.remove('active');
    updateSpotlight('—', 0.0);
  }

  ctx.restore();
}

// Draw futuristic neon skeleton overlay on hand
function drawLandmarkSkeleton(ctx, landmarks, w, h, neonColor = '#00f2fe') {
  const connections = [
    [0, 1], [1, 2], [2, 3], [3, 4],       // thumb
    [0, 5], [5, 6], [6, 7], [7, 8],       // index
    [5, 9], [9, 10], [10, 11], [11, 12],  // middle
    [9, 13], [13, 14], [14, 15], [15, 16],// ring
    [13, 17], [17, 18], [18, 19], [19, 20],// pinky
    [0, 17]                               // palm base
  ];

  // Draw lines
  ctx.strokeStyle = neonColor;
  ctx.lineWidth = 3;
  ctx.lineCap = 'round';
  ctx.shadowColor = neonColor;
  ctx.shadowBlur = 10;

  connections.forEach(([i, j]) => {
    const p1 = landmarks[i];
    const p2 = landmarks[j];
    ctx.beginPath();
    ctx.moveTo(p1.x * w, p1.y * h);
    ctx.lineTo(p2.x * w, p2.y * h);
    ctx.stroke();
  });

  // Draw glowing joint points
  landmarks.forEach((p, idx) => {
    ctx.beginPath();
    const r = [4, 8, 12, 16, 20].includes(idx) ? 6 : 4;
    ctx.arc(p.x * w, p.y * h, r, 0, 2 * Math.PI);
    ctx.fillStyle = [4, 8, 12, 16, 20].includes(idx) ? '#ffffff' : neonColor;
    ctx.shadowColor = neonColor;
    ctx.shadowBlur = 12;
    ctx.fill();
  });
}

// Send cropped hand image to PyTorch RTX 4060 GPU endpoint
let isPredictingGpu = false;
const offscreenCanvas = document.createElement('canvas');
offscreenCanvas.width = 128;
offscreenCanvas.height = 128;
const offCtx = offscreenCanvas.getContext('2d');

async function sendFrameToAslGpu(video, rawLandmarks) {
  if (isPredictingGpu) return;
  isPredictingGpu = true;

  try {
    const formattedLandmarks = rawLandmarks.map(p => [p.x, p.y, p.z || 0.0]);
    let b64 = "";

    const activeVideo = video || state.videoElement || document.getElementById('webcamVideo');
    if (activeVideo && activeVideo.readyState >= 2) {
      const vw = activeVideo.videoWidth || 640;
      const vh = activeVideo.videoHeight || 480;

      let minX = Math.min(...rawLandmarks.map(p => p.x));
      let maxX = Math.max(...rawLandmarks.map(p => p.x));
      let minY = Math.min(...rawLandmarks.map(p => p.y));
      let maxY = Math.max(...rawLandmarks.map(p => p.y));

      const pad = 0.08;
      minX = Math.max(0, minX - pad) * vw;
      maxX = Math.min(1, maxX + pad) * vw;
      minY = Math.max(0, minY - pad) * vh;
      maxY = Math.min(1, maxY + pad) * vh;
      const boxW = Math.max(10, maxX - minX);
      const boxH = Math.max(10, maxY - minY);

      offCtx.drawImage(activeVideo, minX, minY, boxW, boxH, 0, 0, 128, 128);
      b64 = offscreenCanvas.toDataURL('image/jpeg', 0.85);
    }

    const resp = await fetch('/api/predict_asl_image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image_base64: b64,
        landmarks: formattedLandmarks
      })
    });
    const data = await resp.json();

    const letter = data.prediction || '—';
    const conf = data.confidence || 0.0;

    updateSpotlight(`Letter: ${letter}`, conf);
    processGestureStream(letter, conf);

    if (state.activeTab === 'tab-trainer') {
      updatePracticeScore(letter, conf);
    }
  } catch (err) {
    console.error('Error in ASL Alphabet prediction:', err);
  } finally {
    isPredictingGpu = false;
  }
}

// Send landmarks to FastAPI server for high-speed ML classification
let isPredicting = false;
async function sendLandmarksToBackend(landmarks, secondary_landmarks = null, body_landmarks = null) {
  if (isPredicting) return;
  isPredicting = true;

  try {
    const resp = await fetch('/api/predict_landmarks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        landmarks: landmarks,
        secondary_landmarks: secondary_landmarks,
        body_landmarks: body_landmarks
      })
    });
    const data = await resp.json();

    const gesture = data.stable_gesture || data.gesture;
    const confidence = data.confidence || 0.0;

    updateSpotlight(gesture, confidence);
    processGestureStream(gesture, confidence);

    // Update Practice Mode if active
    if (state.activeTab === 'tab-trainer') {
      updatePracticeScore(gesture, confidence);
    }
  } catch (err) {
    console.error('Error predicting landmarks:', err);
  } finally {
    isPredicting = false;
  }
}

// Update HUD spotlight element
function updateSpotlight(gestureName, confidence) {
  const spotlightEl = document.getElementById('currentGestureName');
  const barEl = document.getElementById('confidenceBar');
  const textEl = document.getElementById('confidenceText');

  state.currentGesture = gestureName;
  state.currentConfidence = confidence;

  spotlightEl.textContent = gestureName;
  const pct = Math.round(confidence * 100);
  barEl.style.width = `${pct}%`;
  textEl.textContent = `Confidence: ${pct}%`;
}

// De-jittered sign buffer logic: requires sustained detection before registering
function processGestureStream(gesture, confidence) {
  if (!gesture || gesture === 'NO_HAND' || gesture === 'nothing' || gesture === '—' || confidence < 0.60) {
    state.consecutiveFrames = 0;
    return;
  }

  // Handle DEL / Backspace token
  if (gesture.toLowerCase() === 'del' || gesture.toLowerCase() === 'delete') {
    if (state.candidateSign === gesture) {
      state.consecutiveFrames++;
      if (state.consecutiveFrames === 3) {
        if (state.activeSignBuffer.length > 0) {
          state.activeSignBuffer.pop();
          state.lastAddedSign = null;
          renderSignChips();
          synthesizeSentence();
        }
      }
    } else {
      state.candidateSign = gesture;
      state.consecutiveFrames = 1;
    }
    return;
  }

  // Handle SPACE token
  if (gesture.toLowerCase() === 'space') {
    if (state.candidateSign === gesture) {
      state.consecutiveFrames++;
      if (state.consecutiveFrames === 3) {
        if (state.lastAddedSign !== ' ') {
          addSignToBuffer(' ');
          state.lastAddedSign = ' ';
        }
      }
    } else {
      state.candidateSign = gesture;
      state.consecutiveFrames = 1;
    }
    return;
  }

  let cleanGesture = gesture;
  if (cleanGesture.startsWith('Letter: ')) {
    cleanGesture = cleanGesture.replace('Letter: ', '').trim();
  }

  if (cleanGesture === state.candidateSign) {
    state.consecutiveFrames++;
    // If held stable for 3 frames (~200ms)
    if (state.consecutiveFrames === 3) {
      if (state.lastAddedSign !== cleanGesture) {
        addSignToBuffer(cleanGesture);
        state.lastAddedSign = cleanGesture;
      }
    }
  } else {
    state.candidateSign = cleanGesture;
    state.consecutiveFrames = 1;
  }
}

function addSignToBuffer(signName) {
  state.activeSignBuffer.push(signName);
  renderSignChips();
  // Automatically trigger NLP sentence refinement after adding sign
  synthesizeSentence();
}

function renderSignChips() {
  const container = document.getElementById('signChipsContainer');
  if (state.activeSignBuffer.length === 0) {
    container.innerHTML = `<span class="placeholder-chip">Perform gestures or fingerspell to build sentence...</span>`;
    return;
  }

  container.innerHTML = '';
  state.activeSignBuffer.forEach((sign, idx) => {
    const chip = document.createElement('span');
    chip.className = 'sign-chip';
    const displaySign = sign === ' ' ? '␣ SPACE' : sign;
    chip.innerHTML = `${displaySign} <span style="cursor: pointer; opacity: 0.6; margin-left: 4px;" onclick="removeSignChip(${idx})">&times;</span>`;
    container.appendChild(chip);
  });
}

window.removeSignChip = function(index) {
  state.activeSignBuffer.splice(index, 1);
  renderSignChips();
  synthesizeSentence();
};

function initBufferControls() {
  document.getElementById('btnClearBuffer').addEventListener('click', () => {
    state.activeSignBuffer = [];
    state.lastAddedSign = null;
    renderSignChips();
    document.getElementById('reconstructedSentence').textContent = 
      '"Perform signs in front of the camera. The AI will smooth them into coherent, empathetic speech."';
    updateSentimentWidget('Neutral', 'NORMAL', 0.05);
  });

  document.getElementById('btnRefineSentence').addEventListener('click', () => {
    synthesizeSentence();
  });
}

// Call backend NLP smoothing engine
async function synthesizeSentence() {
  if (state.activeSignBuffer.length === 0) return;

  try {
    const resp = await fetch('/api/nlp_refine', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        signs: state.activeSignBuffer,
        auto_log: true
      })
    });
    const data = await resp.json();

    const sentenceBox = document.getElementById('reconstructedSentence');
    sentenceBox.textContent = `"${data.sentence}"`;
    sentenceBox.classList.add('highlight');
    setTimeout(() => sentenceBox.classList.remove('highlight'), 800);

    updateSentimentWidget(data.sentiment, data.urgency, data.urgency_score);

    // Speak out loud if Auto-Speak is enabled
    if (state.autoSpeak && data.sentence) {
      let speechText = data.sentence;
      // If it's a fingerspelled name, speak the clean name directly
      if (speechText.includes("Fingerspelled Name: ")) {
        speechText = speechText.replace("Fingerspelled Name: ", "").replace("!", "").trim();
      }
      speakText(speechText);
    }
  } catch (err) {
    console.error('Error synthesizing sentence:', err);
  }
}

function updateSentimentWidget(sentiment, urgency, score) {
  document.getElementById('sentimentValue').textContent = sentiment;
  const pill = document.getElementById('urgencyPill');
  pill.textContent = urgency;
  pill.className = `urgency-pill ${urgency.toLowerCase()}`;
  document.getElementById('urgencyScoreVal').textContent = score.toFixed(2);
}

// --- Interactive Dictionary & Sign Studio ---
async function loadDictionary() {
  try {
    const resp = await fetch('/api/dictionary');
    const data = await resp.json();
    state.dictionary = data.signs;
    state.signKeys = Object.keys(data.signs);

    renderDictionaryGrid('ALL');
    setupCategoryFilters();
    setupPracticeControls();
    updatePracticeCard();
  } catch (err) {
    console.error('Error loading dictionary:', err);
  }
}

function renderDictionaryGrid(categoryFilter) {
  const grid = document.getElementById('dictionaryGrid');
  grid.innerHTML = '';

  state.signKeys.forEach((key, idx) => {
    const sign = state.dictionary[key];
    if (categoryFilter !== 'ALL' && sign.category !== categoryFilter) return;

    const card = document.createElement('div');
    card.className = `dict-card ${idx === state.currentPracticeIndex ? 'selected' : ''}`;
    card.innerHTML = `
      <div class="dict-header">
        <span class="dict-sign-title">${sign.label}</span>
        <span class="dict-category-tag">${sign.category}</span>
      </div>
      <div class="dict-desc">${sign.description}</div>
    `;

    card.addEventListener('click', () => {
      state.currentPracticeIndex = idx;
      updatePracticeCard();
      document.querySelectorAll('.dict-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    });

    grid.appendChild(card);
  });
}

function setupCategoryFilters() {
  const pills = document.querySelectorAll('.cat-pill');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      renderDictionaryGrid(pill.getAttribute('data-cat'));
    });
  });
}

function setupPracticeControls() {
  document.getElementById('btnPrevSign').addEventListener('click', () => {
    if (state.currentPracticeIndex > 0) {
      state.currentPracticeIndex--;
    } else {
      state.currentPracticeIndex = state.signKeys.length - 1;
    }
    updatePracticeCard();
  });

  document.getElementById('btnNextSign').addEventListener('click', () => {
    if (state.currentPracticeIndex < state.signKeys.length - 1) {
      state.currentPracticeIndex++;
    } else {
      state.currentPracticeIndex = 0;
    }
    updatePracticeCard();
  });
}

function updatePracticeCard() {
  if (state.signKeys.length === 0) return;
  const currentKey = state.signKeys[state.currentPracticeIndex];
  const signInfo = state.dictionary[currentKey];

  document.getElementById('targetSignBadge').textContent = `Target: ${signInfo.label}`;
  document.getElementById('guideTitle').textContent = `How to Sign "${signInfo.label}"`;
  document.getElementById('guideDesc').textContent = signInfo.description;
  document.getElementById('matchPercentage').textContent = '0%';
  document.getElementById('meterBarFill').style.width = '0%';
  document.getElementById('practiceFeedback').textContent = 'Position your hand in camera view to practice this sign!';
}

function updatePracticeScore(detectedGesture, confidence) {
  if (state.signKeys.length === 0) return;
  const targetSign = state.signKeys[state.currentPracticeIndex];

  const matchEl = document.getElementById('matchPercentage');
  const barEl = document.getElementById('meterBarFill');
  const feedbackEl = document.getElementById('practiceFeedback');

  if (detectedGesture === targetSign) {
    const pct = Math.min(100, Math.round(confidence * 100));
    matchEl.textContent = `${pct}% Match!`;
    matchEl.style.color = 'var(--accent-emerald)';
    barEl.style.width = `${pct}%`;
    feedbackEl.textContent = `🎯 Excellent! You are accurately signing "${targetSign}".`;
  } else {
    matchEl.textContent = `12%`;
    matchEl.style.color = 'var(--accent-rose)';
    barEl.style.width = `12%`;
    feedbackEl.textContent = `Currently performing: ${detectedGesture}. Try adjusting fingers to match "${targetSign}".`;
  }
}

// --- Analytics & SQLite Logs ---
async function loadAnalytics() {
  try {
    const [historyResp, analyticsResp] = await Promise.all([
      fetch('/api/history'),
      fetch('/api/analytics')
    ]);

    const historyData = await historyResp.json();
    const analyticsData = await analyticsResp.json();

    // Render Stats
    document.getElementById('statTotalConvs').textContent = analyticsData.total_conversations || 0;
    document.getElementById('statActiveEmergencies').textContent = analyticsData.active_emergencies || 0;

    // Render Conversation Table
    const convBody = document.getElementById('conversationTableBody');
    if (historyData.conversations && historyData.conversations.length > 0) {
      convBody.innerHTML = '';
      historyData.conversations.forEach(c => {
        const row = document.createElement('tr');
        const channelLabel = c.channel === 'sign_to_voice' ? '🤟 Sign ➔ Voice' : '🎙️ Voice ➔ Sign';
        row.innerHTML = `
          <td>${c.timestamp}</td>
          <td><strong>${channelLabel}</strong></td>
          <td>${c.input_raw}</td>
          <td>${c.output_text}</td>
          <td><span style="font-weight: 600;">${c.sentiment}</span></td>
          <td><span class="urgency-pill ${c.urgency.toLowerCase()}">${c.urgency}</span></td>
        `;
        convBody.appendChild(row);
      });
    }

    // Render SOS Table if present
    const sosBody = document.getElementById('sosTableBody');
    if (sosBody && historyData.emergencies && historyData.emergencies.length > 0) {
      sosBody.innerHTML = '';
      historyData.emergencies.forEach(s => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${s.timestamp}</td>
          <td>${s.trigger_type}</td>
          <td>${s.location}</td>
          <td><strong>${s.summary}</strong></td>
          <td><span class="badge-critical">${s.status}</span></td>
        `;
        sosBody.appendChild(row);
      });
    }
  } catch (err) {
    console.error('Error fetching analytics:', err);
  }
}

document.getElementById('btnRefreshHistory').addEventListener('click', () => {
  loadAnalytics();
});

// Fallback Simulator if browser camera permission is blocked or CDN is unreachable
function setupMockSimulator(canvas, ctx) {
  const handStateBadge = document.getElementById('handStateBadge');
  handStateBadge.textContent = 'Simulated Vision Active';
  handStateBadge.classList.add('active');

  let simIdx = 0;
  const signs = ['HELLO', 'PLEASE', 'PAIN', 'WATER', 'THANK YOU', 'YES', 'OK'];

  setInterval(() => {
    if (state.cameraRunning) {
      const g = signs[simIdx % signs.length];
      simIdx++;
      updateSpotlight(g, 0.94);
      processGestureStream(g, 0.94);
      if (state.activeTab === 'tab-trainer') {
        updatePracticeScore(g, 0.94);
      }
    }
  }, 4000);
}
