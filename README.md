# 🤖 Chatbot RH - HR Assistant Application

A complete microservices-based HR Chatbot application with LDAP authentication, RAG-powered Q&A, and a modern React UI with dark/light theme support.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Test Users](#test-users)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## 🏗️ Architecture

The application consists of three microservices:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Frontend UI    │─────▶│  Backend API    │─────▶│  LDAP Service   │
│  (React+Vite)   │      │  (FastAPI)      │      │  (OpenLDAP)     │
│  Port: 5173     │      │  Port: 8000     │      │  Port: 389      │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                │
                                │
                         ┌──────▼──────┐
                         │             │
                         │  RAG Engine │
                         │  (Sentence  │
                         │ Transformers)│
                         │             │
                         └─────────────┘
```

### Components

1. **LDAP Service** (`ldap-service`)
   - OpenLDAP directory server
   - Domain: `serini.local`
   - Pre-populated with test users
   - Stores user profiles (employeeType, title, department)

2. **Backend API** (`backend-api`)
   - FastAPI REST API
   - JWT authentication (access + refresh tokens)
   - LDAP integration for user authentication
   - RAG engine for semantic Q&A
   - Profile-based answer filtering

3. **Frontend UI** (`frontend-ui`)
   - React 18 with Vite
   - TailwindCSS with dark/light theme
   - Real-time chat interface
   - Automatic token refresh

## ✨ Features

- 🔐 **Secure Authentication**: LDAP-based authentication with JWT tokens
- 🔄 **Token Refresh**: Automatic access token refresh using refresh tokens
- 🧠 **Smart Q&A**: RAG-powered semantic search with sentence-transformers
- 👤 **Profile-Based Filtering**: Answers filtered by user's employment type and title
- 🌓 **Dark/Light Theme**: User-selectable theme with localStorage persistence
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🐳 **Containerized**: Fully Dockerized for easy deployment
- 🔒 **Secure**: CORS protection, httpOnly cookies, secure headers

## 📦 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- Ports available: 389, 636, 5173, 8000

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd /home/omar/myWork/safran
```

### 2. Create Environment File

```bash
cp .env.example .env
```

**Important**: Edit `.env` and change the JWT secret keys for production:

```bash
# Generate secure random keys
openssl rand -hex 32  # Use for JWT_SECRET_KEY
openssl rand -hex 32  # Use for JWT_REFRESH_SECRET_KEY
```

### 3. Start All Services

```bash
docker compose up -d
```

This will:
- Build the backend and frontend images
- Start LDAP service
- Initialize the RAG engine
- Start all services

### 4. Setup LDAP Users

After the services are running, populate LDAP with test users:

```bash
./setup-ldap.sh
```

This script will:
- Copy the bootstrap LDIF file to the LDAP container
- Create organizational units (People, Groups)
- Add 4 test users with their profiles
- Create user groups

### 5. Verify Services

```bash
# Check all services are running
docker compose ps

# Check backend logs
docker compose logs backend-api

# Check LDAP logs
docker compose logs ldap-service
```

### 5. Access the Application

Open your browser and navigate to:

```
http://localhost:5173
```

## ⚙️ Configuration

### Environment Variables

All configuration is managed through environment variables in `.env`:

#### LDAP Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LDAP_HOST` | `ldap-service` | LDAP server hostname |
| `LDAP_PORT` | `389` | LDAP server port |
| `LDAP_DOMAIN` | `serini.local` | LDAP domain |
| `LDAP_BASE_DN` | `dc=serini,dc=local` | LDAP base DN |
| `LDAP_ADMIN_DN` | `cn=admin,dc=serini,dc=local` | LDAP admin DN |
| `LDAP_ADMIN_PASSWORD` | `SecureAdminPass123!` | LDAP admin password |

#### JWT Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | *(change in production)* | Secret key for access tokens |
| `JWT_REFRESH_SECRET_KEY` | *(change in production)* | Secret key for refresh tokens |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access token validity (1 hour) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token validity (7 days) |

#### CORS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Allowed CORS origins |

#### Frontend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API URL |

## 📚 API Documentation

### Authentication Endpoints

#### POST `/api/auth/login`

Authenticate user and receive tokens.

**Request:**
```json
{
  "username": "alice",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### POST `/api/auth/refresh`

Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### User Endpoints

#### GET `/api/profile`

Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "username": "alice",
  "full_name": "Alice Dupont",
  "email": "alice.dupont@serini.local",
  "employee_type": "CDI",
  "title": "Cadre",
  "department": "IT"
}
```

### Chat Endpoints

#### POST `/api/chat`

Send message to chatbot (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "message": "Comment poser un congé annuel ?"
}
```

**Response:**
```json
{
  "question": "Comment poser un congé annuel ?",
  "answer": "La demande se fait via le portail RH au moins 7 jours à l'avance",
  "profile": "CDI/Cadre",
  "domain": "Congés"
}
```

### Health Check

#### GET `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

## 👥 Test Users

The LDAP service is pre-populated with the following test users:

| Username | Password | Employee Type | Title | Department |
|----------|----------|---------------|-------|------------|
| `alice` | `password` | CDI | Cadre | IT |
| `bob` | `password` | CDD | Non-Cadre | Sales |
| `charlie` | `password` | Intérim | Non-Cadre | Logistics |
| `david` | `password` | Stagiaire | Non-Cadre | Marketing |

### Testing Profile-Based Filtering

1. Login as **alice** (CDI/Cadre)
   - Ask: "Comment poser un congé annuel ?"
   - Expected: CDI-specific answer

2. Login as **bob** (CDD/Non-Cadre)
   - Ask: "Ai-je droit aux congés payés ?"
   - Expected: CDD-specific answer

3. Login as **charlie** (Intérim)
   - Ask: "Ai-je accès au transport ?"
   - Expected: Intérim-specific answer

4. Login as **david** (Stagiaire)
   - Ask: "Ai-je accès à la cantine ?"
   - Expected: Stagiaire-specific answer

## 🛠️ Development

### Running Services Individually

#### Backend Only

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Only

```bash
cd frontend
npm install
npm run dev
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend-api
docker compose logs -f frontend-ui
docker compose logs -f ldap-service
```

### Rebuilding Services

```bash
# Rebuild all services
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build backend-api
```

### Stopping Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes LDAP data)
docker compose down -v
```

## 🔧 Troubleshooting

### LDAP Connection Issues

**Problem**: Backend cannot connect to LDAP

**Solution**:
```bash
# Check LDAP service is running
docker compose ps ldap-service

# Test LDAP connection
docker exec -it hr-ldap ldapsearch -x -H ldap://localhost \
  -b "dc=serini,dc=local" \
  -D "cn=admin,dc=serini,dc=local" \
  -w "SecureAdminPass123!"

# Check LDAP logs
docker compose logs ldap-service
```

### Backend API Not Starting

**Problem**: Backend fails to start

**Solution**:
```bash
# Check backend logs
docker compose logs backend-api

# Common issues:
# 1. LDAP service not ready - wait for health check
# 2. Missing CSV file - check backend/data/knowledge_base.csv exists
# 3. Model download failed - check internet connection
```

### Frontend Cannot Connect to Backend

**Problem**: API calls fail with CORS or network errors

**Solution**:
1. Check `VITE_API_BASE_URL` in `.env`
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check browser console for CORS errors
4. Verify `CORS_ORIGINS` includes frontend URL

### Token Refresh Not Working

**Problem**: User gets logged out unexpectedly

**Solution**:
1. Check JWT secret keys match in backend
2. Verify token expiration times in `.env`
3. Check browser localStorage for tokens
4. Review backend logs for token validation errors

### Dark Mode Not Persisting

**Problem**: Theme resets on page refresh

**Solution**:
1. Check browser localStorage (should have `theme` key)
2. Clear browser cache and try again
3. Verify JavaScript is enabled

## 🚀 Production Deployment

### Security Checklist

- [ ] Change `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY`
- [ ] Change `LDAP_ADMIN_PASSWORD`
- [ ] Update `CORS_ORIGINS` to production domains
- [ ] Enable HTTPS/TLS for all services
- [ ] Use secure LDAP (LDAPS) on port 636
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure proper firewall rules
- [ ] Set up monitoring and logging
- [ ] Configure backup for LDAP data

### Docker Compose Production

```yaml
# docker compose.prod.yml
version: '3.8'

services:
  backend-api:
    restart: always
    environment:
      - ENVIRONMENT=production
    # Add production-specific configs

  frontend-ui:
    restart: always
    # Add production-specific configs

  ldap-service:
    restart: always
    # Add production-specific configs
```

### Deployment Steps

1. **Prepare Environment**
   ```bash
   cp .env.example .env.production
   # Edit .env.production with production values
   ```

2. **Build Images**
   ```bash
   docker compose -f docker compose.yml --env-file .env.production build
   ```

3. **Deploy**
   ```bash
   docker compose -f docker compose.yml --env-file .env.production up -d
   ```

4. **Verify**
   ```bash
   docker compose ps
   curl https://your-domain.com/health
   ```

### Scaling

To scale the backend:

```bash
docker compose up -d --scale backend-api=3
```

Add a load balancer (nginx, traefik) in front of backend instances.

## 📝 License

This project is for demonstration purposes.

## 🤝 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Docker logs: `docker compose logs`
3. Check API documentation: http://localhost:8000/docs

---

**Built with**: FastAPI, React, OpenLDAP, Sentence Transformers, Docker
