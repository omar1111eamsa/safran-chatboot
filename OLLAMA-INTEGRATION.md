# Intégration Ollama LLM - Guide Complet

## Modifications Effectuées

### 1. Infrastructure (docker-compose.yml)
- [x] Ajout du service `ollama` avec image officielle
- [x] Volume `ollama-data` pour persistance du modèle
- [x] Port 11434 exposé
- [x] Backend dépend maintenant d'Ollama

### 2. Backend - Nouveau Service LLM
- [x] Créé `backend/app/llm_service.py`
- [x] Classe `OllamaService` pour générer des réponses intelligentes
- [x] Prompts contextuels (avec/sans RAG)

### 3. Backend - RAG Amélioré
- [x] Méthode `search_knowledge()` avec seuil de similarité
- [x] Retourne score de similarité (0.0 à 1.0)
- [x] Seuil par défaut: 0.6

### 4. Backend - Endpoint Chat Hybride
- [x] Recherche RAG d'abord
- [x] Si pertinent (>0.6): Ollama + contexte RAG
- [x] Si non pertinent: Ollama seul

### 5. Configuration
- [x] Variables d'environnement Ollama ajoutées
- [x] `OLLAMA_BASE_URL=http://ollama:11434`
- [x] `OLLAMA_MODEL=llama3.2:3b`

### 6. Scripts
- [x] `setup-ollama.sh` pour télécharger le modèle

---

## Déploiement

### Étape 1: Arrêter les Services Actuels
```bash
cd /home/omar/myWork/safran
docker compose down
```

### Étape 2: Démarrer avec Ollama
```bash
# Démarrer tous les services (y compris Ollama)
docker compose up -d

# Attendre que tous les services soient prêts
docker compose ps
```

### Étape 3: Initialiser Ollama
```bash
# Télécharger le modèle llama3.2:3b (~2 GB)
./setup-ollama.sh
```

**Temps estimé**: ~5-10 minutes (selon votre connexion internet)

### Étape 4: Configurer LDAP
```bash
# Créer les utilisateurs LDAP
./setup-ldap.sh
```

### Étape 5: Tester
```bash
# Vérifier que tout fonctionne
curl http://localhost:8000/health

# Tester Ollama directement
docker exec -it hr-ollama ollama run llama3.2:3b "Bonjour"
```

---

## Exemples de Comportement

### Exemple 1: Salutation
**Utilisateur**: "Bonjour"

**Processus**:
1. RAG: Aucune correspondance (similarity < 0.6)
2. Ollama génère réponse seul

**Réponse**: 
> "Bonjour ! Je suis l'assistant RH de Safran. Comment puis-je vous aider aujourd'hui ? Je peux répondre à vos questions sur les congés, la paie, les avantages sociaux et bien plus encore."

**Domaine**: None

---

### Exemple 2: Question RH Pertinente
**Utilisateur** (CADRE): "Comment poser un congé annuel ?"

**Processus**:
1. RAG: Trouve réponse (similarity = 0.85)
2. Ollama utilise le contexte RAG

**Réponse**:
> "Pour poser un congé annuel, vous devez faire votre demande via le portail RH au moins 7 jours à l'avance. Connectez-vous au portail avec vos identifiants, accédez à la section 'Congés' et remplissez le formulaire de demande en indiquant les dates souhaitées. Votre manager recevra une notification pour validation."

**Domaine**: "congés"

---

### Exemple 3: Question Hors Profil
**Utilisateur** (STAGIAIRE): "Comment déclarer des heures supplémentaires ?"

**Processus**:
1. RAG: Aucune réponse pour STAGIAIRE (similarity = 0.3)
2. Ollama génère réponse seul

**Réponse**:
> "En tant que stagiaire, les heures supplémentaires ne s'appliquent généralement pas à votre type de contrat. Cependant, si vous avez des questions spécifiques sur vos horaires ou votre temps de travail, je vous recommande de contacter directement le service RH ou votre tuteur de stage."

**Domaine**: None

---

### Exemple 4: Question Non-RH
**Utilisateur**: "Quel temps fait-il aujourd'hui ?"

**Processus**:
1. RAG: Aucune correspondance
2. Ollama génère réponse seul

**Réponse**:
> "Je suis désolé, mais je suis un assistant RH et je ne peux répondre qu'aux questions liées aux ressources humaines de l'entreprise Safran. Puis-je vous aider avec une question concernant les congés, la paie, les avantages sociaux ou tout autre sujet RH ?"

**Domaine**: None

