# Push Docker Hub - Guide de Versioning

## Stratégie de Versioning

### Versions Disponibles

| Version | Description | Tags |
|---------|-------------|------|
| **v1.0** | Version initiale sans Ollama | `v1.0` |
| **v2.0** | Version avec Ollama LLM | `v2.0`, `latest` |

### Avantages

- [x] **v1.0 préservée**: L'ancienne version reste disponible
- [x] **v2.0 nouvelle**: Nouvelle version avec Ollama
- [x] **latest pointe vers v2.0**: Par défaut, on utilise la dernière version
- [x] **Rollback facile**: Possibilité de revenir à v1.0 si besoin

---

## Push sur Docker Hub

### Méthode 1: Script Automatique (Recommandé)

```bash
# Exécuter le script
./push-dockerhub.sh
```

Le script va:
1. Vérifier la connexion Docker Hub
2. Tagger les images avec `v2.0` et `latest`
3. Pousser sur Docker Hub
4. Afficher un résumé

---

### Méthode 2: Commandes Manuelles

```bash
# 1. Login Docker Hub
docker login -u serini

# 2. Tag backend
docker tag safran-backend-api:latest serini/safran-backend-api:v2.0
docker tag safran-backend-api:latest serini/safran-backend-api:latest

# 3. Tag frontend
docker tag safran-frontend-ui:latest serini/safran-frontend-ui:v2.0
docker tag safran-frontend-ui:latest serini/safran-frontend-ui:latest

# 4. Push backend
docker push serini/safran-backend-api:v2.0
docker push serini/safran-backend-api:latest

# 5. Push frontend
docker push serini/safran-frontend-ui:v2.0
docker push serini/safran-frontend-ui:latest
```

---

### Méthode 3: Docker Compose (Simple)

```bash
# Login
docker login -u serini

# Build et push automatiquement
docker compose build
docker compose push
```

**Note**: Cette méthode pousse seulement le tag `latest`, pas les versions.

---

## Utilisation des Images

### Déployer v2.0 (avec Ollama)

```yaml
# docker-compose.yml
services:
  backend-api:
    image: serini/safran-backend-api:v2.0
    # ...
  
  frontend-ui:
    image: serini/safran-frontend-ui:v2.0
    # ...
  
  ollama:
    image: ollama/ollama:latest
    # ...
```

```bash
docker compose pull
docker compose up -d
```

---

### Déployer v1.0 (sans Ollama - rollback)

```yaml
# docker-compose.yml
services:
  backend-api:
    image: serini/safran-backend-api:v1.0
    # ...
  
  frontend-ui:
    image: serini/safran-frontend-ui:v1.0
    # ...
  
  # Pas de service ollama
```

```bash
docker compose pull
docker compose up -d
```

---

### Déployer latest (toujours la dernière version)

```yaml
# docker-compose.yml
services:
  backend-api:
    image: serini/safran-backend-api:latest
    # ...
  
  frontend-ui:
    image: serini/safran-frontend-ui:latest
    # ...
```

---

## Vérifier les Images sur Docker Hub

### Via Web
1. Aller sur https://hub.docker.com
2. Login avec `serini`
3. Voir les repositories:
   - `serini/safran-backend-api`
   - `serini/safran-frontend-ui`

### Via CLI
```bash
# Lister les tags backend
curl -s https://hub.docker.com/v2/repositories/serini/safran-backend-api/tags | jq '.results[].name'

# Lister les tags frontend
curl -s https://hub.docker.com/v2/repositories/serini/safran-frontend-ui/tags | jq '.results[].name'
```

---

## Changelog

### v2.0 (Nouvelle Version)
- [x] Intégration Ollama LLM (llama3.2:3b)
- [x] RAG hybride intelligent
- [x] Réponses naturelles aux salutations
- [x] 6 profils distincts (CDI, CDD, CADRE, NON-CADRE, INTÉRIMAIRE, STAGIAIRE)
- [x] 15 entrées Q&A dans la base de connaissances
- [x] Affichage du domaine dans le frontend

### v1.0 (Version Initiale)
- [x] RAG simple avec sentence-transformers
- [x] Authentification LDAP
- [x] 4 profils (CDI, CDD, Intérim, Stagiaire)
- [x] 10 entrées Q&A
- [x] Theme toggle (dark/light)

---

## Recommandations

### Pour Production
```bash
# Utiliser des tags versionnés
image: serini/safran-backend-api:v2.0
```
**Avantage**: Contrôle total, pas de surprises

### Pour Développement
```bash
# Utiliser latest
image: serini/safran-backend-api:latest
```
**Avantage**: Toujours la dernière version

### Pour Rollback
```bash
# Revenir à v1.0
docker compose down
# Modifier docker-compose.yml pour utiliser v1.0
docker compose pull
docker compose up -d
```

---

## Sécurité

### Secrets Docker Hub
Ne jamais commiter les credentials Docker Hub dans Git!

```bash
# Login une seule fois
docker login -u serini

# Les credentials sont sauvegardés dans ~/.docker/config.json
```

### CI/CD
Pour automatiser le push dans un pipeline CI/CD:

```bash
# Utiliser des secrets
echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin

# Build et push
docker compose build
docker compose push
```

---

## Résumé

**Commande Rapide**:
```bash
./push-dockerhub.sh
```

**Résultat**:
- [x] v1.0 préservée (sans Ollama)
- [x] v2.0 créée (avec Ollama)
- [x] latest → v2.0
- [x] Rollback possible vers v1.0
