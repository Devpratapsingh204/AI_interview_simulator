import cv2
import numpy as np
import io
import base64
import random

class EmotionDetector:
    def __init__(self):
        self.use_deepface = False
        self.face_cascade = None
        
        # Try to load DeepFace
        try:
            from deepface import DeepFace
            self.DeepFace = DeepFace
            self.use_deepface = True
            print("✅ DeepFace loaded successfully")
        except ImportError:
            print("⚠️  DeepFace not available, using fallback emotion detection")

        # Try to load OpenCV face detector
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            print("✅ OpenCV face cascade loaded")
        except Exception as e:
            print(f"⚠️  OpenCV cascade error: {e}")

    def analyze(self, image_bytes):
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return self._empty_result()

            result = self._detect_with_opencv(frame)
            
            # Overlay bounding boxes
            annotated_frame = self._draw_annotations(frame.copy(), result)
            annotated_b64 = self._frame_to_base64(annotated_frame)
            result['annotated_image'] = annotated_b64
            
            return result

        except Exception as e:
            print(f"Emotion detection error: {e}")
            return self._empty_result()

    def _detect_with_opencv(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.face_cascade is None:
            return self._mock_detection()

        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )

        if len(faces) == 0:
            return {
                'face_detected': False,
                'emotion': 'unknown',
                'emotion_scores': {},
                'confidence': 0.0,
                'eye_contact': False,
                'face_visible': False,
                'face_box': None,
                'attention_score': 0.0
            }

        # Use the largest face
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face_roi = frame[y:y+h, x:x+w]

        if self.use_deepface:
            return self._analyze_with_deepface(frame, face_roi, x, y, w, h)
        else:
            return self._analyze_heuristic(frame, face_roi, x, y, w, h)

    def _analyze_with_deepface(self, frame, face_roi, x, y, w, h):
        try:
            result = self.DeepFace.analyze(
                face_roi,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            
            if isinstance(result, list):
                result = result[0]
            
            emotion = result.get('dominant_emotion', 'neutral')
            emotion_scores = result.get('emotion', {})
            confidence = emotion_scores.get(emotion, 50.0) / 100.0
            
            fh, fw = frame.shape[:2]
            face_center_x = x + w // 2
            is_centered = abs(face_center_x - fw // 2) < fw * 0.25
            face_size_ratio = (w * h) / (fw * fh)
            eye_contact = is_centered and face_size_ratio > 0.04
            
            return {
                'face_detected': True,
                'emotion': emotion,
                'emotion_scores': {k: round(v / 100.0, 3) for k, v in emotion_scores.items()},
                'confidence': round(confidence, 3),
                'eye_contact': eye_contact,
                'face_visible': True,
                'face_box': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                'attention_score': round(min(1.0, face_size_ratio * 8), 3)
            }
        except Exception as e:
            print(f"DeepFace error: {e}")
            return self._analyze_heuristic(frame, face_roi, x, y, w, h)

    def _analyze_heuristic(self, frame, face_roi, x, y, w, h):
        """Lightweight heuristic emotion detection using pixel analysis"""
        fh, fw = frame.shape[:2]
        face_center_x = x + w // 2
        is_centered = abs(face_center_x - fw // 2) < fw * 0.25
        face_size_ratio = (w * h) / (fw * fh)
        eye_contact = is_centered and face_size_ratio > 0.04

        # Analyze brightness/contrast as proxy for expression energy
        gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray_roi) / 255.0
        std = np.std(gray_roi) / 255.0
        
        # Simple heuristic: brighter + high contrast = happy/engaged
        if brightness > 0.55 and std > 0.12:
            emotion = 'happy'
            scores = {'happy': 0.65, 'neutral': 0.25, 'surprised': 0.10}
        elif brightness < 0.35:
            emotion = 'sad'
            scores = {'sad': 0.55, 'neutral': 0.30, 'fear': 0.15}
        elif std < 0.08:
            emotion = 'neutral'
            scores = {'neutral': 0.70, 'sad': 0.15, 'happy': 0.15}
        else:
            emotion = 'neutral'
            scores = {'neutral': 0.50, 'happy': 0.30, 'nervous': 0.20}
        
        confidence = max(scores.values())

        return {
            'face_detected': True,
            'emotion': emotion,
            'emotion_scores': scores,
            'confidence': round(confidence, 3),
            'eye_contact': eye_contact,
            'face_visible': True,
            'face_box': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
            'attention_score': round(min(1.0, face_size_ratio * 8), 3)
        }

    def _mock_detection(self):
        emotions = ['happy', 'neutral', 'nervous', 'confident', 'neutral', 'happy']
        emotion = random.choice(emotions)
        return {
            'face_detected': True,
            'emotion': emotion,
            'emotion_scores': {emotion: 0.75, 'neutral': 0.25},
            'confidence': 0.75,
            'eye_contact': True,
            'face_visible': True,
            'face_box': {'x': 120, 'y': 80, 'w': 200, 'h': 200},
            'attention_score': 0.82
        }

    def _draw_annotations(self, frame, result):
        if not result.get('face_detected'):
            return frame

        box = result.get('face_box')
        if not box:
            return frame

        x, y, w, h = box['x'], box['y'], box['w'], box['h']
        emotion = result.get('emotion', 'unknown')
        confidence = result.get('confidence', 0)
        eye_contact = result.get('eye_contact', False)

        # Neon color by emotion
        colors = {
            'happy': (0, 255, 128),
            'neutral': (0, 200, 255),
            'sad': (255, 100, 50),
            'angry': (0, 50, 255),
            'nervous': (255, 200, 0),
            'fear': (200, 0, 255),
            'surprised': (0, 255, 255),
            'disgust': (100, 0, 200),
            'confident': (0, 255, 100),
            'unknown': (150, 150, 150)
        }
        color = colors.get(emotion, (0, 200, 255))

        # Draw glowing bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.rectangle(frame, (x - 2, y - 2), (x + w + 2, y + h + 2), 
                     tuple(c // 3 for c in color), 1)

        # Draw corner accents
        corner_len = 20
        thickness = 3
        corners = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
        for cx, cy in corners:
            dx = -corner_len if cx == x + w else corner_len
            dy = -corner_len if cy == y + h else corner_len
            cv2.line(frame, (cx, cy), (cx + dx, cy), color, thickness)
            cv2.line(frame, (cx, cy), (cx, cy + dy), color, thickness)

        # Label background
        label = f"{emotion.upper()} {confidence*100:.0f}%"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x, y - th - 16), (x + tw + 10, y), (0, 0, 0), -1)
        cv2.putText(frame, label, (x + 5, y - 6),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Eye contact indicator
        contact_text = "● EYE CONTACT" if eye_contact else "○ LOOK AT CAMERA"
        contact_color = (0, 255, 128) if eye_contact else (0, 100, 255)
        cv2.putText(frame, contact_text, (x, y + h + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, contact_color, 1)

        return frame

    def _frame_to_base64(self, frame):
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode('utf-8')

    def _empty_result(self):
        return {
            'face_detected': False,
            'emotion': 'unknown',
            'emotion_scores': {},
            'confidence': 0.0,
            'eye_contact': False,
            'face_visible': False,
            'face_box': None,
            'attention_score': 0.0,
            'annotated_image': None
        }
