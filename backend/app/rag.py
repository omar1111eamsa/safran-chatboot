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
        threshold: float = 0.75
    ) -> Tuple[Optional[str], Optional[str], float, bool]:
        """
        Search knowledge base for relevant answer.
        
        Args:
            question: User's question
            employee_type: User's profile (CDI, CDD, CADRE, etc.)
            threshold: Minimum similarity score to consider answer relevant
            
        Returns:
            Tuple of (answer, domain, similarity_score, profile_allowed)
            - profile_allowed is True if the answer matches the user's profile
            - If profile mismatch, returns (None, None, score, False)
        """
        if self.df is None or self.model is None or self.embeddings is None:
            logger.error("RAG engine not initialized")
            return None, None, 0.0, True

        try:
            # Encode user question
            question_embedding = self.model.encode(question, convert_to_tensor=True)
            
            # Compute cosine similarities with ALL entries (global search)
            similarities = util.cos_sim(question_embedding, self.embeddings)[0]
            
            # Get best match
            best_match_idx = similarities.argmax().item()
            best_similarity = similarities[best_match_idx].item()
            
            logger.info(f"Best global match similarity: {best_similarity:.3f}")
            
            # Check if similarity meets threshold
            if best_similarity < threshold:
                logger.info(f"Similarity {best_similarity:.3f} below threshold {threshold}")
                return None, None, best_similarity, True
            
            # Get the best match entry
            best_match = self.df.iloc[best_match_idx]
            match_profile = str(best_match['profil'])
            
            # Check profile authorization
            # Compare normalized profiles (case insensitive)
            if match_profile.strip().lower() != employee_type.strip().lower():
                logger.warning(
                    f"Profile mismatch! Question is for '{match_profile}', "
                    f"user is '{employee_type}'"
                )
                return None, None, best_similarity, False
            
            # Profile matches, return answer
            answer = str(best_match['reponse'])
            domain = str(best_match['domaine'])
            
            logger.info(f"Found authorized answer in domain '{domain}' for profile '{match_profile}'")
            
            return answer, domain, best_similarity, True
            
        except Exception as e:
            logger.error(f"Error in RAG search: {str(e)}")
            return None, None, 0.0, True


# Global RAG engine instance
rag_engine = RAGEngine()
