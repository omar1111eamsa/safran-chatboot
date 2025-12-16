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
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Model loaded successfully")
            
            # Pre-compute embeddings for all questions
            logger.info("Computing embeddings for knowledge base...")
            questions = self.df['question'].tolist()
            self.embeddings = self.model.encode(questions, convert_to_tensor=True)
            logger.info("Embeddings computed successfully")
            
        except Exception as e:
            logger.error(f"Error loading RAG engine: {str(e)}")
            raise
    
    def get_answer(
        self,
        question: str,
        employee_type: str,
        title: str
    ) -> Tuple[str, Optional[str]]:
        """
        Get answer for user question based on their profile.
        
        Args:
            question: User's question
            employee_type: User's employment type (CDI, CDD, Intérim, Stagiaire)
            title: User's title (Cadre, Non-Cadre)
            
        Returns:
            Tuple of (answer, domain) or error message if not found
        """
        if self.df is None or self.model is None or self.embeddings is None:
            return "Le système n'est pas encore initialisé. Veuillez réessayer.", None
        
        try:
            # Filter by profile (employeeType OR title)
            # This allows matching on either employee type or title
            filtered_df = self.df[
                (self.df['profil'] == employee_type) | 
                (self.df['profil'] == title)
            ]
            
            if filtered_df.empty:
                logger.warning(f"No entries found for profile: {employee_type}/{title}")
                return (
                    f"Désolé, je n'ai pas d'information spécifique pour votre profil ({employee_type}/{title}). "
                    "Veuillez contacter le service RH.",
                    None
                )
            
            # Get indices of filtered questions
            filtered_indices = filtered_df.index.tolist()
            filtered_embeddings = self.embeddings[filtered_indices]
            
            # Encode user question
            question_embedding = self.model.encode(question, convert_to_tensor=True)
            
            # Compute cosine similarities
            similarities = util.cos_sim(question_embedding, filtered_embeddings)[0]
            
            # Get best match
            best_match_idx = similarities.argmax().item()
            best_similarity = similarities[best_match_idx].item()
            
            # Get the actual dataframe index
            actual_idx = filtered_indices[best_match_idx]
            
            # Log similarity score
            logger.info(f"Best match similarity: {best_similarity:.4f}")
            
            # Return answer and domain
            answer = self.df.loc[actual_idx, 'reponse']
            domain = self.df.loc[actual_idx, 'domaine']
            
            # Add confidence indicator if similarity is low
            if best_similarity < 0.5:
                answer = f"{answer}\n\n(Note: Cette réponse peut ne pas correspondre exactement à votre question. Contactez le service RH pour plus de précisions.)"
            
            return str(answer), str(domain)
            
        except Exception as e:
            logger.error(f"Error in RAG search: {str(e)}")
            return "Une erreur s'est produite lors de la recherche. Veuillez réessayer.", None


# Global RAG engine instance
rag_engine = RAGEngine()
