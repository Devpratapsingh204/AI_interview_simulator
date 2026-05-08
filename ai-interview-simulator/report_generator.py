import os
import tempfile
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.reportlab_available = False
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.colors import HexColor, white, black
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
            from reportlab.lib.units import inch, cm
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            self.reportlab_available = True
            print("✅ ReportLab loaded")
        except ImportError:
            print("⚠️  ReportLab not available — falling back to text report")

    def generate(self, report_data):
        if self.reportlab_available:
            return self._generate_pdf(report_data)
        else:
            return self._generate_text(report_data)

    def _generate_pdf(self, data):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor, white, black
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.units import inch, cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        doc = SimpleDocTemplate(tmp.name, pagesize=A4,
                                 leftMargin=1.5*cm, rightMargin=1.5*cm,
                                 topMargin=1.5*cm, bottomMargin=1.5*cm)

        # Colors
        dark_bg = HexColor('#0a0e1a')
        neon_cyan = HexColor('#00f5ff')
        neon_purple = HexColor('#a855f7')
        accent_green = HexColor('#00ff88')
        text_color = HexColor('#e2e8f0')
        muted = HexColor('#64748b')
        card_bg = HexColor('#111827')

        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=24,
                                      textColor=neon_cyan, alignment=TA_CENTER, spaceAfter=4)
        subtitle_style = ParagraphStyle('Subtitle', fontName='Helvetica', fontSize=11,
                                         textColor=muted, alignment=TA_CENTER, spaceAfter=12)
        heading_style = ParagraphStyle('Heading', fontName='Helvetica-Bold', fontSize=13,
                                        textColor=neon_purple, spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=10,
                                     textColor=text_color, spaceAfter=4, leading=14)
        score_style = ParagraphStyle('Score', fontName='Helvetica-Bold', fontSize=20,
                                      textColor=accent_green, alignment=TA_CENTER)

        elements = []
        
        # Header
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph("◈ ARIA INTERVIEW REPORT ◈", title_style))
        elements.append(Paragraph("Advanced Recruitment Intelligence Assistant", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=neon_cyan))
        elements.append(Spacer(1, 0.4*cm))

        # Candidate Info Table
        scores = data.get('scores', {})
        confidence = scores.get('confidence', 72)
        overall = scores.get('overall', 75)
        communication = scores.get('communication', 70)
        technical = scores.get('technical', 68)

        info_data = [
            ['CANDIDATE', data.get('candidate_name', 'N/A'), 'ROLE', data.get('job_role', 'N/A')],
            ['DATE', datetime.now().strftime('%B %d, %Y'), 'DURATION', f"{data.get('duration', 0)//60} min {data.get('duration', 0)%60} sec"],
            ['OVERALL SCORE', f"{overall}/100", 'CONFIDENCE', f"{confidence}/100"],
        ]
        
        info_table = Table(info_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 6*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), card_bg),
            ('BACKGROUND', (2, 0), (2, -1), card_bg),
            ('TEXTCOLOR', (0, 0), (0, -1), neon_cyan),
            ('TEXTCOLOR', (2, 0), (2, -1), neon_cyan),
            ('TEXTCOLOR', (1, 0), (1, -1), text_color),
            ('TEXTCOLOR', (3, 0), (3, -1), text_color),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, muted),
            ('ROWBACKGROUND', (0, 0), (-1, -1), [HexColor('#0d1117'), HexColor('#111827'), HexColor('#0d1117')]),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.6*cm))

        # Score Breakdown
        elements.append(Paragraph("▸ PERFORMANCE SCORES", heading_style))
        score_data = [
            ['METRIC', 'SCORE', 'RATING'],
            ['Overall Performance', f'{overall}/100', self._rating(overall)],
            ['Communication Skills', f'{communication}/100', self._rating(communication)],
            ['Technical Knowledge', f'{technical}/100', self._rating(technical)],
            ['Confidence Level', f'{confidence}/100', self._rating(confidence)],
            ['Eye Contact & Presence', f"{scores.get('presence', 65)}/100", self._rating(scores.get('presence', 65))],
        ]
        
        score_table = Table(score_data, colWidths=[8*cm, 4*cm, 7*cm])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), neon_purple),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUND', (0, 1), (-1, -1), [HexColor('#0d1117'), HexColor('#111827')]),
            ('TEXTCOLOR', (0, 1), (-1, -1), text_color),
            ('TEXTCOLOR', (1, 1), (1, -1), accent_green),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, muted),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 0.6*cm))

        # Emotion Summary
        emotion_summary = data.get('emotion_summary', {})
        if emotion_summary:
            elements.append(Paragraph("▸ EMOTION ANALYSIS", heading_style))
            emotion_rows = [['EMOTION', 'FREQUENCY', 'PERCENTAGE']]
            total = sum(emotion_summary.values()) or 1
            for emotion, count in sorted(emotion_summary.items(), key=lambda x: -x[1]):
                pct = (count / total) * 100
                emotion_rows.append([emotion.upper(), str(count), f'{pct:.1f}%'])
            
            emotion_table = Table(emotion_rows, colWidths=[7*cm, 5*cm, 7*cm])
            emotion_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1e3a5f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), neon_cyan),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUND', (0, 1), (-1, -1), [HexColor('#0d1117'), HexColor('#111827')]),
                ('TEXTCOLOR', (0, 1), (-1, -1), text_color),
                ('GRID', (0, 0), (-1, -1), 0.5, muted),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ]))
            elements.append(emotion_table)
            elements.append(Spacer(1, 0.6*cm))

        # Feedback
        feedback_list = data.get('feedback', [])
        if feedback_list:
            elements.append(Paragraph("▸ AI FEEDBACK & RECOMMENDATIONS", heading_style))
            for i, fb in enumerate(feedback_list[:8], 1):
                if isinstance(fb, dict):
                    msg = fb.get('message', str(fb))
                else:
                    msg = str(fb)
                elements.append(Paragraph(f"  {i}. {msg}", body_style))
            elements.append(Spacer(1, 0.4*cm))

        # Transcript Highlights
        transcript = data.get('transcript', [])
        if transcript:
            elements.append(Paragraph("▸ INTERVIEW TRANSCRIPT", heading_style))
            for entry in transcript[:12]:
                role = entry.get('role', 'unknown').upper()
                msg = entry.get('content', '')[:200]
                color = neon_cyan if role == 'ASSISTANT' else text_color
                prefix_style = ParagraphStyle('ts', fontName='Helvetica-Bold', fontSize=8,
                                               textColor=color, spaceAfter=1)
                content_style = ParagraphStyle('tc', fontName='Helvetica', fontSize=9,
                                                textColor=text_color, spaceAfter=5, leading=12)
                elements.append(Paragraph(f"[{role}]", prefix_style))
                elements.append(Paragraph(msg + ('...' if len(entry.get('content','')) > 200 else ''), content_style))

        # Footer
        elements.append(Spacer(1, 0.5*cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=neon_purple))
        footer_style = ParagraphStyle('Footer', fontName='Helvetica', fontSize=8,
                                       textColor=muted, alignment=TA_CENTER, spaceBefore=6)
        elements.append(Paragraph(
            f"Generated by ARIA — AI Interview Simulator | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Confidential",
            footer_style
        ))

        doc.build(elements)
        return tmp.name

    def _rating(self, score):
        if score >= 85: return "★★★★★ EXCELLENT"
        if score >= 70: return "★★★★☆ GOOD"
        if score >= 55: return "★★★☆☆ AVERAGE"
        if score >= 40: return "★★☆☆☆ NEEDS WORK"
        return "★☆☆☆☆ POOR"

    def _generate_text(self, data):
        """Fallback text report as PDF workaround"""
        tmp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w')
        scores = data.get('scores', {})
        
        content = f"""
=====================================
   ARIA INTERVIEW REPORT
=====================================

Candidate: {data.get('candidate_name', 'N/A')}
Role: {data.get('job_role', 'N/A')}
Date: {datetime.now().strftime('%B %d, %Y %H:%M')}
Duration: {data.get('duration', 0)} seconds

--- SCORES ---
Overall: {scores.get('overall', 0)}/100
Confidence: {scores.get('confidence', 0)}/100
Communication: {scores.get('communication', 0)}/100

--- FEEDBACK ---
"""
        for fb in data.get('feedback', []):
            if isinstance(fb, dict):
                content += f"• {fb.get('message', '')}\n"
            else:
                content += f"• {fb}\n"

        content += "\n=====================================\n"
        tmp.write(content)
        tmp.close()
        return tmp.name
