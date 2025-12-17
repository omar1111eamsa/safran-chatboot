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
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 200  # Limit response length
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
        """Build prompt with RAG context."""
        return f"""Tu es un assistant RH utile et précis pour l'entreprise Serini.
Ton rôle est de répondre aux questions des employés en te basant UNIQUEMENT sur les informations fournies dans le contexte.

Contexte (Information officielle RH) :
{context}

Question de l'employé ({profile}) :
{question}

Instructions :
1. Utilise l'information du contexte pour répondre.
2. Formule une phrase complète, naturelle et polie (ex: "Bonjour...", "Voici l'information...").
3. NE CHANGE PAS le sens de l'information officielle. Reste fidèle au contenu.
4. Si l'information n'est pas claire, dis-le.
"""
    
    def _build_prompt_without_context(self, question: str, profile: str) -> str:
        """Build prompt when no RAG context is available."""
        return f"""Tu es un assistant RH professionnel de l'entreprise Serini.

Profil de l'utilisateur: {profile}

Question de l'utilisateur: {question}

Instructions:
- Si c'est une salutation (bonjour, salut, etc.), réponds poliment et propose ton aide
- Si c'est une question RH à laquelle tu ne peux pas répondre sans information spécifique, suggère de contacter le service RH
- Si c'est une question hors-sujet (météo, sport, etc.), explique poliment que tu es un assistant RH
- Reste professionnel et concis
- Ne réponds que dans le cadre des ressources humaines

Réponse:"""
    
    def check_health(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
