"use client";

import { useState, useEffect } from 'react';

// Premium Glass Card Component
export default function IdeaCard({ idea, onRefine, onEvaluate, onConvert, onUpdate, index }) {
    const [loading, setLoading] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [editTitle, setEditTitle] = useState(idea.title);
    const [editDesc, setEditDesc] = useState(idea.description);

    // Sync edit state when idea prop changes (e.g. after refine/evaluate)
    useEffect(() => {
        setEditTitle(idea.title);
        setEditDesc(idea.description);
    }, [idea.title, idea.description]);

    // Status Badge Colors
    const statusColor = {
        seed: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
        refined: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
        evaluated: 'bg-green-500/20 text-green-300 border-green-500/30',
        failed: 'bg-red-500/20 text-red-300 border-red-500/30',
    };

    const currentStatusStyle = statusColor[idea.status] || 'bg-gray-500/20 text-gray-300';

    const handleRefine = () => {
        setLoading(true);
        onRefine(idea.id).finally(() => setLoading(false));
    };

    const handleEvaluate = () => {
        setLoading(true);
        onEvaluate(idea.id).finally(() => setLoading(false));
    };

    const handleConvert = (type) => {
        setLoading(true);
        onConvert(idea.id, type).finally(() => setLoading(false));
    };

    const handleSave = async () => {
        setLoading(true);
        try {
            await onUpdate(idea.id, { title: editTitle, description: editDesc });
            setIsEditing(false);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass-card flex flex-col h-full relative overflow-hidden group">
            {/* Background Gradient Effect on Hover */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-secondary/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

            {/* Card Header */}
            <div className="flex justify-between items-start mb-4 relative z-10">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${currentStatusStyle}`}>
                    {idea.status.toUpperCase()}
                </span>
                <div className="flex gap-2">
                    {!isEditing && (
                        <button
                            onClick={() => {
                                setEditTitle(idea.title);
                                setEditDesc(idea.description);
                                setIsEditing(true);
                            }}
                            className="text-gray-400 hover:text-white text-xs underline"
                        >
                            Edit
                        </button>
                    )}
                    {idea.total_score > 0 && (
                        <div className="flex items-center gap-1 text-accent font-bold">
                            ★ {idea.total_score.toFixed(1)}
                        </div>
                    )}
                </div>
            </div>

            {/* Main Content */}
            {isEditing ? (
                <div className="mb-4 relative z-20">
                    <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        className="input-field mb-2 font-bold"
                        placeholder="Idea Title"
                    />
                    <textarea
                        value={editDesc}
                        onChange={(e) => setEditDesc(e.target.value)}
                        className="input-field min-h-[150px] font-mono text-sm"
                        placeholder="Description..."
                    />
                    <div className="flex gap-2 mt-2">
                        <button onClick={handleSave} disabled={loading} className="btn text-xs py-1 px-3">
                            {loading ? 'Saving...' : 'Save'}
                        </button>
                        <button onClick={() => setIsEditing(false)} disabled={loading} className="btn btn-secondary text-xs py-1 px-3">
                            Cancel
                        </button>
                    </div>
                </div>
            ) : (
                <>
                    <h3 className="text-xl font-bold mb-2 text-white group-hover:text-primary transition-colors">
                        {idea.title}
                    </h3>
                    <div className="text-gray-400 text-sm mb-4 flex-grow" style={{ whiteSpace: 'pre-line' }}>
                        {idea.status === 'seed'
                            ? idea.description.substring(0, 150) + '...'
                            : idea.description}
                    </div>
                </>
            )}

            {/* Origin Badge */}
            <div className="text-xs text-gray-500 mb-4 font-mono">
                ORIGIN: {idea.origin_trend}
            </div>

            {/* Scores Visualization */}
            {(idea.status === 'refined' || idea.status === 'evaluated') && (
                <div className="grid grid-cols-3 gap-2 mb-4 text-xs text-center border-t border-glass-border pt-4">
                    <div>
                        <div className="text-gray-500">Market</div>
                        <div className="font-bold text-white">{idea.market_score || '-'}</div>
                    </div>
                    <div>
                        <div className="text-gray-500">Tech</div>
                        <div className="font-bold text-white">{idea.tech_score || '-'}</div>
                    </div>
                    <div>
                        <div className="text-gray-500">Novelty</div>
                        <div className="font-bold text-white">{idea.novelty_score || '-'}</div>
                    </div>
                </div>
            )}

            {/* Artifact Links */}
            {idea.artifacts && Object.keys(idea.artifacts).length > 0 && (
                <div className="flex gap-2 mb-4">
                    {Object.entries(idea.artifacts).map(([type, url]) => (
                        <a key={type} href={url} target="_blank" rel="noreferrer" className="text-xs text-blue-400 hover:text-blue-300 underline uppercase">
                            View {type}
                        </a>
                    ))}
                </div>
            )}

            {/* Actions */}
            {!isEditing && (
                <div className="mt-auto flex gap-2 relative z-10">
                    {idea.status === 'seed' && (
                        <button
                            onClick={handleRefine}
                            disabled={loading}
                            className="w-full btn text-sm justify-center"
                        >
                            {loading ? 'Refining...' : 'Refine Idea ✨'}
                        </button>
                    )}

                    {idea.status === 'refined' && (
                        <button
                            onClick={handleEvaluate}
                            disabled={loading}
                            className="w-full btn btn-secondary text-sm justify-center border-primary text-primary hover:bg-primary hover:text-white"
                        >
                            {loading ? 'Reviewing...' : 'Evaluate ⚖️'}
                        </button>
                    )}

                    {idea.status === 'evaluated' && (
                        <div className="flex gap-2 w-full">
                            <button
                                onClick={() => handleConvert('pdf')}
                                disabled={loading}
                                className="flex-1 btn btn-secondary text-xs justify-center"
                            >
                                PDF 📄
                            </button>
                            <button
                                onClick={() => handleConvert('video')}
                                disabled={loading}
                                className="flex-1 btn btn-secondary text-xs justify-center"
                            >
                                Video 🎥
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
