"use client";

import { useState } from 'react';
import IdeaCard from '../components/IdeaCard';

export default function Home() {
  interface Idea {
    id: string;
    title: string;
    description: string;
    status: string;
    origin_trend: string;
    market_score?: number;
    tech_score?: number;
    novelty_score?: number;
    total_score?: number;
    artifacts?: { [key: string]: string };
    [key: string]: any;
  }

  const [topic, setTopic] = useState('');
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState('input'); // input, seeds, refining, evaluating

  // API Client (Simple)
  const API_BASE = 'http://localhost:8000';

  const startWorkflow = async () => {
    if (!topic) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/workflow/start?topic=${topic}`, { method: 'POST' });
      const data = await res.json();
      setIdeas(data);
      setStage('seeds');
    } catch (e) {
      console.error(e);
      alert("Error starting workflow. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const refineIdea = async (ideaId: string) => {
    try {
      const res = await fetch(`${API_BASE}/workflow/refine/${ideaId}`, { method: 'POST' });
      const refined = await res.json();
      // Update local state
      setIdeas(prev => prev.map(i => i.id === ideaId ? refined : i));
    } catch (e) {
      console.error(e);
    }
  };

  const evaluateIdea = async (ideaId: string) => {
    try {
      const res = await fetch(`${API_BASE}/workflow/evaluate/${ideaId}`, { method: 'POST' });
      const evaluated = await res.json();
      setIdeas(prev => prev.map(i => i.id === ideaId ? evaluated : i));
    } catch (e) {
      console.error(e);
    }
  };

  const updateIdea = async (ideaId: string, updates: Partial<Idea>) => {
    // Save original for rollback
    const originalIdea = ideas.find(i => i.id === ideaId);

    // Optimistic update
    setIdeas(prev => prev.map(i => i.id === ideaId ? { ...i, ...updates } : i));

    try {
      const res = await fetch(`${API_BASE}/ideas/${ideaId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (!res.ok) {
        let errorMsg = `Failed to update: ${res.statusText}`;
        try {
          const errData = await res.json();
          errorMsg = errData.detail || errorMsg;
        } catch {
          // ignore JSON parse failure
        }
        throw new Error(errorMsg);
      }

      const updated = await res.json();
      setIdeas(prev => prev.map(i => i.id === ideaId ? { ...i, ...updated } : i));
    } catch (e: any) {
      console.error(e);
      // Revert to original on failure
      if (originalIdea) {
        setIdeas(prev => prev.map(i => i.id === ideaId ? originalIdea : i));
      }
      alert(e.message || "Failed to save changes. Please try again.");
    }
  };

  const convertIdea = async (ideaId: string) => {
    try {
      const res = await fetch(`${API_BASE}/workflow/artifact/${ideaId}`, { method: 'POST' });
      const data = await res.json();
      const url = data.url;

      setIdeas(prev => prev.map(i => {
        if (i.id === ideaId) {
          return { ...i, artifacts: { ...i.artifacts, pdf: url } };
        }
        return i;
      }));
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 text-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-radial from-blue-900/20 to-transparent z-0 pointer-events-none" />
        <div className="container relative z-10">
          <h1 className="text-6xl font-bold mb-4 tracking-tight">
            <span className="gradient-text">Idea</span>SA
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-12">
            The Agentic Workflow for Research-Based Idea Discovery.
            <br />
            <span className="text-sm text-gray-500">From Trend to Proposal in Minutes.</span>
          </p>

          {/* Input Area */}
          <div className="max-w-xl mx-auto glass-card flex gap-4 p-2 items-center">
            <input
              type="text"
              placeholder="Enter a trend topic (e.g. 'Sustainable Packaging', 'AI in Education')"
              className="bg-transparent border-none text-white w-full px-4 outline-none text-lg"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && startWorkflow()}
            />
            <button
              onClick={startWorkflow}
              disabled={loading}
              className="bg-primary hover:bg-secondary text-white px-6 py-3 rounded-lg font-bold transition-all shadow-lg shadow-primary/20"
            >
              {loading ? 'Analyzing...' : 'Start 🚀'}
            </button>
          </div>
        </div>
      </section>

      {/* Results Section */}
      {ideas.length > 0 && (
        <section className="container pb-20">
          <div className="step-indicator mb-12">
            <div className={`step ${stage === 'seeds' ? 'active' : ''}`}>1. Seed Generation</div>
            <div className={`step ${ideas.some(i => i.status === 'refined') ? 'active' : ''}`}>2. Refinement</div>
            <div className={`step ${ideas.some(i => i.status === 'evaluated') ? 'active' : ''}`}>3. Evaluation</div>
            <div className={`step ${ideas.some(i => i.artifacts && Object.keys(i.artifacts).length > 0) ? 'active' : ''}`}>4. PDF Export</div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {ideas.map((idea, idx) => (
              <div key={idea.id} className="h-full">
                <IdeaCard
                  idea={idea}
                  onRefine={refineIdea}
                  onEvaluate={evaluateIdea}
                  onConvert={convertIdea}
                  onUpdate={updateIdea}
                  index={idx}
                />
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="text-center py-8 text-gray-600 text-sm border-t border-glass-border mt-auto">
        Built with Agentic AI • Using Patent/Paper Data Sources • Powered by Pollinations & LLMs
      </footer>
    </main>
  );
}
