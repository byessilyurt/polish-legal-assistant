# Deployment Guide for Polish Legal Assistant

This guide covers deployment options for the Polish Legal Assistant application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Environment Variables](#environment-variables)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Required API Keys

1. **OpenAI API Key**
   - Sign up: https://platform.openai.com
   - Create API key in dashboard
   - Recommended: Set usage limits

2. **Pinecone API Key**
   - Sign up: https://www.pinecone.io
   - Free tier: 1M vectors (sufficient for MVP)
   - Create API key in console

### System Requirements

- **Local Development:**
  - Python 3.11+
  - Node.js 18+
  - 4GB RAM minimum
  - 10GB disk space

- **Production:**
  - 2 CPU cores minimum
  - 8GB RAM recommended
  - 20GB disk space
  - HTTPS certificate

---

## Local Development

### 1. Initial Setup

```bash
# Clone or navigate to project
cd polish-legal-assistant

# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit .env files with your API keys
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize Pinecone
python ../scripts/init_pinecone.py

# Ingest knowledge base
python ../scripts/ingest_all_knowledge.py

# Run backend
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:3000

---

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# 1. Ensure .env file exists in root directory
cp .env.example .env
# Edit .env with your API keys

# 2. Build and start services
docker-compose up -d

# 3. Check logs
docker-compose logs -f

# 4. Stop services
docker-compose down
```

### Manual Docker Build

**Backend:**
```bash
cd backend
docker build -t polish-legal-backend .
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e PINECONE_API_KEY=your-key \
  --name backend \
  polish-legal-backend
```

**Frontend:**
```bash
cd frontend
docker build -t polish-legal-frontend .
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  --name frontend \
  polish-legal-frontend
```

---

## Cloud Deployment

### Option 1: Vercel (Frontend) + Railway (Backend)

**Frontend on Vercel:**

1. Push code to GitHub
2. Go to https://vercel.com
3. Import GitHub repository
4. Configure:
   - Framework: Next.js
   - Root Directory: `frontend`
   - Environment Variable: `NEXT_PUBLIC_API_URL`
5. Deploy

**Backend on Railway:**

1. Go to https://railway.app
2. Create new project
3. Deploy from GitHub repo
4. Set root directory: `backend`
5. Add environment variables (all from `.env`)
6. Deploy

### Option 2: AWS (Full Stack)

**Architecture:**
- Frontend: AWS Amplify or S3 + CloudFront
- Backend: ECS Fargate or Lambda
- Database: Pinecone (external)

**Steps:**

1. **Backend on ECS:**
```bash
# Build and push to ECR
aws ecr create-repository --repository-name polish-legal-backend
docker tag polish-legal-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/polish-legal-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/polish-legal-backend:latest

# Create ECS task definition and service
# (Use AWS Console or CloudFormation)
```

2. **Frontend on Amplify:**
```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize
amplify init

# Deploy
amplify publish
```

### Option 3: Google Cloud Platform

**Backend on Cloud Run:**

```bash
# Authenticate
gcloud auth login

# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/polish-legal-backend backend/
gcloud run deploy polish-legal-backend \
  --image gcr.io/PROJECT_ID/polish-legal-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=xxx,PINECONE_API_KEY=xxx
```

**Frontend on Firebase Hosting:**

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login and init
firebase login
firebase init hosting

# Build and deploy
cd frontend
npm run build
firebase deploy
```

### Option 4: DigitalOcean App Platform

1. Connect GitHub repository
2. Create app with two components:
   - **Backend:**
     - Type: Web Service
     - Source: backend/
     - Build: `pip install -r requirements.txt`
     - Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - **Frontend:**
     - Type: Static Site
     - Source: frontend/
     - Build: `npm run build`
     - Output: `.next/`

---

## Environment Variables

### Backend (.env)

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Pinecone
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=polish-legal-kb

# RAG Configuration
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7
RAG_MAX_CONTEXT_LENGTH=6000

# Application
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

---

## Monitoring & Maintenance

### Health Checks

**Backend:**
- Endpoint: `GET /health`
- Expected: 200 OK with JSON response

**Frontend:**
- Endpoint: `GET /` (homepage)
- Expected: 200 OK

### Logging

**Backend Logs:**
```bash
# Docker
docker logs backend -f

# Railway
railway logs

# AWS ECS
aws logs tail /ecs/polish-legal-backend --follow
```

**Frontend Logs:**
```bash
# Vercel
vercel logs

# Docker
docker logs frontend -f
```

### Updating Knowledge Base

```bash
# 1. Update JSON files in data/processed/
# 2. Re-run ingestion
python scripts/ingest_all_knowledge.py

# 3. Restart backend (if needed)
docker-compose restart backend
```

### Scaling Considerations

**Backend:**
- Monitor OpenAI API usage and costs
- Implement rate limiting if needed
- Cache frequent queries
- Use load balancer for multiple instances

**Frontend:**
- CDN for static assets
- Image optimization
- Code splitting (already implemented)

**Pinecone:**
- Free tier: 1M vectors
- Paid tiers for more vectors and performance

### Cost Estimation

**Monthly Costs (Estimated):**

- OpenAI API: $50-200 (depends on usage)
- Pinecone: $0 (free tier) or $70+ (standard tier)
- Backend hosting:
  - Railway: $5-20
  - AWS ECS: $20-50
  - GCP Cloud Run: $10-30
- Frontend hosting:
  - Vercel: $0 (hobby) or $20 (pro)
  - Netlify: $0 (free) or $19 (pro)

**Total: $60-350/month**

### Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Enable HTTPS** - Required for production
3. **Rate limiting** - Prevent abuse
4. **Input validation** - Already implemented
5. **CORS configuration** - Restrict to your frontend domain
6. **Regular updates** - Keep dependencies updated

### Troubleshooting

**Issue: "Pinecone index not found"**
- Solution: Run `python scripts/init_pinecone.py`

**Issue: "OpenAI rate limit exceeded"**
- Solution: Implement request queuing or upgrade OpenAI tier

**Issue: "CORS error in frontend"**
- Solution: Check `CORS_ORIGINS` in backend .env

**Issue: "Empty responses from chatbot"**
- Solution: Verify Pinecone has data (`ingest_all_knowledge.py`)

---

## Support

For deployment issues:
1. Check logs first
2. Verify environment variables
3. Test health endpoints
4. Review this guide
5. Open GitHub issue if problem persists

---

**Last Updated:** November 11, 2025
