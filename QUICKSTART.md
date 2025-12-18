# HR Chatbot Application - READY TO USE

## Project Location
```
/home/omar/myWork/safran
```

## Quick Start (3 Steps)

### 1. Start the Application
```bash
cd /home/omar/myWork/safran
docker compose up -d
```

### 2. Setup LDAP Users
```bash
./setup-ldap.sh
```

### 3. Access the Application
Open your browser: **http://localhost:5173**

## Test Users

| Username | Password | Profile | Use Case |
|----------|----------|---------|----------|
| `alice` | `password` | CDI / Cadre | Full-time manager |
| `bob` | `password` | CDD / Non-Cadre | Fixed-term employee |
| `charlie` | `password` | Intérim | Temporary worker |
| `david` | `password` | Stagiaire | Intern |

## Features to Try

1. **Login** with any test user
2. **Theme Toggle** - Click the sun/moon icon
3. **Ask Questions**:
   - "Comment poser un congé annuel ?" (as alice - CDI)
   - "Ai-je droit aux congés payés ?" (as bob - CDD)
   - "Ai-je accès à la cantine ?" (as david - Stagiaire)
4. **Profile Display** - See your user info in the header
5. **Auto Token Refresh** - Tokens refresh automatically

## Services Running

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **LDAP**: localhost:389

## Useful Commands

```bash
# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend-api
docker compose logs -f frontend-ui
docker compose logs -f ldap-service

# Restart services
docker compose restart

# Stop services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

## Documentation

- **README**: [`README.md`](file:///home/omar/myWork/safran/README.md) - Complete documentation
- **Walkthrough**: See artifacts for implementation details
- **API Docs**: http://localhost:8000/docs (Swagger UI)

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  React Frontend │─────▶│  FastAPI Backend│─────▶│  OpenLDAP       │
│  Port: 5173     │      │  Port: 8000     │      │  Port: 389      │
│  (Nginx)        │      │  (RAG + Auth)   │      │  (User Profiles)│
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Security Notes

**For Development**:
- JWT secrets are set in `.env`
- LDAP admin password: `SecureAdminPass123!`
- All test users have password: `password`

**For Production**:
1. Change JWT secret keys (use `openssl rand -hex 32`)
2. Change LDAP admin password
3. Enable HTTPS
4. Update CORS origins
5. Use strong user passwords

## UI Features

- [x] Dark/Light theme (persists in localStorage)
- [x] Responsive design (mobile, tablet, desktop)
- [x] Real-time chat interface
- [x] User profile display
- [x] Loading states and animations
- [x] Error handling with user-friendly messages

## RAG Engine

- **Model**: all-MiniLM-L6-v2 (sentence-transformers)
- **Knowledge Base**: 10 Q&A entries
- **Filtering**: Answers filtered by user profile (CDI, CDD, Intérim, Stagiaire, Cadre, Non-Cadre)
- **Search**: Semantic search with cosine similarity

## Files Created

**Total**: 35+ files including:
- Docker configuration
- Backend API (FastAPI)
- Frontend UI (React)
- LDAP setup
- Documentation

## Troubleshooting

### Services won't start?
```bash
docker compose down -v
docker compose up -d
./setup-ldap.sh
```

### LDAP users not working?
```bash
./setup-ldap.sh
```

### Frontend not loading?
Check if port 5173 is available:
```bash
lsof -i :5173
```

### Backend errors?
Check logs:
```bash
docker compose logs backend-api
```

## Next Steps

1. **Try the Application**: Login and chat with different users
2. **Explore the Code**: Check the implementation files
3. **Customize**: Add more Q&A entries to `backend/data/knowledge_base.csv`
4. **Deploy**: Follow production deployment guide in README

## Support

- Check [`README.md`](file:///home/omar/myWork/safran/README.md) for detailed documentation
- View API documentation at http://localhost:8000/docs
- Check Docker logs for debugging

---

**Enjoy your HR Chatbot!**
