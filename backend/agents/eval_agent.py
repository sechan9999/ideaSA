from models.idea import Idea, Evaluation
from services.llm_service import LLMService

class EvalAgent:
    def __init__(self):
        self.llm = LLMService()

    async def evaluate(self, idea: Idea) -> Idea:
        """
        Uses multiple reviewer personas to score the idea.
        """
        personas = ["Market Analyst", "Tech Lead", "Patent Attorney"]
        evaluations = []
        scores = []
        
        for p in personas:
            prompt = f"As a {p}, critique this idea: {idea.title}. Provide a score (1-10) and feedback. Output JSON: {{score: float, feedback: str}}"
            res = await self.llm.generate_json(prompt)
            score = res.get('score', 5.0) if isinstance(res, dict) else 5.0
            feedback = res.get('feedback', 'No feedback provided.') if isinstance(res, dict) else "Generic Feedback"
            
            # Create Evaluation object
            eval_obj = Evaluation(reviewer_role=p, score=score, feedback=feedback)
            evaluations.append(eval_obj)
            scores.append(score)
            
        idea.evaluations = evaluations
        idea.total_score = sum(scores) / len(scores) if scores else 0
        idea.status = "evaluated"
        
        return idea
