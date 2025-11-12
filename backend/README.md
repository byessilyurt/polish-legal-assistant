# Polish Legal Assistant - Backend API

Production-ready FastAPI backend with RAG (Retrieval Augmented Generation) capabilities for the Polish Legal Assistant chatbot.

## Overview

This backend service provides AI-powered assistance for foreigners navigating Polish law and daily life. It uses:

- **FastAPI** for the REST API
- **LangChain** for RAG orchestration
- **Pinecone** for vector database storage
- **OpenAI GPT-4o** for response generation
- **OpenAI text-embedding-3-large** for text embeddings

## Architecture

```
User Query → FastAPI → RAG Service → Retrieval Service → Pinecone
                            ↓
                       LLM Service → OpenAI GPT-4o
                            ↓
                    Response with Citations
```

### RAG Pipeline

1. **Query Processing**: User submits a question
2. **Embedding Generation**: Convert query to vector using OpenAI embeddings
3. **Vector Search**: Query Pinecone for relevant documents
4. **Context Construction**: Format retrieved documents with citations
5. **LLM Generation**: Generate response using GPT-4o with context
6. **Response Formatting**: Return answer with source citations

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py                # Chat endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py         # RAG orchestration
│   │   ├── retrieval_service.py   # Pinecone operations
│   │   └── llm_service.py         # OpenAI interactions
│   └── models/
│       ├── __init__.py
│       └── schemas.py             # Pydantic models
├── tests/
│   ├── __init__.py
│   └── test_rag.py                # Test suite
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
└── README.md                      # This file
```

## Installation

### Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Pinecone API key and index

### Local Setup

1. **Clone the repository** (if not already done):
   ```bash
   cd /path/to/polish-legal-assistant/backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   Create a `.env` file in the backend directory:
   ```bash
   # OpenAI Configuration
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-4o
   OPENAI_EMBEDDING_MODEL=text-embedding-3-large
   OPENAI_TEMPERATURE=0.3
   OPENAI_MAX_TOKENS=1500

   # Pinecone Configuration
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_ENVIRONMENT=your-pinecone-environment
   PINECONE_INDEX_NAME=polish-legal-docs

   # RAG Configuration
   RAG_TOP_K=5
   RAG_SIMILARITY_THRESHOLD=0.7
   RAG_MAX_CONTEXT_LENGTH=6000

   # Application Configuration
   DEBUG=False
   LOG_LEVEL=INFO
   CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
   ```

5. **Run the application**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at:
   - API: http://localhost:8000
   - Interactive docs (Swagger): http://localhost:8000/docs
   - Alternative docs (ReDoc): http://localhost:8000/redoc

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `PINECONE_API_KEY` | Pinecone API key | `...` |
| `PINECONE_ENVIRONMENT` | Pinecone environment | `us-west1-gcp` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_MODEL` | OpenAI model for responses | `gpt-4o` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-large` |
| `OPENAI_TEMPERATURE` | Response temperature | `0.3` |
| `OPENAI_MAX_TOKENS` | Max response tokens | `1500` |
| `PINECONE_INDEX_NAME` | Pinecone index name | `polish-legal-docs` |
| `RAG_TOP_K` | Documents to retrieve | `5` |
| `RAG_SIMILARITY_THRESHOLD` | Min similarity score | `0.7` |
| `DEBUG` | Debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |

## API Endpoints

### Health Check

```http
GET /health
```

Returns service health status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "openai_configured": true,
  "pinecone_configured": true,
  "timestamp": "2025-11-11T10:30:00Z"
}
```

### Chat Query

```http
POST /api/v1/chat
```

Process a user query through the RAG pipeline.

**Request:**
```json
{
  "query": "What documents do I need for a temporary residence permit?",
  "category_filter": "immigration",
  "top_k": 5,
  "include_debug": false
}
```

**Response:**
```json
{
  "answer": "To apply for a temporary residence permit in Poland, you need the following documents [1]:\n\n1. Valid passport\n2. Completed application form\n3. Photographs (3.5cm x 4.5cm)\n4. Proof of health insurance\n5. Document justifying the purpose of stay [2]\n\nProcessing time is typically 1-2 months [1].",
  "sources": [
    {
      "id": "1",
      "title": "Temporary Residence Permit Requirements",
      "organization": "Polish Ministry of Interior",
      "url": "https://www.gov.pl/web/mswia/temporary-residence",
      "last_verified": "2025-11-01",
      "relevance_score": 0.92,
      "category": "immigration"
    }
  ],
  "confidence": 0.89,
  "category": "immigration",
  "timestamp": "2025-11-11T10:30:00Z"
}
```

### RAG Health Check

```http
GET /api/v1/chat/health
```

Check RAG service health.

**Response:**
```json
{
  "retrieval_service": true,
  "llm_service": true,
  "overall_healthy": true
}
```

## Testing

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_rag.py -v
```

