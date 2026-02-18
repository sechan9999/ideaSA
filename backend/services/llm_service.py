import os
from typing import List, Dict, Any
import json
import random

class LLMService:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        # Mock responses for MVP without keys
        self.mock_seeds = [
            {"title": "Smart Logistics Optimization", "description": "Using AI agents to optimize..."},
            {"title": "Biodegradable Packaging 2.0", "description": "Using nanocellulose..."},
            {"title": "Personalized Education Platform", "description": "Adjusting curriculum in real-time..."}
        ]

    async def generate_json(self, prompt: str, schema: Dict = None) -> Any:
        # Tries to call real LLM, falls back to mock
        if self.openai_key:
            return await self._call_openai(prompt, schema)
        elif self.anthropic_key:
            return await self._call_anthropic(prompt, schema)
        else:
            print("No API keys found. Returning Mock Data.")
            return self._mock_response(prompt)

    async def _call_openai(self, prompt: str, schema: Dict):
        # Implementation omitted for brevity in this step, but would use openai client
        # Returning mock for safety unless user fills .env
        return self._mock_response(prompt)

    def _mock_response(self, prompt: str):
        p = prompt.lower()
        if "seed" in p or "generate" in p and "refine" not in p and "evaluate" not in p:
            return [
                {"title": f"Idea {i}", "description": f"Draft description based on prompt: {prompt[:20]}...", "origin": "mock", "keywords": ["mock", "idea"]} 
                for i in range(3)
            ]
        elif "refine" in prompt.lower():
            return {
                "title": "Refined Idea",
                "description": "Expanded description with more technical details...",
                "market_score": 8.5,
                "tech_score": 7.0,
                "novelty_score": 9.0
            }
        elif "evaluate" in prompt.lower():
            return {
                "score": random.uniform(5, 10),
                "feedback": "Strong market potential but technical feasibility is challenging."
            }
        return {}

    async def generate_image_prompt(self, idea_description: str) -> str:
        return f"Hyper-realistic editorial photo of {idea_description[:50]}..."
