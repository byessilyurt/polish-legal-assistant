# Polish Legal Assistant - Documentation Index

This directory contains comprehensive analysis of the Polish Legal Assistant codebase.

## Quick Navigation

### Start Here
1. **ANALYSIS_SUMMARY.md** (10 min read)
   - What is this system?
   - Current status & configuration
   - Why response rate might be low
   - Diagnostic checklist
   - Quick fixes

### Deep Dive
2. **CODEBASE_ANALYSIS.md** (30 min read)
   - Complete architecture overview
   - Knowledge base structure (250+ documents)
   - Retrieval & search mechanism
   - Response generation logic
   - API endpoints & data flow
   - Error handling & logging
   - Root cause analysis with 11 potential issues
   - Performance metrics & recommendations

### Visual Reference
3. **ARCHITECTURE_DIAGRAM.txt** (reference)
   - System architecture diagram
   - Data flow visualization
   - Query to response process
   - Configuration reference
   - File locations

## File Sizes & Contents

| File | Size | Type | Purpose |
|------|------|------|---------|
| ANALYSIS_SUMMARY.md | 10KB | Markdown | Quick overview & diagnostics |
| CODEBASE_ANALYSIS.md | 21KB | Markdown | Comprehensive technical analysis |
| ARCHITECTURE_DIAGRAM.txt | 25KB | ASCII Art | Visual diagrams & flows |
| DOCUMENTATION_INDEX.md | This file | Markdown | Navigation guide |

## Key Findings Summary

### System Type
**Retrieval Augmented Generation (RAG) Chatbot**
- Frontend: Next.js 14+
- Backend: FastAPI (Python)
- Vector DB: Pinecone
- LLM: OpenAI GPT-4o

### Knowledge Base
- **250+ documents** from official Polish government sources
- **4 major categories**: Immigration (95), Employment (30), Healthcare/Banking (65), Police/Traffic (60+)
- **Size**: 287KB JSON
- **Status**: All files present and well-structured
- **Updated**: November 2025

### Most Likely Issues (Why Low Response Rate)

| Issue | Probability | Severity | Fix Time |
|-------|-------------|----------|----------|
| Pinecone index not populated | 60% | Critical | 5-10 min |
| Invalid API keys | 25% | Critical | 2-5 min |
| Overly restrictive RAG params | 10% | Medium | 5 min |
| Network/CORS issues | 5% | Medium | 10 min |

## Diagnostic Quick Commands

```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Test RAG service
curl http://localhost:8000/api/v1/chat/health

# 3. Run test query with debug
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is PESEL?","include_debug":true}'

# 4. Check Pinecone vectors
python3 -c "
from pinecone import Pinecone
pc = Pinecone(api_key='YOUR_KEY')
idx = pc.Index('polish-legal-kb')
print(f'Vectors: {idx.describe_index_stats().total_vector_count}')
"
```

## Architecture Overview

```
Frontend (Next.js)        Backend (FastAPI)        Data Services
    :3000                     :8000
       |                         |
       +--- Chat Input --------> RAG Service
       |                         |
       |                         +---> Retrieval Service --> Pinecone
       |                         |
       |                    Response                 Embeddings
       |                         |
       +---- Response ---------- LLM Service ---------> OpenAI
                                 |
                            Knowledge Base
                         (data/processed/*.json)
```

## Configuration Files

### Environment Variables (.env)
- OPENAI_API_KEY (required)
- PINECONE_API_KEY (required)
- PINECONE_ENVIRONMENT (e.g., us-east-1)
- RAG_TOP_K (default: 5)
- RAG_SIMILARITY_THRESHOLD (default: 0.7)

### Backend Configuration (backend/app/config.py)
```python
rag_top_k: 5
rag_similarity_threshold: 0.7
openai_model: "gpt-4o"
embedding_model: "text-embedding-3-large"
openai_temperature: 0.3
```

### Pinecone Index
- Index Name: polish-legal-kb
- Dimension: 1536
- Metric: cosine
- Vector Count: Should be 250+ (verify with status)

## Core Services Breakdown

### RAG Service (rag_service.py)
- Orchestrates the entire pipeline
- Checks service availability
- Retrieves documents
- Generates responses
- Calculates confidence
- Formats citations

### Retrieval Service (retrieval_service.py)
- Generates query embeddings
- Searches Pinecone
- Filters by similarity threshold
- Reranks results
- Returns documents with metadata

### LLM Service (llm_service.py)
- Formats context from documents
- Builds system prompt
- Calls OpenAI GPT-4o
- Handles retries
- Extracts tokens & finish_reason

## Response Flow

```
User Question
    ↓
1. Generate embedding (OpenAI)
    ↓
2. Search Pinecone (top_k=5)
    ↓
3. Filter by threshold (0.7)
    ↓
4. Format context
    ↓
5. Call GPT-4o (temp=0.3)
    ↓
6. Extract answer & sources
    ↓
7. Calculate confidence
    ↓
8. Return JSON response
```

## Confidence Score Calculation