### Test Coverage

The test suite covers:
- Health check endpoints
- Chat endpoint validation
- Request/response models
- Configuration handling
- Error handling for missing API keys
- API documentation endpoints

## Docker Deployment

### Build Docker Image

```bash
docker build -t polish-legal-assistant-backend .
```

### Run Docker Container

```bash
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e PINECONE_API_KEY=your-key \
  -e PINECONE_ENVIRONMENT=your-env \
  --name polish-legal-backend \
  polish-legal-assistant-backend
```

### Using Docker Compose

Create a `docker-compose.yml` in the project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

## Development

### Code Style

This project uses:
- **Black** for code formatting
- **Type hints** throughout
- **Pydantic** for data validation
- **Async/await** for better performance

Format code:
```bash
black app/ tests/
```

### Logging

Logs are configured based on the `LOG_LEVEL` environment variable:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Adding New Endpoints

1. Create a new router in `app/api/`
2. Define Pydantic models in `app/models/schemas.py`
3. Implement business logic in `app/services/`
4. Register router in `app/main.py`
5. Add tests in `tests/`

## Error Handling

The API provides clear error messages for common issues:

### Missing Configuration

```json
{
  "answer": "I apologize, but I encountered an issue: OpenAI API key is not configured. Please set OPENAI_API_KEY environment variable.",
  "sources": [],
  "confidence": 0.0
}
```

### No Relevant Documents

```json
{
  "answer": "I apologize, but I couldn't find relevant information in my knowledge base...",
  "sources": [],
  "confidence": 0.0
}
```

## Performance Considerations

- **Caching**: Settings are cached using `lru_cache`
- **Async Operations**: All I/O operations use async/await
- **Connection Pooling**: OpenAI and Pinecone clients reuse connections
- **Retry Logic**: Automatic retry for transient failures (3 attempts)

## Security

- **Non-root user**: Docker container runs as non-root user
- **Input validation**: All inputs validated with Pydantic
- **Environment variables**: Sensitive data in environment variables
- **CORS**: Configurable allowed origins

## Monitoring

### Health Checks

- **Kubernetes**: Use `/health` endpoint for liveness/readiness probes
- **Docker**: Built-in healthcheck in Dockerfile
- **Uptime monitoring**: Use `/health` endpoint

### Metrics

Consider adding:
- Prometheus metrics export
- Request/response logging
- Error rate tracking
- Response time monitoring

## Troubleshooting

### API Key Issues

If you see "not configured" errors:
1. Verify `.env` file exists in backend directory
2. Check environment variables are properly set
3. Restart the application

### Pinecone Connection Issues

1. Verify Pinecone API key and environment
2. Ensure index exists: check Pinecone console
3. Check index name matches configuration

### OpenAI Rate Limits

1. Monitor usage in OpenAI dashboard
2. Implement rate limiting on API endpoints
3. Consider caching frequent queries

## Production Deployment

### Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure production CORS origins
- [ ] Set up proper logging (e.g., to file or log aggregation)
- [ ] Implement rate limiting
- [ ] Add authentication (API keys, OAuth, etc.)
- [ ] Set up monitoring and alerting
- [ ] Configure SSL/TLS
- [ ] Use environment-specific `.env` files
- [ ] Set up CI/CD pipeline
- [ ] Configure backup for logs

### Recommended Services

- **Hosting**: AWS ECS, Google Cloud Run, Railway, Render
- **Database**: Pinecone (already configured)
- **Monitoring**: Datadog, New Relic, Sentry
- **Logging**: CloudWatch, Stackdriver, Papertrail

## Contributing

When contributing to the backend:

1. Follow existing code style (Black formatting)
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation
5. Ensure all tests pass before submitting

## License

See the main project LICENSE file.

## Support

For issues or questions:
- Check the documentation at `/docs`
- Review error messages in logs
- Consult the test suite for examples
- Check Pinecone and OpenAI status pages

## Next Steps

1. **Set up API keys**: Add your OpenAI and Pinecone keys to `.env`
2. **Populate Pinecone**: Use the knowledge pipeline to add documents
3. **Test the API**: Use the Swagger UI at `/docs` to test endpoints
4. **Deploy**: Follow the Docker deployment guide
5. **Monitor**: Set up health checks and logging
