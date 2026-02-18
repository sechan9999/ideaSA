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
        Idea: {idea.title} - {idea.description}
        Objective: Expand this idea into a detailed product concept.
        Constraints:
        1. Translate the core value proposition into Japanese and critique its service design.
        2. Translate into German and critique its engineering feasibility.
        3. Synthesize these diverse perspectives (Service + Engineering) into a robust English specification.
        Output: Updated JSON object with 'expanded_description', 'feasibility_notes', 'market_validation_points'.
        """
        
        refined_data = await self.llm.generate_json(prompt)
        
        # Merge refined data
        if isinstance(refined_data, dict):
            idea.description += f"\n\n## Refinement\n{refined_data.get('expanded_description', '')}"
            idea.market_score = refined_data.get('market_validation_points', 0) if isinstance(refined_data.get('market_validation_points'), (int, float)) else 0
            idea.tech_score = refined_data.get('feasibility_notes', 0) if isinstance(refined_data.get('feasibility_notes'), (int, float)) else 0
            idea.status = "refined"
            
        return idea
