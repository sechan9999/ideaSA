import os
import random
import hashlib
from typing import Any, Dict


class LLMService:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    async def generate_json(self, prompt: str, schema: Dict = None) -> Any:
        if self.openai_key:
            return await self._call_openai(prompt, schema)
        elif self.anthropic_key:
            return await self._call_anthropic(prompt, schema)
        else:
            return self._mock_response(prompt)

    async def _call_openai(self, prompt: str, schema: Dict):
        return self._mock_response(prompt)

    async def _call_anthropic(self, prompt: str, schema: Dict):
        return self._mock_response(prompt)

    def _mock_response(self, prompt: str):
        p = prompt.lower()
        if "refine" in p:
            return self._mock_refine(prompt)
        elif "evaluate" in p or "critique" in p:
            return self._mock_evaluate(prompt)
        elif "seed" in p or "generate" in p:
            return self._mock_seeds(prompt)
        return {}

    def _mock_seeds(self, prompt: str) -> list:
        """Generate diverse seeds based on the topic in the prompt."""
        # Extract topic hint from prompt for variety
        seed = _prompt_hash(prompt)
        rng = random.Random(seed)

        templates = [
            {
                "angles": ["optimization", "analytics", "automation"],
                "formats": [
                    ("Smart {topic} Optimizer", "An AI-powered platform that analyzes {topic} patterns and automatically optimizes resource allocation using real-time data streams and predictive modeling."),
                    ("{topic} Analytics Dashboard", "Interactive visualization tool that aggregates {topic} metrics from multiple sources, providing actionable insights through customizable charts and anomaly detection."),
                    ("Automated {topic} Pipeline", "End-to-end automation framework for {topic} workflows that reduces manual intervention by 80% through intelligent task orchestration and error recovery."),
                ]
            },
            {
                "angles": ["education", "accessibility", "community"],
                "formats": [
                    ("{topic} Learning Hub", "Gamified educational platform that teaches {topic} concepts through interactive simulations, progress tracking, and personalized learning paths."),
                    ("{topic} for Everyone", "Accessibility-first tool that democratizes {topic} knowledge with simplified interfaces, multilingual support, and step-by-step guided experiences."),
                    ("{topic} Community Platform", "Social platform connecting {topic} enthusiasts with mentorship matching, collaborative projects, and knowledge-sharing forums."),
                ]
            },
            {
                "angles": ["marketplace", "prediction", "monitoring"],
                "formats": [
                    ("{topic} Marketplace", "Decentralized marketplace connecting {topic} providers and consumers with transparent pricing, reputation scoring, and escrow-based transactions."),
                    ("{topic} Predictor", "Machine learning system that forecasts {topic} trends using historical data, sentiment analysis, and multi-factor regression models."),
                    ("{topic} Monitor", "Real-time monitoring system for {topic} with configurable alerts, health dashboards, and automated incident response workflows."),
                ]
            },
        ]

        # Pick a template set based on prompt hash, then shuffle
        group = templates[seed % len(templates)]
        formats = list(group["formats"])
        rng.shuffle(formats)

        # Extract a rough topic from the prompt
        topic = _extract_topic(prompt)

        ideas = []
        for title_tmpl, desc_tmpl in formats[:3]:
            ideas.append({
                "title": title_tmpl.format(topic=topic),
                "description": desc_tmpl.format(topic=topic),
                "keywords": rng.sample(group["angles"] + ["AI", "data", "scale"], 3),
            })
        return ideas

    def _mock_refine(self, prompt: str) -> dict:
        """Generate a unique refinement based on the idea content."""
        seed = _prompt_hash(prompt)
        rng = random.Random(seed)

        perspectives = [
            "From a service design perspective, the user journey should prioritize frictionless onboarding with a 3-step setup wizard and progressive disclosure of advanced features.",
            "Engineering analysis suggests a microservices architecture with event-driven communication. Key technical risks include data synchronization latency and cold-start performance.",
            "Market validation indicates a $2.4B addressable market growing at 18% CAGR. Primary competitors lack real-time capabilities, creating a significant differentiation opportunity.",
            "Cross-cultural analysis reveals strong demand in Asian markets for mobile-first experiences, while European users prioritize data privacy and GDPR compliance.",
            "Financial modeling shows break-even within 14 months at 500 paid users. The freemium-to-paid conversion target of 4.5% is achievable given industry benchmarks.",
        ]

        selected = rng.sample(perspectives, min(3, len(perspectives)))

        return {
            "expanded_description": "\n\n".join(selected),
            "feasibility_notes": round(rng.uniform(6.0, 9.5), 1),
            "market_validation_points": round(rng.uniform(6.5, 9.0), 1),
        }

    def _mock_evaluate(self, prompt: str) -> dict:
        """Generate varied evaluation scores."""
        seed = _prompt_hash(prompt)
        rng = random.Random(seed)

        feedbacks = [
            "Strong market potential with clear customer pain points. Recommend validating with 20+ customer interviews before building.",
            "Technical approach is sound but requires careful attention to scalability. Consider starting with a focused MVP targeting a single vertical.",
            "Novel approach that differentiates from existing solutions. IP protection strategy recommended given the innovative algorithmic core.",
            "Good alignment with current market trends. Revenue model needs refinement - consider value-based pricing over subscription.",
            "Solid engineering plan but competitive moat is weak. Suggest building network effects or data advantages early.",
            "Compelling vision with strong team-market fit. Key risk is go-to-market timing - recommend accelerated launch timeline.",
        ]

        return {
            "score": round(rng.uniform(5.5, 9.5), 1),
            "feedback": rng.choice(feedbacks),
        }


def _prompt_hash(prompt: str) -> int:
    """Deterministic but varied hash from prompt content."""
    return int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)


def _extract_topic(prompt: str) -> str:
    """Extract topic from prompt context string."""
    p = prompt.lower()
    # Try to find "recent developments in X include"
    marker = "recent developments in "
    idx = p.find(marker)
    if idx != -1:
        rest = prompt[idx + len(marker):]
        end = rest.find(" include")
        if end != -1:
            return rest[:end].strip()

    # Try "context:" pattern
    marker2 = "context:"
    idx2 = p.find(marker2)
    if idx2 != -1:
        rest = prompt[idx2 + len(marker2):idx2 + len(marker2) + 60]
        return rest.strip().split(".")[0].strip()[:40]

    # Fallback: use first meaningful words
    words = [w for w in prompt.split() if len(w) > 3 and w.isalpha()]
    return " ".join(words[:3]) if words else "Innovation"
