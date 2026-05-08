/* ═══════════════════════════════════════════
   ARIA — AI Interview Simulator
   Complete Frontend Logic
═══════════════════════════════════════════ */

// ── State ──
const STATE = {
  sessionId: null,
  candidateName: '',
  jobRole: '',
  resumeText: '',
  isInterviewActive: false,
  isRecording: false,
  questionCount: 0,
  timerInterval: null,
  elapsedSeconds: 0,
  transcript: [],
  emotionHistory: [],
  emotionSummary: {},
  feedbackHistory: [],
  scores: { overall: 0, confidence: 0, communication: 0, presence: 0, technical: 0 },
  webcamStream: null,
  emotionInterval: null,
  mediaRecorder: null,
  audioChunks: [],
  speechRecognition: null,
  isTyping: false
};

// ── Emotion Config ──
const EMOTION_COLORS = {
  happy: '#00ff88', neutral: '#00f5ff', sad: '#f472b6',
  angry: '#ef4444', nervous: '#f59e0b', fear: '#a855f7',
  surprised: '#22d3ee', disgust: '#6366f1', unknown: '#475569', confident: '#00ff88'
};

const EMOTION_ICONS = {
  happy: '😊', neutral: '😐', sad: '😔', angry: '😠',
  nervous: '😰', fear: '😨', surprised: '😲', disgust: '😒', unknown: '◉', confident: '💪'
};

// ═══════════════════════════
// PARTICLE BACKGROUND
// ═══════════════════════════
function initParticles() {
  const canvas = document.getElementById('particles-canvas');
  const ctx = canvas.getContext('2d');
  let particles = [];
  let animFrame;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.size = Math.random() * 1.5 + 0.2;
      this.speedX = (Math.random() - 0.5) * 0.3;
      this.speedY = (Math.random() - 0.5) * 0.3;
      this.opacity = Math.random() * 0.4 + 0.1;
      this.color = Math.random() > 0.6 ? '#00f5ff' : '#a855f7';
    }
    update() {
      this.x += this.speedX; this.y += this.speedY;
      if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) this.reset();
    }
    draw() {
      ctx.save();
      ctx.globalAlpha = this.opacity;
      ctx.fillStyle = this.color;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }

  function init() {
    particles = Array.from({ length: 120 }, () => new Particle());
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => { p.update(); p.draw(); });

    // Draw connections
    ctx.strokeStyle = 'rgba(0, 245, 255, 0.04)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 100) {
          ctx.globalAlpha = (1 - dist / 100) * 0.3;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }
    ctx.globalAlpha = 1;
    animFrame = requestAnimationFrame(animate);
  }

  window.addEventListener('resize', () => { resize(); init(); });
  resize(); init(); animate();
}

// ═══════════════════════════
// SCREEN MANAGEMENT
// ═══════════════════════════
function showScreen(screenId) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(screenId).classList.add('active');
}

// ═══════════════════════════
// SETUP SCREEN
// ═══════════════════════════
function initSetup() {
  const uploadZone = document.getElementById('upload-zone');
  const resumeFile = document.getElementById('resume-file');
  const launchBtn = document.getElementById('launch-btn');

  uploadZone.addEventListener('click', () => resumeFile.click());
  uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
  uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) handleResumeUpload(file);
  });

  resumeFile.addEventListener('change', (e) => {
    if (e.target.files[0]) handleResumeUpload(e.target.files[0]);
  });

  launchBtn.addEventListener('click', startInterview);
}

async function handleResumeUpload(file) {
  const status = document.getElementById('upload-status');
  status.textContent = `⏳ Processing ${file.name}...`;

  const formData = new FormData();
  formData.append('resume', file);

  try {
    const res = await fetch('/api/upload-resume', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.success && data.text) {
      STATE.resumeText = data.text;
      status.textContent = `✅ ${file.name} loaded (${data.text.length} chars)`;
    } else {
      status.textContent = `⚠️ Could not extract text — interview will proceed without it`;
    }
  } catch {
    status.textContent = `⚠️ Upload failed — continuing without resume`;
  }
}

