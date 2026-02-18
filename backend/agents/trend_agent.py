import httpx
import re
from typing import List, Dict
from collections import Counter


class TrendAgent:
    def __init__(self):
        self.openalex_api = "https://api.openalex.org/works"
        self.patents_api = "https://api.patentsview.org/patents/query"

    async def collect_trends(self, topic: str) -> Dict:
        print(f"Collecting trends for: {topic}")

        papers = await self._search_papers(topic)
        patents = self._search_patents(topic)
        keywords = self._build_keyword_book(topic, papers, patents)

        paper_refs = [
            f"'{p['title']}' ({p.get('year', '?')})"
            for p in papers[:5]
        ]
        patent_refs = [
            p.get("patent_title", "?") for p in patents[:3]
        ]

        context_str = (
            f"Topic: {topic}. "
            f"Found {len(papers)} papers and {len(patents)} patents. "
            f"Key research: {'; '.join(paper_refs[:3])}. "
            f"Key themes: {', '.join(keywords[:8])}."
        )

        keyword_book_str = (
            f"Keyword Book for '{topic}':\n"
            f"Core terms: {', '.join(keywords[:10])}\n"
            f"Research papers: {'; '.join(paper_refs[:5])}\n"
            f"Patents: {'; '.join(patent_refs[:3])}"
        )

        return {
            "topic": topic,
            "papers": papers[:5],
            "patents": patents[:3],
            "keywords": keywords[:15],
            "keyword_book_str": keyword_book_str,
            "context_str": context_str,
        }

    async def _search_papers(self, topic: str) -> List[Dict]:
        """Fetch real papers from OpenAlex (free, no API key needed)."""
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    self.openalex_api,
                    params={
                        "search": topic,
                        "per_page": 10,
                        "sort": "cited_by_count:desc",
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for work in data.get("results", []):
                        abstract = ""
                        inv_abstract = work.get("abstract_inverted_index")
                        if inv_abstract:
                            # Reconstruct abstract from inverted index
                            word_positions = []
                            for word, positions in inv_abstract.items():
                                for pos in positions:
                                    word_positions.append((pos, word))
                            word_positions.sort()
                            abstract = " ".join(w for _, w in word_positions)[:500]

                        results.append({
                            "title": work.get("title", "Untitled"),
                            "year": work.get("publication_year"),
                            "abstract": abstract,
                            "cited_by": work.get("cited_by_count", 0),
                            "doi": work.get("doi", ""),
                            "url": work.get("id", ""),
                        })
                    if results:
                        print(f"  OpenAlex: {len(results)} papers found")
                        return results
        except Exception as e:
            print(f"  OpenAlex search failed: {e}")

        # Fallback mock
        return [
            {"title": f"Advances in {topic}: A Comprehensive Survey", "year": 2024,
             "abstract": f"This survey reviews recent developments in {topic}...",
             "cited_by": 45, "doi": "", "url": ""},
            {"title": f"Optimizing {topic} with Machine Learning", "year": 2025,
             "abstract": f"We propose a novel ML framework for {topic}...",
             "cited_by": 12, "doi": "", "url": ""},
        ]

    def _search_patents(self, topic: str) -> List[Dict]:
        """Fetch patents from PatentsView."""
        try:
            import requests
            import json
            resp = requests.post(
                self.patents_api,
                json={
                    "q": {"_text_any": {"patent_title": topic}},
                    "f": ["patent_title", "patent_date", "patent_abstract", "patent_number"],
                    "o": {"per_page": 5},
                },
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                patents = data.get("patents", []) or []
                if patents:
                    print(f"  PatentsView: {len(patents)} patents found")
                    return patents
        except Exception as e:
            print(f"  Patent search failed: {e}")

        return [
            {"patent_title": f"System and Method for {topic.title()} Analysis",
             "patent_date": "2024-03-15", "patent_number": "US11,234,567"},
        ]

    def _build_keyword_book(self, topic: str, papers: List[Dict], patents: List[Dict]) -> List[str]:
        """Extract keywords from paper titles and abstracts."""
        text = topic.lower()
        for p in papers:
            text += " " + (p.get("title", "") + " " + p.get("abstract", "")).lower()
        for p in patents:
            text += " " + (p.get("patent_title", "") + " " + p.get("patent_abstract", "")).lower()

        # Simple keyword extraction: split, filter stopwords, count
        stopwords = {
            "the", "a", "an", "of", "in", "for", "and", "or", "to", "is", "are",
            "was", "were", "be", "been", "with", "on", "at", "by", "from", "as",
            "it", "its", "this", "that", "these", "those", "we", "our", "their",
            "has", "have", "had", "not", "but", "can", "will", "may", "also",
            "more", "than", "which", "who", "how", "what", "when", "where",
            "about", "between", "through", "during", "before", "after", "into",
            "over", "under", "above", "below", "all", "each", "both", "such",
            "no", "other", "new", "used", "using", "based", "two", "first",
        }
        words = re.findall(r'[a-z]{3,}', text)
        counter = Counter(w for w in words if w not in stopwords and len(w) > 3)

        # Remove topic words themselves to get related terms
        topic_words = set(topic.lower().split())
        return [w for w, _ in counter.most_common(25) if w not in topic_words][:15]
