from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import os

# Register CJK font for Korean/Japanese/Chinese support
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))

# Font helpers: use CJK font when text contains non-ASCII characters
_CJK_FONT = 'HeiseiMin-W3'
_LATIN_FONT = 'Helvetica'
_LATIN_FONT_BOLD = 'Helvetica-Bold'

def _has_cjk(text: str) -> bool:
    return any(ord(ch) > 127 for ch in text)

def _pick_font(text: str, bold=False) -> str:
    if _has_cjk(text):
        return _CJK_FONT
    return _LATIN_FONT_BOLD if bold else _LATIN_FONT

def _safe_text(text: str) -> str:
    """Remove surrogate characters that can't be encoded."""
    return text.encode('utf-8', errors='replace').decode('utf-8')


class ArtifactAgent:
    async def generate_pdf(self, idea) -> str:
        """
        Generates a PDF proposal for the idea.
        """
        filename = f"{idea.id}_proposal.pdf"
        # Match ARTIFACTS_DIR in main.py
        base_path = os.path.dirname(os.path.abspath(__file__)) # agents/
        artifacts_path = os.path.join(base_path, "..", "artifacts") # backend/artifacts
        filepath = os.path.join(artifacts_path, filename)

        # Ensure artifacts dir exists
        os.makedirs(artifacts_path, exist_ok=True)

        try:
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter

            title_text = _safe_text(f"Proposal: {idea.title}")
            subtitle_text = f"Status: {idea.status.upper()} | Score: {idea.total_score:.1f}/10"

            # Title
            c.setFont(_pick_font(title_text, bold=True), 24)
            c.drawString(72, height - 72, title_text)

            # Subtitle
            c.setFont(_pick_font(subtitle_text), 14)
            c.drawString(72, height - 100, subtitle_text)

            # Description
            y = height - 140
            desc = _safe_text(idea.description)
            font = _pick_font(desc)
            text = c.beginText(72, y)
            text.setFont(font, 12)

            # Simple text wrapping
            lines = desc.split('\n')
            for line in lines:
                # Wrap long lines at ~80 chars
                while len(line) > 80:
                    text.textLine(line[:80])
                    line = line[80:]
                text.textLine(line)

            c.drawText(text)

            # Evaluation
            y -= (len(lines) * 15 + 40)
            c.setFont(_LATIN_FONT, 12)
            c.drawString(72, y, "Evaluations:")
            y -= 20
            for ev in idea.evaluations:
                ev_text = _safe_text(f"- {ev.reviewer_role}: {ev.score}/10")
                c.setFont(_pick_font(ev_text), 11)
                c.drawString(90, y, ev_text)
                y -= 15

            c.save()
            return f"http://localhost:8000/artifacts/{filename}"
        except Exception as e:
            print(f"PDF Generation failed: {e}")
            return "error_generating_pdf.pdf"

    async def generate(self, idea, artifact_type: str):
        if artifact_type == "pdf":
            return await self.generate_pdf(idea)
        return ""
