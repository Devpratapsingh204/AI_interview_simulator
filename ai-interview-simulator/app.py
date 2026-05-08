import os
import base64
import json
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Import modules
from chatbot import InterviewChatbot
from emotion_detection import EmotionDetector
from speech_module import SpeechProcessor
from report_generator import ReportGenerator

chatbot = InterviewChatbot()
emotion_detector = EmotionDetector()
speech_processor = SpeechProcessor()
report_generator = ReportGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start-interview', methods=['POST'])
def start_interview():
    data = request.json
    job_role = data.get('job_role', 'Software Engineer')
    candidate_name = data.get('candidate_name', 'Candidate')
    resume_text = data.get('resume_text', '')
    
    result = chatbot.start_interview(job_role, candidate_name, resume_text)
    return jsonify(result)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    result = chatbot.send_message(user_message, session_id)
    return jsonify(result)

@app.route('/api/analyze-emotion', methods=['POST'])
def analyze_emotion():
    data = request.json
    image_data = data.get('image', '')
    
    if not image_data:
        return jsonify({'error': 'No image provided'}), 400
    
    # Decode base64 image
    if ',' in image_data:
        image_data = image_data.split(',')[1]
    
    image_bytes = base64.b64decode(image_data)
    result = emotion_detector.analyze(image_bytes)
    return jsonify(result)

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file'}), 400
    
    audio_file = request.files['audio']
    result = speech_processor.transcribe(audio_file)
    return jsonify(result)

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    data = request.json
    report_data = {
        'candidate_name': data.get('candidate_name', 'Candidate'),
        'job_role': data.get('job_role', 'Software Engineer'),
        'duration': data.get('duration', 0),
        'transcript': data.get('transcript', []),
        'emotion_summary': data.get('emotion_summary', {}),
        'scores': data.get('scores', {}),
        'feedback': data.get('feedback', [])
    }
    
    pdf_path = report_generator.generate(report_data)
    return send_file(pdf_path, as_attachment=True, download_name='interview_report.pdf')

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Extract text from resume
    result = speech_processor.extract_resume_text(file)
    return jsonify(result)

@app.route('/api/feedback', methods=['POST'])
def get_feedback():
    data = request.json
    emotion = data.get('emotion', 'neutral')
    eye_contact = data.get('eye_contact', True)
    face_visible = data.get('face_visible', True)
    confidence_score = data.get('confidence_score', 0.5)
    
    feedback = generate_realtime_feedback(emotion, eye_contact, face_visible, confidence_score)
    return jsonify({'feedback': feedback})

def generate_realtime_feedback(emotion, eye_contact, face_visible, confidence_score):
    feedback = []
    
    if not face_visible:
        feedback.append({"type": "warning", "message": "Position your face in the camera frame"})
    
    if not eye_contact:
        feedback.append({"type": "warning", "message": "Maintain eye contact with the camera"})
    
    emotion_feedback = {
        'happy': {"type": "success", "message": "Great energy! You appear confident and positive"},
        'nervous': {"type": "warning", "message": "Take a deep breath — you're doing great"},
        'sad': {"type": "warning", "message": "Try to project more enthusiasm and positivity"},
        'angry': {"type": "warning", "message": "Relax your expression — appear more approachable"},
        'neutral': {"type": "info", "message": "Good composure — show a bit more warmth"},
        'surprised': {"type": "info", "message": "Stay composed and focused"},
        'fear': {"type": "warning", "message": "Build your confidence — you're well prepared"},
        'disgust': {"type": "warning", "message": "Maintain a professional, pleasant expression"}
    }
    
    if emotion in emotion_feedback:
        feedback.append(emotion_feedback[emotion])
    
    if confidence_score > 0.75:
        feedback.append({"type": "success", "message": "You seem very confident — excellent!"})
    elif confidence_score < 0.35:
        feedback.append({"type": "warning", "message": "Project more confidence in your delivery"})
    
    return feedback

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
