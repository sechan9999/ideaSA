import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import os

try:
    from sentence_transformers import SentenceTransformer
    MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    print("SentenceTransformers not installed. Running in mock mode.")
    MODEL = None

class EmbeddingService:
    def __init__(self):
        self.model = MODEL

    def get_embedding(self, text: str) -> np.ndarray:
        if self.model:
            return self.model.encode(text)
        else:
            # Mock embedding (random vector of size 384)
            return np.random.rand(384)

    def deduplicate(self, ideas: List) -> List:
        """
        Clusters ideas based on cosine similarity and returns unique ones (one per cluster).
        """
        if not ideas:
            return []
            
        embeddings = [self.get_embedding(idea.description) for idea in ideas]
        similarity_matrix = cosine_similarity(embeddings)
        
        # Simple greedy clustering
        # Mark ideas as 'duplicate' if similarity > threshold (e.g. 0.85)
        threshold = 0.85
        unique_ideas = []
        seen_indices = set()
        
        for i in range(len(ideas)):
            if i in seen_indices:
                continue
            
            unique_ideas.append(ideas[i])
            seen_indices.add(i)
            
            for j in range(i + 1, len(ideas)):
                if j in seen_indices:
                    continue
                
                if similarity_matrix[i][j] > threshold:
                    seen_indices.add(j)
                    # Optionally merge ideas or add references
                    
        return unique_ideas