---

### Exemple 5: Conversation Naturelle
**Utilisateur**: "Merci beaucoup !"

**Réponse**:
> "Je vous en prie ! N'hésitez pas si vous avez d'autres questions RH. Bonne journée !"

---

## Configuration Avancée

### Changer de Modèle

Pour utiliser un modèle différent, modifiez `.env`:

```env
# Modèle plus petit et rapide (1.5 GB)
OLLAMA_MODEL=llama3.2:1b

# Modèle plus performant (4 GB)
OLLAMA_MODEL=mistral:7b

# Modèle très performant (4.7 GB)
OLLAMA_MODEL=llama3.1:8b
```

Puis téléchargez le nouveau modèle:
```bash
docker exec hr-ollama ollama pull mistral:7b
docker compose restart backend-api
```

### Ajuster le Seuil de Similarité

Dans `backend/app/main.py`, ligne ~220:

```python
rag_answer, domain, similarity = rag_engine.search_knowledge(
    question=request.message,
    employee_type=current_user.employee_type,
    threshold=0.6  # Modifier ici (0.0 à 1.0)
)
```

- **0.4-0.5**: Plus permissif (plus de réponses RAG)
- **0.6-0.7**: Équilibré (recommandé)
- **0.8-0.9**: Strict (seulement réponses très pertinentes)

---

## Ressources Système

### Avant (Sans Ollama)
- RAM: ~2 GB
- Disque: ~3 GB

### Après (Avec Ollama + llama3.2:3b)
- RAM: ~6 GB (+4 GB)
- Disque: ~5 GB (+2 GB)

### Modèles Alternatifs

| Modèle | Taille | RAM | Qualité | Vitesse |
|--------|--------|-----|---------|---------|
| llama3.2:1b | 1 GB | 2 GB | 3/5 | 5/5 |
| **llama3.2:3b** | 2 GB | 4 GB | 4/5 | 4/5 |
| mistral:7b | 4 GB | 8 GB | 5/5 | 3/5 |
| llama3.1:8b | 4.7 GB | 8 GB | 5/5 | 2/5 |

---

## Dépannage

### Ollama ne démarre pas
```bash
# Vérifier les logs
docker compose logs ollama

# Redémarrer Ollama
docker compose restart ollama
```

### Modèle non téléchargé
```bash
# Vérifier les modèles installés
docker exec hr-ollama ollama list

# Télécharger manuellement
docker exec hr-ollama ollama pull llama3.2:3b
```

### Réponses lentes
```bash
# Utiliser un modèle plus petit
docker exec hr-ollama ollama pull llama3.2:1b

# Modifier .env
OLLAMA_MODEL=llama3.2:1b

# Redémarrer backend
docker compose restart backend-api
```

### Backend ne peut pas se connecter à Ollama
```bash
# Vérifier le réseau
docker network inspect hr-chatbot-network

# Vérifier qu'Ollama est accessible
docker exec hr-backend curl http://ollama:11434/api/tags
```

---

## Avantages de Cette Approche

### 1. Intelligence Contextuelle
- [x] Comprend les salutations
- [x] Peut refuser poliment les questions hors-sujet
- [x] Conversations naturelles

### 2. Précision RH
- [x] Utilise la base de connaissances quand pertinent
- [x] Cite les domaines (congés, paie, etc.)
- [x] Filtre par profil utilisateur

### 3. Flexibilité
- [x] Peut gérer plusieurs tours de conversation
- [x] S'adapte au contexte
- [x] Reformule les réponses de façon naturelle

### 4. Local et Sécurisé
- [x] Pas d'API externe
- [x] Données privées (RGPD)
- [x] Gratuit (pas de coût API)

---

## Commandes Utiles

```bash
# Tester Ollama en interactif
docker exec -it hr-ollama ollama run llama3.2:3b

# Voir les modèles installés
docker exec hr-ollama ollama list

# Supprimer un modèle
docker exec hr-ollama ollama rm llama3.2:3b

# Logs Ollama
docker compose logs -f ollama

# Logs Backend
docker compose logs -f backend-api

# Redémarrer tout
docker compose restart
```

---

## Résultat Final

Votre chatbot RH est maintenant **intelligent** et peut:
- [x] Saluer les utilisateurs
- [x] Répondre aux questions RH avec précision
- [x] Refuser poliment les questions hors-sujet
- [x] Avoir des conversations naturelles
- [x] Utiliser la base de connaissances quand pertinent

**Fini les réponses aléatoires pour "bonjour" !**
