# Correction du Système de Profils + Docker Hub Push

## Problème Corrigé: Profils Uniques

### Avant (Incorrect)
Chaque utilisateur avait **2 attributs** combinés:
- employeeType: CDI, CDD, INTÉRIMAIRE, STAGIAIRE
- title: CADRE, NON-CADRE

Affichage: "Alice Dupont - CDI / CADRE" [INCORRECT]

### Maintenant (Correct)
Chaque utilisateur a **1 seul profil** parmi les 6:
- CDI
- CDD  
- CADRE
- NON-CADRE
- INTÉRIMAIRE
- STAGIAIRE

Affichage: "Alice Dupont - CADRE" [CORRECT]

---

## Utilisateurs Mis à Jour

| Utilisateur | Profil | Département |
|-------------|--------|-------------|
| alice | **CADRE** | IT |
| bob | **CDI** | Sales |
| charlie | **INTÉRIMAIRE** | Logistics |
| david | **STAGIAIRE** | Marketing |

---

## Push Docker Hub Simplifié

### Configuration docker-compose.yml

Le `docker-compose.yml` est maintenant configuré avec les noms d'images Docker Hub:

```yaml
backend-api:
  image: safran/safran-backend-api:latest
  build: ...

frontend-ui:
  image: safran/safran-frontend-ui:latest
  build: ...
```

### Commandes pour Push

```bash
# 1. Connexion à Docker Hub
docker login -u safran

# 2. Build des images
docker compose build

# 3. Push sur Docker Hub (automatique!)
docker compose push

# Done!
```

### Images Disponibles

Après le push, les images seront disponibles sur:
- `docker pull safran/safran-backend-api:latest`
- `docker pull safran/safran-frontend-ui:latest`

---

## Pour Appliquer les Changements

```bash
cd /home/omar/myWork/safran

# Arrêter les services actuels
docker compose down -v

# Reconstruire avec les nouveaux profils
docker compose build

# Démarrer
docker compose up -d

# Configurer LDAP avec les nouveaux profils
./setup-ldap.sh

# (Optionnel) Push sur Docker Hub
docker login -u safran
docker compose push
```

---

## Résultat Final

### Affichage Frontend
- [x] "Connecté en tant que Alice Dupont - CADRE"
- [x] "Connecté en tant que Bob Martin - CDI"
- [x] "Connecté en tant que Charlie Bernard - INTÉRIMAIRE"
- [x] "Connecté en tant que David Petit - STAGIAIRE"

### Filtrage RAG
Chaque profil voit **uniquement** ses questions:
- CADRE → Questions CADRE
- CDI → Questions CDI
- INTÉRIMAIRE → Questions INTÉRIMAIRE
- STAGIAIRE → Questions STAGIAIRE
- etc.

### Docker Hub
- [x] Images taguées avec `safran/`
- [x] Push simple avec `docker compose push`
- [x] Pull facile pour déploiement

---

## Fichiers Modifiés

1. [x] `infra/ldap/bootstrap.ldif` - Profils uniques
2. [x] `backend/app/ldap_service.py` - Suppression de `title`
3. [x] `backend/app/models.py` - Modèle UserProfile mis à jour
4. [x] `backend/app/rag.py` - Filtrage sur 1 seul attribut
5. [x] `backend/app/main.py` - Endpoint chat mis à jour
6. [x] `frontend/src/components/Chat.jsx` - Affichage profil unique
7. [x] `docker-compose.yml` - Noms d'images Docker Hub
8. [x] `push-dockerhub.sh` - Script de push (optionnel)

**Tout est prêt!**
