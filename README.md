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

## Installation

Nous proposons deux méthodes d'installation : **Automatique** (recommandée) et **Manuelle**.

### Méthode 1 : Installation Automatique (Recommandée)

Le script `install.sh` automatise tout le processus : construction des images, démarrage des conteneurs, initialisation LDAP et téléchargement du modèle IA.

1.  **Lancer l'installation** :
    ```bash
    ./install.sh
    ```
    *Note : Soyez patient, le téléchargement du modèle IA (2 Go) peut prendre quelques minutes.*

2.  **Accéder à l'application** :
    - URL : [http://localhost:5173](http://localhost:5173)

---

### Méthode 2 : Installation Manuelle (Docker Compose)

Si vous préférez contrôler chaque étape.

1.  **Démarrer les services** :
    ```bash
    docker compose up -d --build
    ```

2.  **Initialiser l'Annuaire LDAP** (Requis pour la connexion) :
    ```bash
    ./setup-ldap.sh
    ```

3.  **Installer le Modèle IA** (Requis pour le chat) :
    ```bash
    ./setup-ollama.sh
    # Ou manuellement : docker exec hr-ollama ollama pull llama3.2:3b
    ```

---

## Vérification et Tests

Nous fournissons un script de vérification automatisé pour s'assurer que le système répond correctement.

### 1. Lancer les tests de vérification
```bash
./verify_bot.sh
```
Ce script va :
- Vérifier la connexion de tous les utilisateurs types.
- Tester la réponse "Bonjour" (Salutation standardisée).
- Tester des questions RH spécifiques (RAG) pour chaque profil.

### 2. Comptes de Test Disponibles

Utilisez ces comptes pour vous connecter à l'application :

| Utilisateur | Mot de passe | Profil      | Accès                                      |
|-------------|--------------|-------------|--------------------------------------------|
| **alice**   | password     | Cadre       | Tout accès + Gestion Manager               |
| **bob**     | password     | CDI         | Accès standard (Congés, Avantages)        |
| **charlie** | password     | Intérimaire | Accès limité (Missions, Sécurité)         |
| **david**   | password     | Stagiaire   | Accès limité (Stage, Cantine)             |
| **emma**    | password     | CDD         | Accès standard (Contrat durée déterminée) |
| **frank**   | password     | Non-Cadre   | Accès standard                             |

---

## Utilisation

1.  Connectez-vous avec un des comptes ci-dessus.
2.  Posez une question (ex: "Comment poser des congés ?").
3.  Le chatbot vous répondra en utilisant la base de connaissance interne.
    - **Questions RH** : Réponse factuelle issue de la base.
    - **Salutations/Hors-sujet** : Réponse conversationnelle courte ("Bonjour !...").

## Dépannage

- **Erreur "Model not found"** : Relancez `./setup-ollama.sh`.
- **Login impossible** : Relancez `./setup-ldap.sh`.
- **Application non accessible** : Vérifiez que les conteneurs tournent avec `docker ps`.

---

**Développé par l'équipe d'ingénierie Serini**