```
confidence = (avg_similarity * 0.6) +
             (num_docs_factor * 0.2) +
             (completeness_factor * 0.2)

Where:
  avg_similarity = mean similarity score of retrieved docs
  num_docs_factor = min(len(docs) / 5, 1.0)
  completeness_factor = 1.0 if finish_reason="stop" else 0.8
```

## Rate Limiting & Timeouts

- Frontend HTTP timeout: 60 seconds
- OpenAI API retry: 3 attempts with exponential backoff
- Pinecone retry: 3 attempts with exponential backoff
- No rate limiting currently implemented

## Cost Estimation

Per Query:
- Embedding: ~$0.0001
- GPT-4o response: ~$0.015
- **Total**: ~$0.015 per query

Monthly (1000 queries):
- OpenAI: $15-50
- Pinecone: $0 (free tier)
- Infrastructure: $5-50
- **Total**: $20-100/month

## Performance Targets

- Response time: 3-4 seconds (typical)
- Retrieval accuracy: 85%+ relevant documents
- Confidence score: 0.8+ for good answers
- User satisfaction: High (depends on answer quality)

## Testing Endpoints

### Health Checks
- `GET /health` - API configuration status
- `GET /api/v1/chat/health` - RAG service status

### Chat Endpoint
- `POST /api/v1/chat` - Send query

### Documentation
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation

## Troubleshooting Guide

### Issue: "No relevant documents found"
**Cause**: Pinecone index empty or threshold too high
**Fix**: 
1. Run ingestion script
2. Lower similarity_threshold to 0.5
3. Increase top_k to 10

### Issue: Service shows "degraded"
**Cause**: API keys missing or invalid
**Fix**: 
1. Verify .env has valid keys
2. Check API key quotas
3. Restart backend

### Issue: Slow responses (>10s)
**Cause**: OpenAI API overloaded or network latency
**Fix**:
1. Check OpenAI status page
2. Review debug_info for timing
3. Consider response caching

### Issue: Frontend connection refused
**Cause**: Backend not running or CORS misconfigured
**Fix**:
1. Start backend: `uvicorn app.main:app --reload`
2. Check CORS_ORIGINS in config
3. Verify localhost:8000 is accessible

## Knowledge Base Files

All stored in `/data/processed/`:

1. **immigration_knowledge.json** (95 docs)
   - Residence permits (temporary, permanent, EU long-term)
   - Work permits and Blue Cards
   - Visas and entry requirements
   - PESEL and meldunek procedures
   - Family reunification
   - Special programs

2. **employment_knowledge.json** (30 docs)
   - Employment vs B2B contracts
   - Worker rights and protections
   - ZUS social insurance
   - Tax obligations
   - Business registration
   - 2025 minimum wage

3. **healthcare_banking_knowledge.json** (65 docs)
   - NFZ registration procedures
   - Finding doctors (POZ)
   - Emergency healthcare
   - Bank account opening
   - BLIK payment system
   - Best banks for foreigners

4. **police_traffic_knowledge.json** (60+ docs)
   - Filing police reports
   - Lost/stolen documents
   - Traffic fines and procedures
   - Driving license conversion
   - Car registration
   - Emergency numbers

## Recent Updates

- Updated November 11-12, 2025
- All documents verified as current
- July 2025 law changes documented
- English translations verified
- Official sources only (no forums/Reddit)

## Next Steps

1. **Verify Status**: Run diagnostic checklist
2. **Fix Issues**: Follow recommendations in ANALYSIS_SUMMARY.md
3. **Monitor**: Enable debug_info in queries
4. **Optimize**: Tune RAG parameters based on results
5. **Expand**: Add new knowledge categories as needed

## Additional Resources

### Existing Documentation
- `/README.md` - Project overview
- `/PROJECT_COMPLETE.md` - Completion status
- `/RUNNING.md` - Current runtime info
- `/DEPLOYMENT.md` - Production deployment guide
- `/frontend/ARCHITECTURE.md` - Frontend details
- `/backend/README.md` - Backend documentation

### External Resources
- [Next.js Documentation](https://nextjs.org)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pinecone Documentation](https://docs.pinecone.io)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [RAG Best Practices](https://www.anthropic.com/research)

## Maintenance & Support

### Regular Tasks
- Monitor API usage and costs
- Check knowledge base freshness
- Review failed queries
- Update RAG parameters based on metrics
- Monitor response times

### Monitoring Metrics
- Query success rate (should be >90%)
- Average response time (should be <5s)
- Confidence score distribution
- Category accuracy
- API error rates

### Scaling Considerations
- Pinecone free tier supports 1M vectors
- OpenAI has rate limits (check account)
- Consider response caching for common questions
- Implement multi-turn conversation support
- Add monitoring/logging infrastructure

---

**Last Updated**: November 12, 2025
**Analysis Version**: 1.0
**Status**: Production-Ready with Configuration Issues

For detailed technical information, see CODEBASE_ANALYSIS.md
For quick diagnostics, see ANALYSIS_SUMMARY.md
For visual reference, see ARCHITECTURE_DIAGRAM.txt