async function startInterview() {
  const name = document.getElementById('candidate-name').value.trim();
  const role = document.getElementById('job-role').value;

  if (!name) { showToast('Please enter your name', 'error'); return; }
  if (!role) { showToast('Please select a job role', 'error'); return; }

  STATE.candidateName = name;
  STATE.jobRole = role;

  const btn = document.getElementById('launch-btn');
  btn.querySelector('.btn-text').textContent = 'INITIALIZING...';
  btn.disabled = true;

  try {
    // Start webcam
    await initWebcam();

    // Start interview session
    const res = await fetch('/api/start-interview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_role: role, candidate_name: name, resume_text: STATE.resumeText })
    });
    const data = await res.json();

    if (data.session_id) {
      STATE.sessionId = data.session_id;
      showScreen('interview-screen');
      initInterviewUI();
      startTimer();
      startEmotionDetection();
      initSpeechInput();

      // Add opening message
      setTimeout(() => {
        addMessage('assistant', data.message);
      }, 500);
    }
  } catch (e) {
    console.error('Start error:', e);
    showToast('Failed to start interview. Check console.', 'error');
    btn.querySelector('.btn-text').textContent = 'INITIALIZE INTERVIEW';
    btn.disabled = false;
  }
}

// ═══════════════════════════
// WEBCAM
// ═══════════════════════════
async function initWebcam() {
  try {
    STATE.webcamStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
      audio: false
    });
    document.getElementById('webcam-video').srcObject = STATE.webcamStream;
    return true;
  } catch (e) {
    console.warn('Webcam access denied:', e);
    showToast('Webcam not available — continuing without video analysis', 'info');
    return false;
  }
}

// ═══════════════════════════
// INTERVIEW UI
// ═══════════════════════════
function initInterviewUI() {
  STATE.isInterviewActive = true;

  // Update HUD
  document.getElementById('hud-name').textContent = STATE.candidateName.toUpperCase();
  document.getElementById('hud-role').textContent = STATE.jobRole.toUpperCase();

  // Clear welcome placeholder
  document.getElementById('chat-messages').innerHTML = '';

  // Button handlers
  document.getElementById('send-btn').addEventListener('click', sendMessage);
  document.getElementById('mic-btn').addEventListener('mousedown', startVoiceRecording);
  document.getElementById('mic-btn').addEventListener('mouseup', stopVoiceRecording);
  document.getElementById('mic-btn').addEventListener('touchstart', (e) => { e.preventDefault(); startVoiceRecording(); });
  document.getElementById('mic-btn').addEventListener('touchend', (e) => { e.preventDefault(); stopVoiceRecording(); });
  document.getElementById('end-interview-btn').addEventListener('click', endInterview);
  document.getElementById('user-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  // Score animation
  animateScore('overall-score', 0);
  animateScore('confidence-live', 0);
  animateScore('communication-score', 0);
  animateScore('presence-score', 0);
}

// ═══════════════════════════
// TIMER
// ═══════════════════════════
function startTimer() {
  STATE.timerInterval = setInterval(() => {
    STATE.elapsedSeconds++;
    const m = Math.floor(STATE.elapsedSeconds / 60).toString().padStart(2, '0');
    const s = (STATE.elapsedSeconds % 60).toString().padStart(2, '0');
    document.getElementById('timer').textContent = `${m}:${s}`;
  }, 1000);
}

// ═══════════════════════════
// CHAT
// ═══════════════════════════
async function sendMessage() {
  const input = document.getElementById('user-input');
  const text = input.value.trim();
  if (!text || !STATE.isInterviewActive) return;

  input.value = '';
  addMessage('user', text);
  STATE.transcript.push({ role: 'user', content: text });

  // Update communication score based on response length
  const wordCount = text.split(' ').length;
  STATE.scores.communication = Math.min(100, STATE.scores.communication + Math.min(8, wordCount / 2));
  updateScoreDisplay();

  showTyping(true);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, session_id: STATE.sessionId })
    });
    const data = await res.json();
    showTyping(false);

    if (data.message) {
      STATE.transcript.push({ role: 'assistant', content: data.message });
      addMessage('assistant', data.message);

      STATE.questionCount = data.question_count || STATE.questionCount + 1;
      document.getElementById('q-num').textContent = STATE.questionCount;

      // Update overall score
      STATE.scores.overall = Math.min(100, Math.round(
        (STATE.scores.confidence * 0.3 + STATE.scores.communication * 0.4 + STATE.scores.presence * 0.3)
      ));
      updateScoreDisplay();

      if (data.is_complete) {
        setTimeout(() => endInterview(), 3000);
      }
    }
  } catch (e) {
    showTyping(false);
    showToast('Connection error. Please try again.', 'error');
    console.error('Chat error:', e);
  }
}

