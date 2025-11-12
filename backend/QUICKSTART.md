# Quick Start Guide

Get the Polish Legal Assistant backend running in 5 minutes.

## Prerequisites

- Python 3.11+
- OpenAI API key
- Pinecone API key

## Setup Steps

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# Required:
#   - OPENAI_API_KEY
#   - PINECONE_API_KEY
#   - PINECONE_ENVIRONMENT
```

### 3. Verify Setup

```bash
# Run verification script
python verify_setup.py
```

### 4. Start the Server

```bash
# Option 1: Use the helper script
./run.sh

# Option 2: Run directly
uvicorn app.main:app --reload
```

### 5. Test the API

Visit http://localhost:8000/docs for interactive API documentation.

## Quick Test

```bash
# Check health
curl http://localhost:8000/health

# Send a test query
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What documents do I need for a residence permit?"
  }'
```

## Troubleshooting

### "OpenAI not configured"
- Check that OPENAI_API_KEY is set in .env
- Verify the API key is valid at https://platform.openai.com/api-keys

### "Pinecone not configured"
- Check that PINECONE_API_KEY and PINECONE_ENVIRONMENT are set
- Verify your Pinecone index exists at https://app.pinecone.io/

### "No module named 'app'"
- Ensure you're in the backend directory
- Activate your virtual environment

### Port already in use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

## Next Steps

1. **Populate the knowledge base**: Use the knowledge pipeline to add documents to Pinecone
2. **Test queries**: Try different types of questions in the API docs
3. **Adjust settings**: Modify RAG_TOP_K and RAG_SIMILARITY_THRESHOLD in .env
4. **Review logs**: Check console output for errors and performance metrics

## Useful Commands

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app

# Format code
black app/ tests/

# Check types (if mypy installed)
mypy app/

# Build Docker image
docker build -t polish-legal-backend .

# Run Docker container
docker run -p 8000:8000 --env-file .env polish-legal-backend
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `POST /api/v1/chat` - Chat with the assistant
- `GET /api/v1/chat/health` - RAG service health

## Configuration Tips

### For Development
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

### For Production
```bash
DEBUG=False
LOG_LEVEL=INFO
OPENAI_TEMPERATURE=0.2  # More deterministic
RAG_TOP_K=7  # More context
```

### For Testing
```bash
RAG_TOP_K=3  # Faster responses
LOG_LEVEL=WARNING  # Less noise
```

## Getting Help

- Full documentation: `README.md`
- API docs: http://localhost:8000/docs
- Test examples: `tests/test_rag.py`
- Configuration: `app/config.py`

## Common Issues

**Q: Responses are slow**
A: Reduce RAG_TOP_K or OPENAI_MAX_TOKENS in .env

**Q: Answers are not accurate**
A: Increase RAG_TOP_K and lower RAG_SIMILARITY_THRESHOLD

**Q: Getting rate limit errors**
A: Implement rate limiting or upgrade your OpenAI plan

**Q: Pinecone index is empty**
A: Run the knowledge pipeline to populate documents first
