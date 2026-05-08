# 🚀 AI Interview Simulator

An AI-powered interview preparation platform that simulates real interview experiences using Artificial Intelligence, Emotion Detection, and Speech Recognition.

Built with **Python, Flask, HTML, CSS, JavaScript, SQLite, OpenRouter API, MediaPipe, and Web Speech API**.

---

# 📌 Project Overview

Preparing for interviews is difficult for many students and job seekers because they do not get access to realistic interview practice and proper feedback.

The **AI Interview Simulator** solves this problem by creating a smart virtual interviewer that:
- asks interview questions,
- listens to answers,
- detects emotions,
- calculates confidence levels,
- and generates detailed performance reports.

The platform provides a real-time interview environment directly inside the browser.

---

# ✨ Features

## 🎤 AI-Based Interviewer
- AI interviewer named **Alex**
- Generates technical and HR interview questions
- Asks intelligent follow-up questions
- Human-like conversation flow

---

## 🗣️ Speech Recognition
- Uses **Web Speech API**
- Converts voice into text in real time
- Users can answer by speaking naturally
- Live microphone interaction

---

## 😊 Emotion Detection
- Uses **Google MediaPipe FaceLandmarker**
- Detects facial emotions using webcam
- Tracks confidence, stress, focus, happiness, and anxiety
- Maps 478 facial points in real time

---

## 📊 Live Performance Scoring
Two live scores are calculated during interviews:

### Confidence Score
Based on:
- facial expressions
- eye focus
- emotional state

### Communication Score
Based on:
- answer length
- speaking activity
- response frequency

---

## 📄 AI Performance Report
After interview completion:
- strengths are generated
- weaknesses are identified
- improvement suggestions are provided
- full transcript is displayed
- report download support

---

## 🕘 Session History
- Stores previous interview sessions
- Search and filter functionality
- Persistent local database storage

---

# 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Flask | API routing and server |
| SQLite | Local database |
| HTML | Frontend structure |
| CSS | Styling and UI |
| JavaScript | Real-time browser interaction |
| OpenRouter API | AI communication |
| LLaMA 3.3 70B | AI interview model |
| MediaPipe | Emotion detection |
| Web Speech API | Speech-to-text |

---

# 🧠 APIs and Libraries Used

## 1. OpenRouter API
Used for connecting the backend with the **LLaMA 3.3 70B AI model**.

### Usage
- Generates interview questions
- Creates follow-up questions
- Analyzes user responses
- Generates performance reports

### Workflow
1. User submits answer
2. Flask backend sends request to OpenRouter API
3. AI model processes response
4. AI sends next question back to frontend

---

## 2. MediaPipe FaceLandmarker
Google’s machine learning library for facial analysis.

### Usage
- Face tracking
- Emotion detection
- Confidence analysis

### Features
- 478 facial landmark mapping
- Runs completely inside browser
- No facial data sent to server

---

## 3. Web Speech API
Browser-based speech recognition API.

### Usage
- Converts speech to text
- Real-time microphone input
- Hands-free interview interaction

---

# ⚙️ Project Architecture

```text
User Browser
│
├── HTML/CSS Frontend
├── JavaScript Interaction
├── MediaPipe Emotion Detection
├── Web Speech API
│
↓ HTTP Requests
│
Flask Backend (Python)
│
├── OpenRouter API Communication
├── Score Processing
├── Report Generation
├── Database Operations
│
↓
│
SQLite Database
```

---

# 🔄 Project Workflow

## Step 1
User enters:
- Name
- Job role

---

## Step 2
AI interviewer starts interview session.

---

## Step 3
User answers:
- using voice
- or typing

---

## Step 4
System performs:
- speech recognition
- emotion detection
- confidence analysis
- communication analysis

---

## Step 5
Scores update live during interview.

---

## Step 6
Final report is generated automatically.

---

# 📂 Project Structure

```text
AI_Interview_Simulator/
│
├── app.py
├── interview.db
├── requirements.txt
├── static/
│   ├── css/
│   ├── js/
│   └── assets/
│
├── templates/
│   ├── home.html
│   ├── interview.html
│   ├── report.html
│   └── sessions.html
│
└── README.md
```

---

# ▶️ How to Run the Project

## 1. Clone Repository

```bash
git clone https://github.com/Devpratapsingh204/AI_interview_simulator.git
```

---

## 2. Open Project Folder

```bash
cd AI_interview_simulator
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run Flask Application

```bash
python app.py
```

---

## 5. Open Browser

```text
http://localhost:5000
```

---

# 📸 Main Modules

## 🏠 Home Page
- User details input
- Job role selection
- Interview start

---

## 🎥 Interview Page
- Live webcam feed
- AI conversation
- Live scores
- Speech recognition
- Timer

---

## 📑 Report Page
- Final scores
- AI analysis
- Strengths and weaknesses
- Full interview transcript

---

## 📚 Session History
- Previous interviews
- Search and filter support

---

# 🔒 Privacy and Security

- Facial processing happens locally in browser
- No webcam video stored
- No face data uploaded externally
- Local SQLite storage

---

# 🚀 Future Scope

- Resume analysis
- Multi-language support
- Coding interview rounds
- Cloud deployment
- Advanced AI analytics
- Eye contact tracking
- Real-time recruiter feedback
- AI personality customization

---

# 🎯 Learning Outcomes

This project helped in understanding:
- Artificial Intelligence integration
- Flask backend development
- REST APIs
- Real-time browser interaction
- Emotion detection
- Speech recognition
- Database management
- Frontend-backend communication

---

# 👨‍💻 Author

## Dev Pratap Singh

B.Tech CSE Student  
Lovely Professional University

GitHub:
https://github.com/Devpratapsingh204

---

# 🙏 Acknowledgements

- OpenRouter API
- Meta LLaMA
- Google MediaPipe
- Flask Community
- Web Speech API Documentation

---

# ⭐ Conclusion

The AI Interview Simulator is a smart and interactive platform designed to improve interview preparation using Artificial Intelligence.

It combines:
- AI conversation,
- speech recognition,
- emotion detection,
- and performance analytics

to create a realistic interview experience for students and job seekers.

---
