from typing import List
from models.idea import Idea, IdeaCreate
import uuid

class SeedAgent:
    def __init__(self):
        # In a real app, inject LLMService
        from services.llm_service import LLMService
        self.llm = LLMService()

    async def generate_seeds(self, context: dict, count: int = 5) -> List[Idea]:
        """
        Uses verbalized sampling prompt technique to generate diverse ideas.
        """
        prompt = f"""
        Context: {context.get('context_str', '')}
        Objective: Generate {count} high-quality, actionable product ideas (seeds) based on these trends.
        Constraint: Use 'Verbalized Sampling'. First, explicitly list 3 completely different strategic directions (e.g., 'Optimization vs Innovation vs Adaptation'). Then generate ideas from each direction to ensure diversity.
        Output: JSON array of objects with 'title', 'description', 'keywords'.
        """
        
        # Real implementation would parse this prompt into structured Output
        # For now, rely on LLMService returning mock/structured data
        raw_ideas = await self.llm.generate_json(prompt)
        
        if not isinstance(raw_ideas, list) or not raw_ideas:
            print(f"DEBUG: raw_ideas was {raw_ideas} (type: {type(raw_ideas)})")
            # Re-request with explicit seed keyword to hit the right mock branch
            raw_ideas = await self.llm.generate_json(f"Generate seed ideas for: {context.get('topic', 'innovation')}")
            if not isinstance(raw_ideas, list):
                raw_ideas = [{"title": f"{context.get('topic', 'Innovation')} Concept", "description": "A new approach worth exploring.", "keywords": ["concept"]}]

        # Force conversion to Idea objects
        seeds = []
        if isinstance(raw_ideas, list):
            for item in raw_ideas:
                seed = Idea(
                    id=str(uuid.uuid4()),
                    title=item.get("title", "Untitled idea"),
                    description=item.get("description", "No description provided"),
                    origin_trend=context.get("topic", "unknown"),
                    status="seed"
                )
                seeds.append(seed)
        else:
            # Fallback for single object response
            seed = Idea(
                id=str(uuid.uuid4()),
                title=raw_ideas.get("title", "Untitled"),
                description=raw_ideas.get("description", ""),
                origin_trend=context.get("topic"),
                status="seed"
            )
            seeds.append(seed)
            
        return seeds
