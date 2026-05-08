import os
import io
import tempfile

class SpeechProcessor:
    def __init__(self):
        self.whisper_available = False
        self.sr_available = False
        
        try:
            import whisper
            self.whisper = whisper
            self.whisper_model = whisper.load_model("tiny")
            self.whisper_available = True
            print("✅ Whisper loaded")
        except ImportError:
            print("⚠️  Whisper not available")
        
        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            self.sr_available = True
            print("✅ SpeechRecognition loaded")
        except ImportError:
            print("⚠️  SpeechRecognition not available")

    def transcribe(self, audio_file):
        try:
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as tmp:
                audio_file.save(tmp.name)
                tmp_path = tmp.name
            
            if self.whisper_available:
                result = self.whisper_model.transcribe(tmp_path)
                text = result.get('text', '').strip()
                os.unlink(tmp_path)
                return {'text': text, 'success': True, 'method': 'whisper'}
            
            elif self.sr_available:
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(tmp_path)
                    wav_path = tmp_path.replace('.webm', '.wav')
                    audio.export(wav_path, format='wav')
                    
                    with self.sr.AudioFile(wav_path) as source:
                        audio_data = self.recognizer.record(source)
                    
                    text = self.recognizer.recognize_google(audio_data)
                    os.unlink(tmp_path)
                    if os.path.exists(wav_path):
                        os.unlink(wav_path)
                    return {'text': text, 'success': True, 'method': 'google_sr'}
                except Exception as e:
                    print(f"SR error: {e}")
            
            os.unlink(tmp_path)
            return {'text': '', 'success': False, 'error': 'No STT engine available'}
        
        except Exception as e:
            return {'text': '', 'success': False, 'error': str(e)}

    def extract_resume_text(self, file):
        filename = file.filename.lower()
        
        try:
            if filename.endswith('.pdf'):
                return self._extract_pdf(file)
            elif filename.endswith('.txt'):
                text = file.read().decode('utf-8', errors='ignore')
                return {'text': text, 'success': True}
            elif filename.endswith('.docx'):
                return self._extract_docx(file)
            else:
                text = file.read().decode('utf-8', errors='ignore')
                return {'text': text, 'success': True}
        except Exception as e:
            return {'text': '', 'success': False, 'error': str(e)}

    def _extract_pdf(self, file):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            return {'text': text.strip(), 'success': True}
        except ImportError:
            try:
                import pdfplumber
                with pdfplumber.open(file) as pdf:
                    text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
                return {'text': text.strip(), 'success': True}
            except ImportError:
                return {'text': 'PDF text extraction requires PyPDF2 or pdfplumber.', 'success': False}

    def _extract_docx(self, file):
        try:
            from docx import Document
            doc = Document(file)
            text = '\n'.join(para.text for para in doc.paragraphs)
            return {'text': text.strip(), 'success': True}
        except ImportError:
            return {'text': 'DOCX extraction requires python-docx.', 'success': False}
