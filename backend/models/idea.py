from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

class Evaluation(BaseModel):
    reviewer_role: str  # "Market", "Tech", "Novelty"
    score: float
    feedback: str
    timestamp: datetime = Field(default_factory=datetime.now)

class Idea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    status: str = "seed"  # seed, refined, evaluated, archived
    origin_trend: Optional[str] = None
    keywords: List[str] = []
    
    # Validation Scores
    market_score: float = 0.0
    tech_score: float = 0.0
    novelty_score: float = 0.0
    total_score: float = 0.0
    
    evaluations: List[Evaluation] = []
    
    # Artifacts and Evidence
    evidence_urls: List[str] = []  # Links to papers, patents
    artifacts: Dict[str, str] = {}  # "pdf": "url", "video": "url"
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class IdeaCreate(BaseModel):
    title: str
    description: str
    keywords: List[str] = []

class TrendContext(BaseModel):
    topic: str
    related_keywords: List[str]
    recent_papers: List[Dict[str, str]]
    news_titles: List[str]
