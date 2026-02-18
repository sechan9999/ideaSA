from typing import List
from models.idea import Idea
from services.llm_service import LLMService
import uuid
import hashlib
import random


# 3 strategic directions for Verbalized Sampling
DIRECTIONS = [
    {
        "name": "Optimization",
        "angle": "Improve efficiency, reduce cost, or automate existing processes",
        "template": "{topic} Optimizer: {desc}",
    },
    {
        "name": "Innovation",
        "angle": "Create entirely new products, services, or market categories",
        "template": "Next-Gen {topic}: {desc}",
    },
    {
        "name": "Adaptation",
        "angle": "Apply proven concepts from other domains to this space",
        "template": "{topic} Reimagined: {desc}",
    },
]


class SeedAgent:
    def __init__(self):
        self.llm = LLMService()

    async def generate_seeds(self, context: dict, count: int = 5) -> List[Idea]:
        """
        Research-grounded seed generation using Verbalized Sampling.
        Uses trend context (papers, patents, keywords) to generate diverse ideas
        from 3 explicit strategic directions.
        """
        topic = context.get("topic", "innovation")
        keywords = context.get("keywords", [])
        papers = context.get("papers", [])
        patents = context.get("patents", [])
        keyword_book = context.get("keyword_book_str", "")

        prompt = f"""
        Keyword Book: {keyword_book}

        Context: {context.get('context_str', '')}

        Objective: Generate {count} research-grounded product ideas for '{topic}'.

        Strategy (Verbalized Sampling - 3 directions):
        1. Optimization: Improve efficiency or automate existing processes
        2. Innovation: Create entirely new products or market categories
        3. Adaptation: Apply proven concepts from other domains

        Generate at least 1 idea per direction. Each idea MUST reference specific
        keywords from the keyword book.

        Output: JSON array with 'title', 'description', 'keywords', 'direction'.
        """

        raw_ideas = await self.llm.generate_json(prompt)

        # Use research-grounded generation unless LLM returned ideas with 'direction' field
        # (indicating it understood the Verbalized Sampling instruction)
        has_directions = (
            isinstance(raw_ideas, list) and raw_ideas
            and isinstance(raw_ideas[0], dict) and "direction" in raw_ideas[0]
        )
        if not has_directions:
            raw_ideas = self._generate_research_seeds(topic, keywords, papers, patents, count)

        # Build paper/patent evidence URLs
        evidence_urls = []
        for p in papers[:3]:
            url = p.get("url") or p.get("doi", "")
            if url:
                evidence_urls.append(url)

        seeds = []
        for i, item in enumerate(raw_ideas[:count]):
            seed = Idea(
                id=str(uuid.uuid4()),
                title=item.get("title", f"{topic} Concept {i+1}"),
                description=item.get("description", ""),
                origin_trend=topic,
                keywords=item.get("keywords", keywords[:3]),
                evidence_urls=evidence_urls[:2],
                status="seed",
            )
            seeds.append(seed)

        return seeds

    def _generate_research_seeds(
        self, topic: str, keywords: List[str], papers: List[dict], patents: List[dict], count: int
    ) -> List[dict]:
        """Generate diverse seeds grounded in actual research data."""
        seed_val = int(hashlib.md5(topic.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed_val)

        # Build reference strings
        paper_refs = []
        for p in papers[:5]:
            ref = f"'{p.get('title', '?')}' ({p.get('year', '?')})"
            paper_refs.append(ref)

        patent_refs = []
        for p in patents[:3]:
            patent_refs.append(p.get("patent_title", "?"))

        kw = keywords[:10] if keywords else ["analysis", "optimization", "platform"]

        ideas = []
        for i, direction in enumerate(DIRECTIONS):
            # Pick different keywords for each direction
            dir_kw = kw[i * 3: i * 3 + 3] if len(kw) > i * 3 else kw[:3]
            rng.shuffle(dir_kw)

            ref_paper = paper_refs[i] if i < len(paper_refs) else "recent research"

            if direction["name"] == "Optimization":
                title = f"Smart {topic.title()} {dir_kw[0].title()} Engine"
                desc = (
                    f"An AI-powered platform that optimizes {topic} through {dir_kw[0]} "
                    f"and {dir_kw[1] if len(dir_kw) > 1 else 'analytics'}. "
                    f"Building on research from {ref_paper}, this system automates "
                    f"pattern detection and resource allocation using real-time data streams. "
                    f"Key differentiator: integrates {dir_kw[-1]} metrics for predictive optimization."
                )
            elif direction["name"] == "Innovation":
                title = f"{topic.title()} Intelligence Platform"
                desc = (
                    f"A novel platform that creates an entirely new category in {topic} "
                    f"by combining {dir_kw[0]} with {dir_kw[1] if len(dir_kw) > 1 else 'AI'}. "
                    f"Inspired by findings in {ref_paper}, this approach enables "
                    f"previously impossible insights through multi-dimensional analysis. "
                    f"Target market: organizations seeking {dir_kw[-1]}-driven decision support."
                )
            else:  # Adaptation
                title = f"{topic.title()} Cross-Domain Analyzer"
                desc = (
                    f"Applies proven {dir_kw[0]} methodologies from adjacent fields to {topic}. "
                    f"Referenced research ({ref_paper}) suggests significant untapped potential "
                    f"in applying {dir_kw[1] if len(dir_kw) > 1 else 'transfer learning'} techniques. "
                    f"Combines {dir_kw[-1]} frameworks with domain-specific data for "
                    f"actionable insights."
                )

            ideas.append({
                "title": title,
                "description": desc,
                "keywords": dir_kw,
                "direction": direction["name"],
            })

        # Add extra seeds if count > 3 by mixing directions
        while len(ideas) < count:
            idx = len(ideas) % len(DIRECTIONS)
            extra_kw = rng.sample(kw, min(3, len(kw)))
            ref = paper_refs[len(ideas) % len(paper_refs)] if paper_refs else "literature review"
            ideas.append({
                "title": f"{topic.title()} {extra_kw[0].title()} System",
                "description": (
                    f"Hybrid approach combining {extra_kw[0]} and {extra_kw[1] if len(extra_kw) > 1 else 'data'} "
                    f"for {topic}. Research basis: {ref}. "
                    f"Targets the gap between current {extra_kw[-1]} solutions and market needs."
                ),
                "keywords": extra_kw,
                "direction": DIRECTIONS[idx]["name"],
            })

        return ideas[:count]