function addMessage(role, text) {
  const container = document.getElementById('chat-messages');
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${role}`;

  const label = role === 'assistant' ? '◈ ARIA' : `⬡ ${STATE.candidateName.toUpperCase()}`;
  const time = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

  msgDiv.innerHTML = `
    <div class="message-header">
      <span>${label}</span>
      <span style="opacity:0.4">${time}</span>
    </div>
    <div class="message-bubble" id="msg-${Date.now()}"></div>
  `;

  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;

  // Typewriter effect for assistant
  const bubble = msgDiv.querySelector('.message-bubble');
  if (role === 'assistant') {
    typewriterEffect(bubble, text);
  } else {
    bubble.textContent = text;
  }
}

function typewriterEffect(element, text, speed = 18) {
  let i = 0;
  const cursor = document.createElement('span');
  cursor.className = 'typing-cursor';
  element.appendChild(cursor);

  const interval = setInterval(() => {
    if (i < text.length) {
      element.insertBefore(document.createTextNode(text[i]), cursor);
      i++;
      const container = document.getElementById('chat-messages');
      container.scrollTop = container.scrollHeight;
    } else {
      clearInterval(interval);
      cursor.remove();
    }
  }, speed);
}

function showTyping(show) {
  const el = document.getElementById('typing-indicator');
  el.className = show ? 'typing-indicator visible' : 'typing-indicator';
  if (show) {
    const container = document.getElementById('chat-messages');
    container.scrollTop = container.scrollHeight;
  }
}

// ═══════════════════════════
// EMOTION DETECTION
// ═══════════════════════════
function startEmotionDetection() {
  if (!STATE.webcamStream) return;

  STATE.emotionInterval = setInterval(async () => {
    if (!STATE.isInterviewActive) return;
    const frame = captureWebcamFrame();
    if (!frame) return;

    try {
      const res = await fetch('/api/analyze-emotion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: frame })
      });
      const data = await res.json();
      updateEmotionUI(data);
      updateFeedback(data);
    } catch (e) {
      // Silent fail
    }
  }, 2500);
}

function captureWebcamFrame() {
  const video = document.getElementById('webcam-video');
  const canvas = document.createElement('canvas');
  canvas.width = 320; canvas.height = 240;
  const ctx = canvas.getContext('2d');
  try {
    ctx.drawImage(video, 0, 0, 320, 240);
    return canvas.toDataURL('image/jpeg', 0.7);
  } catch { return null; }
}

function updateEmotionUI(data) {
  const emotion = data.emotion || 'unknown';
  const confidence = data.confidence || 0;
  const eyeContact = data.eye_contact || false;
  const faceVisible = data.face_visible || false;
  const attention = data.attention_score || 0;

  // Track emotion history
  STATE.emotionHistory.push(emotion);
  STATE.emotionSummary[emotion] = (STATE.emotionSummary[emotion] || 0) + 1;

  // Update presence score
  if (faceVisible) {
    STATE.scores.presence = Math.min(100, STATE.scores.presence + (eyeContact ? 1.5 : 0.5));
  }
  if (emotion === 'happy' || emotion === 'confident') {
    STATE.scores.confidence = Math.min(100, STATE.scores.confidence + 1);
  }
  updateScoreDisplay();

  // Emotion display
  const color = EMOTION_COLORS[emotion] || '#00f5ff';
  const icon = EMOTION_ICONS[emotion] || '◉';
  document.getElementById('emotion-icon').textContent = icon;
  document.getElementById('emotion-label').textContent = emotion.toUpperCase();
  document.getElementById('emotion-display').style.color = color;
  document.getElementById('confidence-bar').style.width = `${confidence * 100}%`;
  document.getElementById('confidence-pct').textContent = `${(confidence * 100).toFixed(0)}%`;

  // Face status
  const faceDot = document.getElementById('face-dot');
  const faceLabel = document.getElementById('face-label');
  if (faceVisible) {
    faceDot.className = 'face-dot detected';
    faceLabel.textContent = 'FACE DETECTED';
  } else {
    faceDot.className = 'face-dot lost';
    faceLabel.textContent = 'NO FACE FOUND';
  }

  // Eye contact
  document.getElementById('eye-contact-val').textContent = eyeContact ? '✓ YES' : '✗ NO';
  document.getElementById('eye-contact-val').style.color = eyeContact ? 'var(--green)' : 'var(--amber)';

  // Attention
  document.getElementById('attention-bar').style.width = `${attention * 100}%`;

  // Confidence display
  const confDisplay = Math.round(STATE.scores.confidence);
  document.getElementById('confidence-score-val').textContent = `${confDisplay}`;

  // Timeline
  addTimelineSegment(emotion, color);

  // Annotated frame
  if (data.annotated_image) {
    const canvas = document.getElementById('webcam-canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.onload = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    img.src = data.annotated_image;
  }
}

function addTimelineSegment(emotion, color) {
  const track = document.getElementById('timeline-track');
  const seg = document.createElement('div');
  seg.className = 'timeline-segment';
  seg.style.backgroundColor = color;
  seg.style.opacity = '0.7';
  seg.title = emotion;
  track.appendChild(seg);

  // Keep max 50 segments
  while (track.children.length > 50) track.removeChild(track.firstChild);
}

// ═══════════════════════════
// REALTIME FEEDBACK
// ═══════════════════════════
async function updateFeedback(emotionData) {
  try {
    const res = await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        emotion: emotionData.emotion,
        eye_contact: emotionData.eye_contact,
        face_visible: emotionData.face_visible,
        confidence_score: emotionData.confidence
      })
    });
    const data = await res.json();
    if (data.feedback && data.feedback.length > 0) {
      renderFeedback(data.feedback);
      STATE.feedbackHistory.push(...data.feedback);
    }
  } catch { }
}

function renderFeedback(feedbackList) {
  const container = document.getElementById('feedback-items');
  container.innerHTML = '';

  feedbackList.slice(0, 4).forEach(fb => {
    const item = document.createElement('div');
    item.className = `feedback-item ${fb.type || 'info'}`;
    const icons = { success: '✓', warning: '⚠', info: '◈', error: '✕' };
    item.innerHTML = `<span class="fb-icon">${icons[fb.type] || '◈'}</span><span>${fb.message}</span>`;
    container.appendChild(item);
  });
}

// ═══════════════════════════
// VOICE INPUT
// ═══════════════════════════
function initSpeechInput() {
  // Web Speech API (browser-native)
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    STATE.speechRecognition = new SpeechRecognition();
    STATE.speechRecognition.continuous = false;
    STATE.speechRecognition.interimResults = true;
    STATE.speechRecognition.lang = 'en-US';

    STATE.speechRecognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      const display = document.getElementById('transcript-display');
      display.classList.add('active');
      document.getElementById('transcript-text').textContent = transcript;

      if (event.results[event.results.length - 1].isFinal) {
        document.getElementById('user-input').value = transcript;
        display.classList.remove('active');
      }
    };

    STATE.speechRecognition.onerror = (e) => {
      console.warn('Speech error:', e.error);
      stopVoiceRecording();
    };

    STATE.speechRecognition.onend = () => {
      stopVoiceRecordingUI();
    };
  }
}

function startVoiceRecording() {
  if (STATE.isRecording) return;
  STATE.isRecording = true;

  const micBtn = document.getElementById('mic-btn');
  micBtn.classList.add('recording');
  document.getElementById('transcript-text').textContent = 'Listening...';
  document.getElementById('transcript-display').classList.add('active');

  if (STATE.speechRecognition) {
    try { STATE.speechRecognition.start(); } catch (e) { console.warn(e); }
  } else {
    // Fallback: MediaRecorder + Whisper
    startMediaRecorder();
  }
}

function stopVoiceRecording() {
  if (!STATE.isRecording) return;

  if (STATE.speechRecognition) {
    try { STATE.speechRecognition.stop(); } catch (e) { }
  }
  if (STATE.mediaRecorder && STATE.mediaRecorder.state === 'recording') {
    STATE.mediaRecorder.stop();
  }
  stopVoiceRecordingUI();
}

function stopVoiceRecordingUI() {
  STATE.isRecording = false;
  document.getElementById('mic-btn').classList.remove('recording');
  setTimeout(() => {
    document.getElementById('transcript-display').classList.remove('active');
  }, 2000);
}

async function startMediaRecorder() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    STATE.audioChunks = [];
    STATE.mediaRecorder = new MediaRecorder(stream);
    STATE.mediaRecorder.ondataavailable = (e) => STATE.audioChunks.push(e.data);
    STATE.mediaRecorder.onstop = async () => {
      const blob = new Blob(STATE.audioChunks, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('audio', blob, 'recording.webm');

      try {
        const res = await fetch('/api/speech-to-text', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.text) {
          document.getElementById('user-input').value = data.text;
          document.getElementById('transcript-text').textContent = data.text;
        }
      } catch (e) { console.error('STT error:', e); }

      stream.getTracks().forEach(t => t.stop());
    };
    STATE.mediaRecorder.start();
  } catch (e) {
    showToast('Microphone access denied', 'error');
  }
}

// ═══════════════════════════
// SCORE DISPLAY
// ═══════════════════════════
function updateScoreDisplay() {
  STATE.scores.overall = Math.min(100, Math.round(
    (STATE.scores.confidence * 0.3 + STATE.scores.communication * 0.4 + STATE.scores.presence * 0.3)
  ));

  animateScore('overall-score', STATE.scores.overall);
  animateScore('confidence-live', Math.round(STATE.scores.confidence));
  animateScore('communication-score', Math.round(STATE.scores.communication));
  animateScore('presence-score', Math.round(STATE.scores.presence));
}

function animateScore(elementId, target) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const current = parseInt(el.textContent) || 0;
  const step = (target - current) / 15;
  let val = current;
  const interval = setInterval(() => {
    val += step;
    if ((step > 0 && val >= target) || (step < 0 && val <= target)) {
      val = target;
      clearInterval(interval);
    }
    el.textContent = Math.round(val);
  }, 20);
}

// ═══════════════════════════
// END INTERVIEW
// ═══════════════════════════
function endInterview() {
  if (!STATE.isInterviewActive) return;
  STATE.isInterviewActive = false;

  clearInterval(STATE.timerInterval);
  clearInterval(STATE.emotionInterval);

  if (STATE.webcamStream) {
    STATE.webcamStream.getTracks().forEach(t => t.stop());
  }
  if (STATE.speechRecognition) {
    try { STATE.speechRecognition.stop(); } catch (e) { }
  }

  // Calculate final scores
  STATE.scores.technical = Math.min(100, Math.round(STATE.questionCount * 8 + Math.random() * 15));
  STATE.scores.overall = Math.min(100, Math.round(
    (STATE.scores.confidence * 0.25 + STATE.scores.communication * 0.35 +
     STATE.scores.presence * 0.2 + STATE.scores.technical * 0.2)
  ));

  showScreen('results-screen');
  initResultsScreen();
}

// ═══════════════════════════
// RESULTS SCREEN
// ═══════════════════════════
function initResultsScreen() {
  // Overall score circle
  setTimeout(() => {
    const score = STATE.scores.overall;
    document.getElementById('final-overall').textContent = score;
    const circumference = 314;
    const offset = circumference - (score / 100) * circumference;
    document.getElementById('score-ring').style.strokeDashoffset = offset;
    document.getElementById('score-rating').textContent = getRating(score);
  }, 300);

  // Breakdown bars
  setTimeout(() => {
    setBar('r-confidence', 'r-confidence-val', STATE.scores.confidence);
    setBar('r-communication', 'r-communication-val', STATE.scores.communication);
    setBar('r-presence', 'r-presence-val', STATE.scores.presence);
    setBar('r-technical', 'r-technical-val', STATE.scores.technical);
  }, 500);

  // Emotion chart
  buildEmotionChart();

  // Final feedback
  buildFinalFeedback();

  // Download report button
  document.getElementById('download-report-btn').addEventListener('click', downloadReport);
  document.getElementById('new-interview-btn').addEventListener('click', () => location.reload());
}

function setBar(barId, valId, value) {
  const rounded = Math.round(value);
  document.getElementById(barId).style.width = `${rounded}%`;
  document.getElementById(valId).textContent = rounded;
}

function buildEmotionChart() {
  const chart = document.getElementById('emotion-chart');
  const total = Object.values(STATE.emotionSummary).reduce((a, b) => a + b, 0) || 1;

  const sorted = Object.entries(STATE.emotionSummary)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 6);

  if (sorted.length === 0) {
    chart.innerHTML = '<p style="color:var(--text-muted);font-size:0.75rem">No emotion data captured</p>';
    return;
  }

  chart.innerHTML = sorted.map(([emotion, count]) => {
    const pct = Math.round((count / total) * 100);
    const color = EMOTION_COLORS[emotion] || '#00f5ff';
    const icon = EMOTION_ICONS[emotion] || '◉';
    return `
      <div class="echart-item">
        <span class="echart-label">${icon} ${emotion}</span>
        <div class="echart-bar-wrap">
          <div class="echart-bar" style="width:${pct}%;background:${color}" data-pct="${pct}"></div>
        </div>
        <span class="echart-pct">${pct}%</span>
      </div>
    `;
  }).join('');

  // Animate bars
  setTimeout(() => {
    chart.querySelectorAll('.echart-bar').forEach(bar => {
      bar.style.transition = 'width 1s ease';
    });
  }, 100);
}

function buildFinalFeedback() {
  const container = document.getElementById('final-feedback-list');

  const feedbacks = generateFinalFeedback();
  container.innerHTML = feedbacks.map(fb => `
    <div class="final-fb-item ${fb.type}">
      <span>${fb.type === 'success' ? '✓' : fb.type === 'warning' ? '⚠' : '◈'}</span>
      <span>${fb.message}</span>
    </div>
  `).join('');
}

function generateFinalFeedback() {
  const feedback = [];
  const scores = STATE.scores;

  if (scores.overall >= 75) feedback.push({ type: 'success', message: 'Excellent overall interview performance!' });
  else if (scores.overall >= 55) feedback.push({ type: 'info', message: 'Good performance with room to grow.' });
  else feedback.push({ type: 'warning', message: 'Consider more practice before your next interview.' });

  if (scores.communication >= 70) feedback.push({ type: 'success', message: 'Strong communication skills demonstrated.' });
  else feedback.push({ type: 'warning', message: 'Work on providing more detailed, structured answers.' });

  if (scores.presence >= 60) feedback.push({ type: 'success', message: 'Good camera presence and eye contact.' });
  else feedback.push({ type: 'warning', message: 'Maintain better eye contact with the camera.' });

  const dominantEmotion = Object.entries(STATE.emotionSummary).sort(([,a],[,b]) => b-a)[0];
  if (dominantEmotion) {
    const [emotion] = dominantEmotion;
    if (emotion === 'happy' || emotion === 'confident') {
      feedback.push({ type: 'success', message: `You projected a positive, confident demeanor.` });
    } else if (emotion === 'nervous' || emotion === 'fear') {
      feedback.push({ type: 'warning', message: 'Work on managing interview anxiety — practice helps.' });
    } else {
      feedback.push({ type: 'info', message: `Your dominant expression was ${emotion} — aim for warm and confident.` });
    }
  }

  if (STATE.questionCount >= 8) feedback.push({ type: 'success', message: 'Completed a comprehensive interview session.' });

  // Add unique tips from history
  const uniqueFeedback = [...new Set(STATE.feedbackHistory.map(f => f.message))].slice(0, 2);
  uniqueFeedback.forEach(msg => feedback.push({ type: 'info', message: msg }));

  return feedback.slice(0, 6);
}

async function downloadReport() {
  const btn = document.getElementById('download-report-btn');
  btn.textContent = '⏳ GENERATING REPORT...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/generate-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        candidate_name: STATE.candidateName,
        job_role: STATE.jobRole,
        duration: STATE.elapsedSeconds,
        transcript: STATE.transcript,
        emotion_summary: STATE.emotionSummary,
        scores: STATE.scores,
        feedback: generateFinalFeedback()
      })
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ARIA_Interview_Report_${STATE.candidateName.replace(/\s/g,'_')}.pdf`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('Report downloaded!', 'success');
    btn.textContent = '✓ REPORT DOWNLOADED';
  } catch (e) {
    showToast('Report generation failed. Check server.', 'error');
    btn.textContent = '⬇ DOWNLOAD PDF REPORT';
    btn.disabled = false;
    console.error('Report error:', e);
  }
}

// ═══════════════════════════
// TOAST NOTIFICATIONS
// ═══════════════════════════
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icons = { success: '✓', error: '✕', info: '◈', warning: '⚠' };
  toast.innerHTML = `
    <span style="color:var(--${type === 'success' ? 'green' : type === 'error' ? 'red' : 'cyan'})">${icons[type]}</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ═══════════════════════════
// HELPERS
// ═══════════════════════════
function getRating(score) {
  if (score >= 85) return '★★★★★ OUTSTANDING';
  if (score >= 70) return '★★★★☆ STRONG CANDIDATE';
  if (score >= 55) return '★★★☆☆ AVERAGE PERFORMANCE';
  if (score >= 40) return '★★☆☆☆ NEEDS IMPROVEMENT';
  return '★☆☆☆☆ REQUIRES PRACTICE';
}

// ═══════════════════════════
// INIT
// ═══════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initParticles();
  initSetup();
  showScreen('setup-screen');
  console.log('%c◈ ARIA AI Interview Simulator', 'color:#00f5ff;font-family:monospace;font-size:16px;font-weight:bold');
  console.log('%cAdvanced Recruitment Intelligence Assistant', 'color:#a855f7;font-family:monospace;font-size:10px');
});
