from models.idea import Idea
from services.llm_service import LLMService


class RefineAgent:
    def __init__(self):
        self.llm = LLMService()

    async def refine(self, idea: Idea) -> Idea:
        """
        Uses multilingual prompting and multi-perspective reflection to refine ideas.
        """
        prompt = f"""
        Refine this idea:
        Title: {idea.title}
        Description: {idea.description}
        Objective: Expand into a detailed product concept with service design, engineering feasibility, and market validation.
        Output: JSON with 'expanded_description', 'feasibility_notes' (float), 'market_validation_points' (float).
        """

        refined_data = await self.llm.generate_json(prompt)

        if isinstance(refined_data, dict):
            expanded = refined_data.get('expanded_description', '')
            if expanded:
                idea.description += f"\n\n## Refinement\n{expanded}"

            try:
                idea.market_score = float(refined_data.get('market_validation_points', 0))
            except (ValueError, TypeError):
                idea.market_score = 0.0

            try:
                idea.tech_score = float(refined_data.get('feasibility_notes', 0))
            except (ValueError, TypeError):
                idea.tech_score = 0.0

        idea.status = "refined"
        return idea
