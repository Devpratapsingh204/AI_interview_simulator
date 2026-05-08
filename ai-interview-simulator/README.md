# ◈ ARIA — AI Interview Simulator

> **Advanced Recruitment Intelligence Assistant**  
> A futuristic AI-powered interview simulator with live webcam, emotion detection, voice input, and real-time feedback.

---

## 🚀 Quick Start

### 1. Clone / Extract the Project
```
ai-interview-simulator/
├── app.py
├── chatbot.py
├── emotion_detection.py
├── speech_module.py
├── report_generator.py
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up API Key
```bash
cp .env.example .env
```
Then open `.env` and add your API key:

**Option A — Groq (FREE, recommended):**
1. Sign up at https://console.groq.com
2. Create an API key
3. Set `GROQ_API_KEY=gsk_your_key_here`

**Option B — OpenRouter (FREE tier):**
1. Sign up at https://openrouter.ai
2. Set `OPENROUTER_API_KEY=sk-or-your_key_here`

> ⚠️ If no API key is provided, the simulator uses smart mock responses.

### 5. Run the Application
```bash
python app.py
```
Open your browser: **http://localhost:5000**

---

## 🧠 Features

| Feature | Status | Notes |
|---------|--------|-------|
| AI Chatbot (LLaMA-3) | ✅ | Groq or OpenRouter |
| Webcam Feed | ✅ | Browser permission required |
| Emotion Detection | ✅ | OpenCV + optional DeepFace |
| Voice Input | ✅ | Web Speech API (browser-native) |
| Real-time Feedback | ✅ | Live emotion + presence scoring |
| PDF Report | ✅ | ReportLab |
| Resume Upload | ✅ | PDF, TXT, DOCX |
| Interview Timer | ✅ | Live HUD timer |
| Score Tracking | ✅ | Confidence, Communication, Presence |

---

## 📦 Optional Enhancements

Install these for more powerful features:

```bash
# Advanced emotion detection
pip install deepface

# Whisper speech-to-text (requires ffmpeg)
pip install openai-whisper

# Alternative STT + audio processing
pip install SpeechRecognition pydub

# PDF resume reading
pip install PyPDF2

# DOCX resume reading
pip install python-docx
```

---

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **AI**: Groq API (LLaMA-3) / OpenRouter
- **Vision**: OpenCV (+ DeepFace optional)
- **Voice**: Web Speech API + Whisper
- **Report**: ReportLab PDF
- **Frontend**: Pure HTML + CSS + JavaScript (no frameworks)

---

## 💡 Tips

- **Lighting**: Ensure good front lighting for best emotion detection
- **Camera position**: Face centered, ~arm's length from screen
- **Microphone**: Hold mic button and speak clearly
- **Browser**: Chrome or Edge recommended (best Web Speech API support)

---

## 📄 License

MIT — Free to use, modify, and distribute.

---

*Built with ◈ ARIA — Making interviews smarter, one session at a time.*
