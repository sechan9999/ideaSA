# IdeaSA: Research-Based Agentic Workflow App

IdeaSA transforms raw trend topics into verified, actionable project proposals through a rigorous agentic pipeline.

## Features
- **Trend Collection**: Aggregates data from patents and research papers.
- **Seed Generation**: Uses Verbalized Sampling to generate diverse initial ideas.
- **Refinement**: Expands ideas with multilingual prompting and multi-perspective reflection.
- **Evaluation**: Scores ideas using Market, Tech, and Novelty reviewer personas.
- **Artifacts**: Generates PDF proposals and concept images.
- **Deduplication**: Filters redundant ideas using embedding similarity.

## Tech Stack
- **Frontend**: Next.js 14 (App Router), React, Premium Glassmorphism UI.
- **Backend**: FastAPI, Python, Agents (LangChain/Custom), SQLite/In-Memory DB.
- **AI**: Integrates with LLMs (OpenAI/Anthropic) and Pollinations.ai for images.

## Setup & Run

### Prerequisites
- Node.js & npm
- Python 3.10+
- OpenAI/Anthropic API Key (optional, defaults to mock mode)

### Quick Start
1. **Run the all-in-one launcher:**
   Double-click `start_app_full.bat` (Windows)
   
   *OR manually:*
   
2. **Backend:**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

3. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the App:**
   Open [http://localhost:3000](http://localhost:3000)

## API Documentation
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
