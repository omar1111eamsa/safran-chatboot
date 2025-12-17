"""
RAG (Retrieval Augmented Generation) engine for HR knowledge base.
Uses sentence-transformers for semantic search.
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine for semantic search in HR knowledge base."""
    
    def __init__(self, csv_path: str = "data/knowledge_base.csv"):
        """
        Initialize RAG engine.
        
        Args:
            csv_path: Path to knowledge base CSV file
        """
        self.csv_path = Path(csv_path)
        self.df: Optional[pd.DataFrame] = None
        self.model: Optional[SentenceTransformer] = None
        self.embeddings: Optional[np.ndarray] = None
        
    def load(self):
        """Load knowledge base and initialize model."""
        try:
            # Load CSV
            logger.info(f"Loading knowledge base from {self.csv_path}")
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} entries from knowledge base")
            
            # Load sentence transformer model
            logger.info("Loading sentence-transformer model...")
            self.model = SentenceTransformer('all-mpnet-base-v2')
            logger.info("Model loaded successfully")
            
            # Pre-compute embeddings for all questions
            logger.info("Computing embeddings for knowledge base...")
            questions = self.df['question'].tolist()
            self.embeddings = self.model.encode(questions, convert_to_tensor=True)
            logger.info("Embeddings computed successfully")
            
        except Exception as e:
            logger.error(f"Error loading RAG engine: {str(e)}")
            raise
    
    def search_knowledge(
        self,
        question: str,
        employee_type: str,
        threshold: float = 0.6
    ) -> Tuple[Optional[str], Optional[str], float]:
        """
        Search knowledge base for relevant answer.
        
        Args:
            question: User's question
            employee_type: User's profile (CDI, CDD, CADRE, NON-CADRE, INTÉRIMAIRE, STAGIAIRE)
            threshold: Minimum similarity score to consider answer relevant (0.0 to 1.0)
            
        Returns:
            Tuple of (answer, domain, similarity_score)
            If similarity < threshold, returns (None, None, score)
        """
        if self.df is None or self.model is None or self.embeddings is None:
            return None, None, 0.0
        
        try:
            # Filter by profile - single attribute now
            # Supports 6 profiles: CDI, CDD, CADRE, NON-CADRE, INTÉRIMAIRE, STAGIAIRE
            filtered_df = self.df[self.df['profil'] == employee_type]
            
            if filtered_df.empty:
                logger.warning(f"No entries found for profile: {employee_type}")
                return None, None, 0.0
            
            # Get indices of filtered entries
            filtered_indices = filtered_df.index.tolist()
            filtered_embeddings = self.embeddings[filtered_indices]
            
            # Encode user question
            question_embedding = self.model.encode(question, convert_to_tensor=True)
            
            # Compute cosine similarities
            similarities = util.cos_sim(question_embedding, filtered_embeddings)[0]
            
            # Get best match
            best_match_idx = similarities.argmax().item()
            best_similarity = similarities[best_match_idx].item()
            
            logger.info(f"Best match similarity: {best_similarity:.3f} (threshold: {threshold})")
            
            # Check if similarity meets threshold
            if best_similarity < threshold:
                logger.info(f"Similarity {best_similarity:.3f} below threshold {threshold}")
                return None, None, best_similarity
            
            # Get the actual index in the original dataframe
            actual_idx = filtered_indices[best_match_idx]
            
            # Extract answer and domain
            answer = str(self.df.loc[actual_idx, 'reponse'])
            domain = str(self.df.loc[actual_idx, 'domaine'])
            
            logger.info(f"Found answer in domain '{domain}' with similarity {best_similarity:.3f}")
            
            return answer, domain, best_similarity
            
        except Exception as e:
            logger.error(f"Error in RAG search: {str(e)}")
            return None, None, 0.0


# Global RAG engine instance
rag_engine = RAGEngine()
