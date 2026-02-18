from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models.idea import Idea, IdeaCreate, TrendContext
from agents.trend_agent import TrendAgent
from agents.seed_agent import SeedAgent
from agents.refine_agent import RefineAgent
from agents.eval_agent import EvalAgent
from agents.artifact_agent import ArtifactAgent
from services.embedding_service import EmbeddingService
import asyncio

app = FastAPI(title="IdeaSA Backend", description="Agentic Idea Generation & Verification System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for MVP simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for MVP. In production, use DB.
IDEAS_DB = {}
TRENDS_DB = []

# Services & Agents (Initialized lazily or on startup)
embedding_service = EmbeddingService()
trend_agent = TrendAgent()
seed_agent = SeedAgent()
refine_agent = RefineAgent()
eval_agent = EvalAgent() 
artifact_agent = ArtifactAgent()

@app.get("/")
async def root():
    return {"message": "IdeaSA API is running"}

@app.get("/ideas", response_model=List[Idea])
async def get_all_ideas():
    return list(IDEAS_DB.values())

@app.post("/workflow/start", response_model=List[Idea])
async def start_workflow(topic: str):
    """
    Step 1: Trend Collection -> Step 2: Seed Generation (Batch)
    """
    # 1. Trend Collection
    context = await trend_agent.collect_trends(topic)
    
    # 2. Seed Generation (Batch + Verbalized Sampling)
    seeds = await seed_agent.generate_seeds(context, count=5)
    
    # Check for duplicates immediately? Or later?
    # Let's clean and store them.
    for seed in seeds:
        IDEAS_DB[seed.id] = seed
        
    return seeds

@app.post("/workflow/refine/{idea_id}", response_model=Idea)
async def refine_idea(idea_id: str):
    """
    Step 3: Refinement (Multilingual Prompting + Multi-perspective)
    """
    if idea_id not in IDEAS_DB:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    idea = IDEAS_DB[idea_id]
    refined_idea = await refine_agent.refine(idea)
    
    # Update DB
    IDEAS_DB[idea_id] = refined_idea
    return refined_idea

@app.post("/workflow/evaluate/{idea_id}", response_model=Idea)
async def evaluate_idea(idea_id: str):
    """
    Step 4: Evaluation (Reviewer Agents) & Leaderboard Scoring
    """
    if idea_id not in IDEAS_DB:
        raise HTTPException(status_code=404, detail="Idea not found")
        
    idea = IDEAS_DB[idea_id]
    evaluated_idea = await eval_agent.evaluate(idea)
    
    IDEAS_DB[idea_id] = evaluated_idea
    return evaluated_idea

@app.post("/workflow/artifact/{idea_id}")
async def generate_artifact(idea_id: str, artifact_type: str = "pdf"):
    """
    Step 5: Generate PDF/Video
    """
    if idea_id not in IDEAS_DB:
        raise HTTPException(status_code=404, detail="Idea not found")
        
    idea = IDEAS_DB[idea_id]
    url = await artifact_agent.generate(idea, artifact_type)
    
    if artifact_type == "pdf":
        idea.artifacts["pdf"] = url
    elif artifact_type == "video":
        idea.artifacts["video"] = url
        
    IDEAS_DB[idea_id] = idea
    return {"url": url}

@app.get("/leaderboard", response_model=List[Idea])
async def get_leaderboard():
    """
    Returns ideas sorted by total_score.
    """
    all_ideas = list(IDEAS_DB.values())
    # Sort by total_score descending
    sorted_ideas = sorted(all_ideas, key=lambda x: x.total_score, reverse=True)
    return sorted_ideas

@app.post("/deduplicate")
async def deduplicate_ideas():
    """
    Step 4b: Embedding-based deduplication
    """
    all_ideas = list(IDEAS_DB.values())
    unique_ideas = embedding_service.deduplicate(all_ideas)
    
    # In a real app, strict dedup logic would archive duplicates
    # For now, return unique
    return unique_ideas
