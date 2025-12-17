# HR Chatbot Intelligent (RAG + Ollama LLM)

Application de chatbot RH d'entreprise intégrant un système hybride combinant l'intelligence artificielle générative (Ollama) et la recherche documentaire (RAG - Retrieval Augmented Generation) pour fournir des réponses contextuelles et précises aux employés.

![Status](https://img.shields.io/badge/Status-Active-success)
![Docker](https://img.shields.io/badge/Docker-v24.0+-blue)
![Python](https://img.shields.io/badge/Python-3.11-yellow)
![Node](https://img.shields.io/badge/Node-20-green)
![React](https://img.shields.io/badge/React-19-blue)

---

## Sommaire

1. [Aperçu Technique](#aperçu-technique)
2. [Stack Technologique et Versions](#stack-technologique-et-versions)
3. [Fonctionnalités Principales](#fonctionnalités-principales)
4. [Installation via Docker Hub (Production/Test)](#installation-via-docker-hub-productiontest)
5. [Installation via GitHub (Développement)](#installation-via-github-développement)
6. [Installation Manuelle (Code Source)](#installation-manuelle-code-source)
7. [Configuration et Initialisation](#configuration-et-initialisation)
8. [Utilisation et Scénarios de Test](#utilisation-et-scénarios-de-test)

---

## Aperçu Technique

Ce projet implémente une architecture micro-services pour servir un chatbot intelligent capable de distinguer les questions nécessitant des connaissances spécifiques à l'entreprise (traitées par RAG) des interactions conversationnelles générales (traitées par LLM).

L'architecture repose sur :
- **Frontend** : Interface utilisateur React moderne.
- **Backend** : API FastAPI gérant l'orchestration entre le moteur RAG et le service LLM.
- **Services de Données** :
  - **OpenLDAP** : Gestion des identités et des profils utilisateurs.
  - **Ollama** : Exécution locale du modèle de langage (Llama 3.2).
  - **Base Vectorielle** : Moteur RAG interne (basé sur FAISS/Pandas et Sentence Transformers).

---

## Stack Technologique et Versions

### Backend (Python/FastAPI)
- **Langage** : Python 3.11
- **Framework Web** : `fastapi==0.109.0`
- **Serveur d'Application** : `uvicorn[standard]==0.27.0`
- **Sécurité & Auth** :
  - `python-jose==3.3.0` (Gestion JWT)
  - `passlib==1.7.4` (Hachage)
  - `ldap3==2.9.1` (Connecteur LDAP)
- **IA & RAG** :
  - `sentence-transformers==2.3.1` (Modèle d'embedding : `all-mpnet-base-v2`)
  - `pandas==2.1.4` (Manipulation de données)
  - `numpy==1.26.3` (Calcul scientifique)
  - `scikit-learn==1.4.0` (Similarité cosinus)
- **Client LLM** : `requests==2.31.0`
- **Validation de Données** : `pydantic==2.5.3`

### Frontend (React/Vite)
- **Runtime** : Node.js 20 (Base Alpine Linux)
- **Bibliothèque UI** : React 19.2.0 (`react`, `react-dom`)
- **Build System** : Vite 7.2.4
- **Routage** : React Router 7.10.1 (`react-router-dom`)
- **Client HTTP** : Axios 1.13.2
- **Styling** : TailwindCSS 3.4.19 (`postcss`, `autoprefixer`)

### Infrastructure
- **LLM** : Ollama (Image Docker : `ollama/ollama:latest`)
  - Modèle : `llama3.2:3b`
- **Annuaire** : OpenLDAP (Image Docker : `osixia/openldap:1.5.0`)
- **Orchestration** : Docker Compose v2.20+
- **Serveur Web Frontend** : Nginx (Alpine)

---

## Fonctionnalités Principales

1.  **Orchestration Hybride (RAG + LLM)** : Le système évalue la pertinence de la question par rapport à la base de connaissances interne. Si le score de similarité dépasse le seuil (0.6), le contexte est injecté dans le prompt du LLM. Sinon, le LLM répond en mode conversationnel standard.
2.  **Gestion Granulaire des Profils** : Prise en charge de 6 statuts employés distincts (CDI, CDD, Cadre, Non-Cadre, Intérimaire, Stagiaire) influençant les réponses fournies.
3.  **Interface Utilisateur Réactive** : Application Single Page (SPA) avec support natif du mode sombre.
4.  **Authentification Centralisée** : Simulation d'un environnement d'entreprise via connexion LDAP sécurisée.

---

## Installation via Docker Hub (Production/Test)

Cette méthode est recommandée pour un déploiement rapide sans compilation locale.

### Prérequis
- Docker Engine et Docker Compose installés.

### Procédure

1.  Créer un fichier `docker-compose.yml` avec le contenu suivant :

    ```yaml
    services:
      backend-api:
        image: serini/safran-backend-api:v2.0
        ports:
          - "8000:8000"
        depends_on:
          ldap-service:
            condition: service_healthy
          ollama:
            condition: service_healthy
        environment:
          - LDAP_HOST=ldap-service
          - OLLAMA_BASE_URL=http://ollama:11434
          - OLLAMA_MODEL=llama3.2:3b

      frontend-ui:
        image: serini/safran-frontend-ui:v2.0
        ports:
          - "5173:80"
        depends_on:
          - backend-api

      ldap-service:
        image: osixia/openldap:1.5.0
        ports:
          - "389:389"
          - "636:636"
        environment:
          - LDAP_ORGANISATION=Serini
          - LDAP_DOMAIN=serini.local
          - LDAP_ADMIN_PASSWORD=SecureAdminPass123!
          - LDAP_TLS=false
        healthcheck:
          test: ["CMD", "ldapsearch", "-x", "-H", "ldap://localhost", "-b", "", "-s", "base"]
          interval: 30s
          retries: 5

      ollama:
        image: ollama/ollama:latest
        ports:
          - "11434:11434"
        volumes:
          - ollama-data:/root/.ollama
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
          interval: 30s
          retries: 3

    volumes:
      ollama-data:
    ```

2.  Démarrer l'environnement :
    ```bash
    docker compose up -d
    ```

3.  Procéder à la [Configuration et Initialisation](#configuration-et-initialisation).

---

## Installation via GitHub (Développement)

Pour contribuer au projet ou modifier la configuration.

1.  Cloner le dépôt :
    ```bash
    git clone https://github.com/votre-user/safran-chatbot.git
    cd safran-chatbot
    ```

2.  Construire et démarrer les services :
    ```bash
    docker compose up -d --build
    ```

3.  Procéder à la [Configuration et Initialisation](#configuration-et-initialisation).

---

## Installation Manuelle (Code Source)

Exécution locale des applications (Backend et Frontend) hors conteneurs.
*Note : Il est fortement recommandé d'utiliser Docker pour les services LDAP et Ollama.*

### 1. Démarrage des Services Dépendants (Docker)

```bash
docker compose up -d ldap-service ollama
```

### 2. Backend (Python)

```bash
cd backend
python -m venv venv
# Activation: source venv/bin/activate (Linux/Mac) ou venv\Scripts\activate (Windows)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
*Assurez-vous que les variables d'environnement pointent vers localhost pour LDAP et Ollama.*

### 3. Frontend (Node.js)

```bash
cd frontend
npm install
npm run dev
```

---

## Configuration et Initialisation

Une fois les conteneurs ou services démarrés, il est impératif d'initialiser le modèle d'IA et les données de test.

### 1. Téléchargement du Modèle LLM

Le modèle `llama3.2:3b` (environ 2 Go) doit être téléchargé dans le conteneur Ollama.

**Via script (si disponible localement) :**
```bash
./setup-ollama.sh
```

**Via commande Docker manuelle :**
```bash
docker exec -it <nom_conteneur_ollama> ollama pull llama3.2:3b
```

### 2. Population de l'Annuaire LDAP

Création de la structure organisationnelle et des utilisateurs de test.

**Via script :**
```bash
./setup-ldap.sh
```

### Comptes de Test Disponibles

| Identifiant | Mot de passe | Profil |
|-------------|--------------|--------|
| **alice**   | password     | CDI / Cadre |
| **bob**     | password     | CDD / Non-Cadre |
| **charlie** | password     | Intérimaire |
| **david**   | password     | Stagiaire |

---

## Utilisation et Scénarios de Test

Accès à l'application : **http://localhost:5173**

### Scénarios de Validation

1.  **Interaction Conversationnelle (LLM)**
    - **Entrée** : "Bonjour, qui êtes-vous ?"
    - **Comportement attendu** : Réponse fluide générée par le LLM sans consultation de la base documentaire.

2.  **Requête Métier (RAG + LLM)**
    - **Entrée** : "Quelle est la procédure pour poser des congés ?"
    - **Comportement attendu** : Identification du contexte RH, récupération des règles spécifiques, et génération d'une réponse précise incluant les démarches (Portail RH, délais).

3.  **Filtrage de Domaine**
    - **Entrée** : "Quel est le score du match d'hier ?"
    - **Comportement attendu** : Le système identifie la question comme hors-sujet RH et décline poliment la réponse.

---

**Développé par l'équipe d'ingénierie Serini**
