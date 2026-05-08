import os
import json
import uuid
import requests
from datetime import datetime

class InterviewChatbot:
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY', '')
        self.sessions = {}
        
        # Determine which API to use
        if self.groq_api_key:
            self.api_type = 'groq'
            self.api_url = 'https://api.groq.com/openai/v1/chat/completions'
            self.model = 'llama3-8b-8192'
        elif self.openrouter_api_key:
            self.api_type = 'openrouter'
            self.api_url = 'https://openrouter.ai/api/v1/chat/completions'
            self.model = 'meta-llama/llama-3-8b-instruct:free'
        else:
            self.api_type = 'mock'

    def _get_system_prompt(self, job_role, candidate_name, resume_text=''):
        resume_section = f"\n\nCandidate Resume Summary:\n{resume_text[:1500]}" if resume_text else ""
        return f"""You are ARIA (Advanced Recruitment Intelligence Assistant), a sophisticated AI interviewer conducting a professional job interview for a {job_role} position.

Candidate Name: {candidate_name}{resume_section}

Your personality:
- Professional yet warm and encouraging
- Ask focused, intelligent questions
- Give brief positive acknowledgment before the next question
- Mix behavioral (STAR method), technical, and situational questions
- Adapt questions based on candidate's responses
- After 6-8 questions, conduct a wrap-up

Interview phases:
1. Warm welcome and ice-breaker (1-2 questions)
2. Background and experience (2-3 questions)
3. Technical/role-specific skills (2-3 questions)
4. Behavioral questions (2-3 questions)
5. Situational/problem-solving (1-2 questions)
6. Candidate's questions and closing

Rules:
- Keep responses concise (2-4 sentences max)
- Never break character
- If candidate asks for feedback mid-interview, briefly acknowledge and continue
- Track interview flow and don't repeat questions
- Be encouraging but professional

Start by warmly welcoming the candidate and asking your first ice-breaker question."""

    def start_interview(self, job_role, candidate_name, resume_text=''):
        session_id = str(uuid.uuid4())
        system_prompt = self._get_system_prompt(job_role, candidate_name, resume_text)
        
        self.sessions[session_id] = {
            'job_role': job_role,
            'candidate_name': candidate_name,
            'messages': [],
            'system_prompt': system_prompt,
            'start_time': datetime.now().isoformat(),
            'question_count': 0
        }
        
        # Get opening message from AI
        opening = self._call_api(session_id, None, is_opening=True)
        
        return {
            'session_id': session_id,
            'message': opening,
            'role': 'assistant'
        }

    def send_message(self, user_message, session_id):
        if session_id not in self.sessions:
            return {'error': 'Session not found', 'message': 'Session expired. Please start a new interview.'}
        
        session = self.sessions[session_id]
        session['messages'].append({'role': 'user', 'content': user_message})
        session['question_count'] += 1
        
        response = self._call_api(session_id, user_message)
        session['messages'].append({'role': 'assistant', 'content': response})
        
        # Check if interview should end
        is_complete = session['question_count'] >= 10
        
        return {
            'message': response,
            'role': 'assistant',
            'question_count': session['question_count'],
            'is_complete': is_complete
        }

    def _call_api(self, session_id, user_message, is_opening=False):
        if self.api_type == 'mock':
            return self._mock_response(session_id, user_message, is_opening)
        
        session = self.sessions[session_id]
        
        messages = [{'role': 'system', 'content': session['system_prompt']}]
        messages.extend(session['messages'])
        
        if user_message and not is_opening:
            messages.append({'role': 'user', 'content': user_message})
        
        headers = {'Content-Type': 'application/json'}
        
        if self.api_type == 'groq':
            headers['Authorization'] = f'Bearer {self.groq_api_key}'
        elif self.api_type == 'openrouter':
            headers['Authorization'] = f'Bearer {self.openrouter_api_key}'
            headers['HTTP-Referer'] = 'http://localhost:5000'
            headers['X-Title'] = 'AI Interview Simulator'
        
        payload = {
            'model': self.model,
            'messages': messages,
            'max_tokens': 300,
            'temperature': 0.7
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except requests.exceptions.Timeout:
            return "I apologize for the delay. Could you please repeat your answer?"
        except Exception as e:
            print(f"API Error: {e}")
            return self._mock_response(session_id, user_message, is_opening)

    def _mock_response(self, session_id, user_message, is_opening=False):
        session = self.sessions.get(session_id, {})
        job_role = session.get('job_role', 'Software Engineer')
        candidate_name = session.get('candidate_name', 'Candidate')
        count = session.get('question_count', 0)
        
        if is_opening:
            return f"Welcome, {candidate_name}! I'm ARIA, your AI interviewer today. I'm genuinely excited to learn more about you. To break the ice — what made you interested in pursuing a {job_role} role, and what aspect of this field excites you the most?"
        
        responses = [
            f"Thank you for sharing that. Your enthusiasm really comes through! Now, tell me about your most impactful project as a {job_role}. What was your specific contribution and what was the outcome?",
            "That's a compelling example. I'd love to dig deeper — can you walk me through a situation where you had to solve a particularly complex technical problem under pressure? What was your process?",
            "Excellent approach! Strong problem-solving is critical here. Let's shift gears — describe a time when you disagreed with a teammate or manager. How did you handle it professionally?",
            "I appreciate your thoughtfulness on that. Collaboration is key in any role. Now, where do you see the intersection of your technical skills and business impact? Can you give me a concrete example?",
            f"Fascinating perspective. You've clearly thought deeply about this. For a {job_role} position, how do you stay current with rapidly evolving technologies and industry trends?",
            "That shows great initiative! One more — if you joined our team tomorrow and discovered a major process inefficiency, what would be your first steps to address it?",
            "Wonderful — you've demonstrated excellent strategic thinking. We're wrapping up now. Do you have any questions about the role, team culture, or what success looks like in this position?",
            f"Thank you so much, {candidate_name}. You've been a phenomenal interview candidate. I'll be compiling my analysis and feedback. Is there anything else you'd like to add before we close?",
            "This has been an outstanding interview. Your depth of experience and clear communication skills are impressive. The team will be in touch very soon. Thank you for your time today!",
        ]
        
        idx = min(count - 1, len(responses) - 1)
        return responses[max(0, idx)]

    def get_session_data(self, session_id):
        return self.sessions.get(session_id, {})
