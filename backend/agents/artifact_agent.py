from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import time

class ArtifactAgent:
    def __init__(self):
        self.image_api_base = "https://image.pollinations.ai/prompt/"

    async def generate_image(self, idea_title: str) -> str:
        """
        Generates an image URL using Pollinations.ai (Free, no key).
        """
        # Clean title for URL
        safe_title = "".join(x for x in idea_title if x.isalnum() or x == " ").replace(" ", "%20")
        return f"{self.image_api_base}{safe_title}?width=800&height=600&nologo=true"

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
            
            # Title
            c.setFont("Helvetica-Bold", 24)
            c.drawString(72, height - 72, f"Proposal: {idea.title}")
            
            # Subtitle
            c.setFont("Helvetica", 14)
            c.drawString(72, height - 100, f"Status: {idea.status.upper()} | Score: {idea.total_score:.1f}/10")
            
            # Description
            c.setFont("Helvetica", 12)
            y = height - 140
            text = c.beginText(72, y)
            text.setFont("Helvetica", 12)
            
            # Simple text wrapping (very basic)
            lines = idea.description.split('\n')
            for line in lines:
                text.textLine(line[:90])  # Truncate for MVP
                if len(line) > 90:
                    text.textLine(line[90:180])
                    
            c.drawText(text)
            
            # Evaluation
            y -= (len(lines) * 15 + 40)
            c.drawString(72, y, "Evaluations:")
            y -= 20
            for ev in idea.evaluations:
                c.drawString(90, y, f"- {ev.reviewer_role}: {ev.score}/10")
                y -= 15
                
            c.save()
            return f"http://localhost:8000/artifacts/{filename}"
        except Exception as e:
            print(f"PDF Generation failed: {e}")
            return "error_generating_pdf.pdf"

    async def generate(self, idea, artifact_type: str):
        if artifact_type == "image":
            return await self.generate_image(idea.title)
        elif artifact_type == "pdf":
            return await self.generate_pdf(idea)
        return ""
