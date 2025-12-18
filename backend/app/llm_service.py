"""
Ollama LLM Service for intelligent chatbot responses.
"""
import requests
from typing import Optional
import logging
import re
from app.config import settings

logger = logging.getLogger(__name__)


# Greeting and conversational patterns
GREETING_PATTERNS = [
    r'\b(bonjour|salut|hello|hey|bonsoir|coucou)\b',
    r'\b(qui es-tu|qui êtes-vous|c\'est quoi ton nom|quel est ton nom)\b',
    r'\b(comment (tu )?t\'appelles?|comment (vous )?vous appelez)\b',
]

CONVERSATIONAL_PATTERNS = [
    r'\b(comment (vas-tu|allez-vous|ça va|ca va))\b',
    r'\b(ça va|ca va)\??$',
    r'\b(tu vas bien|vous allez bien)\b',
]


def is_greeting(message: str) -> bool:
    """
    Check if the message is a greeting or self-introduction question.
    
    Args:
        message: User's message
        
    Returns:
        True if it's a greeting, False otherwise
    """
    message_lower = message.lower().strip()
    
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, message_lower):
            logger.info(f"Detected greeting: {message}")
            return True
    
    return False


def is_conversational(message: str) -> bool:
    """
    Check if the message is a conversational question (not HR-related).
    
    Args:
        message: User's message
        
    Returns:
        True if it's conversational, False otherwise
    """
    message_lower = message.lower().strip()
    
    for pattern in CONVERSATIONAL_PATTERNS:
        if re.search(pattern, message_lower):
            logger.info(f"Detected conversational question: {message}")
            return True
    
    return False


class OllamaService:
    """Service for interacting with Ollama LLM."""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        logger.info(f"Initializing Ollama service: {self.base_url} with model {self.model}")
    
    def generate_response(
        self,
        question: str,
        context: Optional[str] = None,
        profile: str = "Unknown"
    ) -> str:
        """
        Generate an intelligent response using Ollama LLM.
        
        Args:
            question: User's question
            context: RAG context if available (answer + domain from knowledge base)
            profile: User's profile (CDI, CDD, CADRE, etc.)
            
        Returns:
            Generated response from Ollama
        """
        # Build the prompt based on whether we have RAG context
        if context:
            prompt = self._build_prompt_with_context(question, context, profile)
        else:
            prompt = self._build_prompt_without_context(question, profile)
        
        # Call Ollama API
        try:
            logger.info(f"Calling Ollama for question: {question[:50]}...")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Very low for strict adherence to context
                        "top_p": 0.8,  # Reduced for more focused responses
                        "num_predict": 100  # Shorter responses to avoid elaboration
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                answer = response.json()["response"].strip()
                logger.info(f"Ollama response generated successfully")
                return answer
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return "Désolé, je rencontre un problème technique. Veuillez réessayer."
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timeout")
            return "Désolé, la réponse prend trop de temps. Veuillez réessayer."
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama service")
            return "Désolé, le service de chat est temporairement indisponible."
        except Exception as e:
            logger.error(f"Ollama exception: {str(e)}")
            return "Désolé, une erreur s'est produite. Veuillez réessayer."
    
    def _build_prompt_with_context(
        self,
        question: str,
        context: str,
        profile: str
    ) -> str:
        """Build prompt with RAG context - ultra-strict mode."""
        return f"""Tu es un assistant RH pour Serini.

Contexte : {context}
Question : {question}

RÈGLE : Réponds en UNE phrase courte en utilisant UNIQUEMENT les mots du contexte.
Tu peux ajouter "Pour" au début, mais N'AJOUTE RIEN D'AUTRE.

Exemple :
Contexte : "Via le manager et le portail RH"
Réponse : "Pour déclarer des heures supplémentaires, passez via le manager et le portail RH."

Réponds maintenant :"""
    
    def _build_prompt_without_context(self, question: str, profile: str) -> str:
        """Build prompt when no RAG context is available."""
        return f"""Tu es l'assistant RH virtuel de l'entreprise Serini. Tu n'as pas de nom personnel.

Profil de l'utilisateur: {profile}
Question de l'utilisateur: {question}

Instructions:
- Si c'est une salutation (bonjour, salut, etc.), réponds exactement: "Bonjour ! Je suis l'assistant RH virtuel de Serini. Comment puis-je vous aider ?"
- Ne te présente JAMAIS avec un nom ou un placeholder comme "[Votre nom]".
- Si c'est une question RH sans réponse dans la base, suggère de contacter le service RH.
- Si c'est hors sujet, rappelle que tu es un assistant RH.

Réponse:"""
    
    def check_health(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
