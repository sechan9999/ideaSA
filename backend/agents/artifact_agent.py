from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import os

# Register CJK font for Korean/Japanese/Chinese support
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))

_CJK_FONT = 'HeiseiMin-W3'
_LATIN_FONT = 'Helvetica'
_LATIN_FONT_BOLD = 'Helvetica-Bold'

MARGIN = 72  # 1 inch
PAGE_W, PAGE_H = letter
CONTENT_W = PAGE_W - 2 * MARGIN  # usable text width


def _has_cjk(text: str) -> bool:
    return any(ord(ch) > 127 for ch in text)


def _pick_font(text: str, bold=False) -> str:
    if _has_cjk(text):
        return _CJK_FONT
    return _LATIN_FONT_BOLD if bold else _LATIN_FONT


def _safe_text(text: str) -> str:
    return text.encode('utf-8', errors='replace').decode('utf-8')


def _wrap_lines(text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    result = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            result.append('')
            continue
        words = paragraph.split(' ')
        current_line = ''
        for word in words:
            test = f"{current_line} {word}".strip()
            w = pdfmetrics.stringWidth(test, font_name, font_size)
            if w <= max_width:
                current_line = test
            else:
                if current_line:
                    result.append(current_line)
                # If single word is wider than line, force-break it
                if pdfmetrics.stringWidth(word, font_name, font_size) > max_width:
                    while word:
                        for i in range(len(word), 0, -1):
                            if pdfmetrics.stringWidth(word[:i], font_name, font_size) <= max_width:
                                result.append(word[:i])
                                word = word[i:]
                                break
                        else:
                            result.append(word)
                            word = ''
                else:
                    current_line = word
        if current_line:
            result.append(current_line)
    return result


class ArtifactAgent:
    async def generate_pdf(self, idea) -> str:
        filename = f"{idea.id}_proposal.pdf"
        base_path = os.path.dirname(os.path.abspath(__file__))
        artifacts_path = os.path.join(base_path, "..", "artifacts")
        filepath = os.path.join(artifacts_path, filename)
        os.makedirs(artifacts_path, exist_ok=True)

        try:
            c = canvas.Canvas(filepath, pagesize=letter)
            y = PAGE_H - MARGIN

            # --- Title (wrapped) ---
            title_text = _safe_text(f"Proposal: {idea.title}")
            title_font = _pick_font(title_text, bold=True)
            title_size = 22
            title_lines = _wrap_lines(title_text, title_font, title_size, CONTENT_W)
            for line in title_lines:
                c.setFont(title_font, title_size)
                c.drawString(MARGIN, y, line)
                y -= title_size + 6

            y -= 4

            # --- Subtitle ---
            subtitle = f"Status: {idea.status.upper()}  |  Score: {idea.total_score:.1f} / 10"
            c.setFont(_LATIN_FONT, 12)
            c.drawString(MARGIN, y, subtitle)
            y -= 28

            # --- Divider ---
            c.setStrokeColorRGB(0.7, 0.7, 0.7)
            c.line(MARGIN, y, PAGE_W - MARGIN, y)
            y -= 20

            # --- Description (wrapped) ---
            desc = _safe_text(idea.description)
            desc_font = _pick_font(desc)
            desc_size = 11
            leading = desc_size + 4
            desc_lines = _wrap_lines(desc, desc_font, desc_size, CONTENT_W)

            for line in desc_lines:
                if y < MARGIN + 40:
                    c.showPage()
                    y = PAGE_H - MARGIN
                # Section headers get bold
                if line.startswith('## '):
                    c.setFont(_pick_font(line, bold=True), 13)
                    y -= 6
                    c.drawString(MARGIN, y, line.replace('## ', ''))
                    y -= 20
                else:
                    c.setFont(desc_font, desc_size)
                    c.drawString(MARGIN, y, line)
                    y -= leading

            y -= 16

            # --- Evaluations ---
            if idea.evaluations:
                if y < MARGIN + 80:
                    c.showPage()
                    y = PAGE_H - MARGIN

                c.setStrokeColorRGB(0.7, 0.7, 0.7)
                c.line(MARGIN, y, PAGE_W - MARGIN, y)
                y -= 18

                c.setFont(_LATIN_FONT_BOLD, 13)
                c.drawString(MARGIN, y, "Evaluations")
                y -= 20

                for ev in idea.evaluations:
                    if y < MARGIN + 30:
                        c.showPage()
                        y = PAGE_H - MARGIN

                    role_text = _safe_text(f"{ev.reviewer_role}: {ev.score}/10")
                    c.setFont(_pick_font(role_text, bold=True), 11)
                    c.drawString(MARGIN + 10, y, role_text)
                    y -= 16

                    feedback = _safe_text(ev.feedback) if hasattr(ev, 'feedback') and ev.feedback else ''
                    if feedback:
                        fb_font = _pick_font(feedback)
                        fb_lines = _wrap_lines(feedback, fb_font, 10, CONTENT_W - 20)
                        for fb_line in fb_lines:
                            if y < MARGIN + 20:
                                c.showPage()
                                y = PAGE_H - MARGIN
                            c.setFont(fb_font, 10)
                            c.drawString(MARGIN + 20, y, fb_line)
                            y -= 14
                    y -= 8

            c.save()
            return f"http://localhost:8000/artifacts/{filename}"
        except Exception as e:
            print(f"PDF Generation failed: {e}")
            return "error_generating_pdf.pdf"

    async def generate(self, idea, artifact_type: str):
        if artifact_type == "pdf":
            return await self.generate_pdf(idea)
        return ""
