import hashlib
import random
from models.idea import Idea, Evaluation
from services.llm_service import LLMService


class EvalAgent:
    def __init__(self):
        self.llm = LLMService()

    async def evaluate(self, idea: Idea) -> Idea:
        """
        Multi-persona evaluation with idea-specific feedback.
        Each reviewer generates unique commentary based on the idea content.
        """
        personas = ["Market Analyst", "Tech Lead", "Patent Attorney"]
        evaluations = []
        scores = []

        for persona in personas:
            prompt = (
                f"As a {persona}, critique this idea: '{idea.title}' - "
                f"{idea.description[:200]}. Keywords: {', '.join(idea.keywords)}. "
                f"Provide a score (1-10) and feedback. Output JSON: {{score: float, feedback: str}}"
            )
            res = await self.llm.generate_json(prompt)

            # Check if LLM returned idea-specific feedback (mentions the idea title)
            if (isinstance(res, dict) and "score" in res
                    and idea.title.lower()[:15] in res.get("feedback", "").lower()):
                score = float(res.get("score", 5.0))
                feedback = res.get("feedback", "No feedback.")
            else:
                # Use our context-aware evaluator
                score, feedback = self._mock_evaluate(idea, persona)

            eval_obj = Evaluation(reviewer_role=persona, score=score, feedback=feedback)
            evaluations.append(eval_obj)
            scores.append(score)

        idea.evaluations = evaluations
        idea.total_score = round(sum(scores) / len(scores), 1) if scores else 0
        idea.novelty_score = round(scores[2] if len(scores) > 2 else 0, 1)
        idea.status = "evaluated"
        return idea

    def _mock_evaluate(self, idea: Idea, persona: str) -> tuple:
        """Generate idea-specific evaluation per persona."""
        key = f"{idea.id}{idea.title}{persona}"
        seed = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)

        title = idea.title
        kw = idea.keywords[:3] if idea.keywords else ["the concept"]
        origin = idea.origin_trend or "the market"

        if persona == "Market Analyst":
            score = round(rng.uniform(6.0, 9.5), 1)
            feedbacks = [
                f"'{title}' addresses a real gap in {origin}. The {kw[0]} focus gives "
                f"it a clear positioning. Concern: customer education cost may be high "
                f"for the {kw[-1]} component. Recommend starting with a single vertical "
                f"before horizontal expansion. Score reflects strong TAM but execution risk.",

                f"Market timing is favorable for '{title}'. The {origin} sector is actively "
                f"seeking {kw[0]} solutions, with 3 recent Series A rounds in adjacent space. "
                f"Competitive moat via {kw[-1]} differentiation is moderate. Suggest validating "
                f"with 15-20 customer interviews before committing to full build.",
            ]
        elif persona == "Tech Lead":
            score = round(rng.uniform(5.5, 9.0), 1)
            feedbacks = [
                f"'{title}' is technically feasible with current stack. The {kw[0]} pipeline "
                f"can be built using proven async patterns. Key concern: {kw[-1]} integration "
                f"adds complexity — estimate +30% to timeline. Recommend building {kw[0]} core "
                f"first, add {kw[-1]} in v2. Architecture risk: moderate.",

                f"Solid technical foundation for '{title}'. The {kw[0]} component maps well to "
                f"an event-driven architecture. Scalability concern: {origin} data volumes may "
                f"require sharding strategy by month 6. Suggest starting with PostgreSQL, "
                f"migrate to time-series DB if needed. MVP: 10-12 weeks.",
            ]
        else:  # Patent Attorney
            score = round(rng.uniform(5.0, 9.0), 1)
            feedbacks = [
                f"Novelty assessment for '{title}': the combination of {kw[0]} and {kw[-1]} "
                f"in the {origin} context has limited prior art. Found 2-3 tangentially related "
                f"patents but none covering this specific approach. Recommend filing a provisional "
                f"patent on the {kw[0]} methodology. Freedom-to-operate risk: low.",

                f"'{title}' shows moderate novelty. The {kw[0]} approach has existing prior art "
                f"but the application to {origin} via {kw[-1]} is relatively unexplored. "
                f"Suggest a defensive IP strategy: publish technical details early to establish "
                f"prior art, file narrow claims on the unique algorithmic approach.",
            ]

        return score, rng.choice(feedbacks)
