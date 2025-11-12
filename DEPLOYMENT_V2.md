# Polish Legal Assistant - V2 Deployment Guide

## 🎯 Overview

This deployment includes comprehensive improvements to dramatically increase the response rate of the Polish Legal Assistant from ~35% to an expected ~90-95%.

### Key Improvements Implemented

1. **Knowledge Base Expansion**: 88 → 248 documents (+182%)
2. **Improved Chunking**: 800 tokens → 600 tokens for better precision
3. **RAG Parameters Optimization**: threshold 0.7→0.55, top_k 5→10
4. **Two-Tier Fallback Retrieval**: Strict + Relaxed tiers for maximum coverage
5. **Query Preprocessing**: Polish abbreviation expansion
6. **Metrics Collection**: Real-time performance monitoring

---

## 📊 What Changed

### Knowledge Base
- **Before**: 88 docs (Immigration: 58, Employment: 30, Healthcare/Banking: 0, Police/Traffic: 0)
- **After**: 248 docs (Immigration: 58, Employment: 30, Healthcare/Banking: 85, Police/Traffic: 75)
- **Impact**: 3x more topics covered, filling critical gaps in healthcare, banking, and traffic information

### Vector Database
- **Old Index**: `polish-legal-kb` (~91 vectors)
- **New Index**: `polish-legal-kb-v2` (251 vectors)
- **Chunking**: Improved from 800 to 600 tokens for better precision

### RAG Configuration
```env
# OLD VALUES
rag_top_k = 5
rag_similarity_threshold = 0.7

# NEW VALUES
rag_top_k = 10
rag_similarity_threshold = 0.55

# NEW TWO-TIER FALLBACK
rag_tier1_threshold = 0.65  (strict)
rag_tier1_top_k = 5
rag_tier2_threshold = 0.50  (relaxed fallback)
rag_tier2_top_k = 15
```

### New Features
1. **Two-Tier Retrieval**
   - Tier 1: High-confidence retrieval (threshold 0.65, top_k 5)
   - Tier 2: Fallback for edge cases (threshold 0.50, top_k 15)
   - Automatic fallback if Tier 1 returns <2 results

2. **Query Preprocessing**
   - Expands Polish abbreviations (np. → na przykład, zł → złotych, etc.)
   - Normalizes whitespace
   - Improves embedding quality

3. **Metrics Collection**
   - Response rate tracking
   - Tier distribution analytics
   - Failed query logging
   - Category distribution
   - **Endpoints**: `/api/v1/metrics`, `/api/v1/metrics/reset`

---

## 🚀 Deployment Steps

### Step 1: Verify Environment

```bash
# Ensure you're in the project root
cd /path/to/polish-legal-assistant

# Check that new index exists
python3 << 'EOF'
from pinecone import Pinecone
import os
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
indices = pc.list_indexes().names()
print("Available indices:", indices)
assert "polish-legal-kb-v2" in indices, "New index not found!"
stats = pc.Index("polish-legal-kb-v2").describe_index_stats()
print(f"Vectors in new index: {stats.total_vector_count}")
EOF
```

**Expected Output**:
```
Available indices: ['polish-legal-kb', 'polish-legal-kb-v2']
Vectors in new index: 251
```

### Step 2: Update Environment Configuration

The `.env` file has been updated to use the new index:

```bash
# Verify the change
cat .env | grep PINECONE_INDEX_NAME
# Should output: PINECONE_INDEX_NAME=polish-legal-kb-v2
```

### Step 3: Install/Update Dependencies

```bash
# Backend dependencies (if not already installed)
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

### Step 4: Start Services

#### Option A: Using Docker (Recommended for Production)

```bash
# From project root
docker-compose down
docker-compose up --build -d

# Check logs
docker-compose logs -f backend
```

#### Option B: Manual Start (Development)

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### Step 5: Health Check

```bash
# Check backend health
curl http://localhost:8000/health

# Check RAG service health
curl http://localhost:8000/api/v1/chat/health

# Expected response:
# {
#   "retrieval_service": true,
#   "llm_service": true,
#   "overall_healthy": true
# }
```

### Step 6: Test with Sample Queries

```bash
# Test query across different categories
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Jak zarejestrować się w NFZ?",
    "include_debug": true
  }'

# Should return successful response with tier_used in debug_info
```

### Step 7: Monitor Metrics

```bash
# Check metrics after a few queries
curl http://localhost:8000/api/v1/metrics

# Expected response:
# {
#   "total_queries": X,
#   "response_rate": 0.9+,
#   "tier_distribution": {...},
#   "similarity_scores": {...}
# }
```

---

## 📈 Expected Performance Improvements

| Metric | Before | After V2 | Target |
|--------|--------|----------|--------|
| Response Rate | ~35% | ~90% | 95% |
| Knowledge Coverage | 88 docs | 248 docs | 250+ |
| Avg Similarity Score | 0.76 | 0.65 | 0.65+ |
| Categories Covered | 2/4 | 4/4 | 4/4 |
| Query Latency (p95) | 2.5s | 3.0s | <3.5s |

### Cost Impact (1000 queries/day)

| Component | Before | After | Increase |
|-----------|--------|-------|----------|
| Embeddings | $3/mo | $6/mo | +$3 |
| LLM Calls | $150/mo | $240/mo | +$90 |
| Pinecone | $70/mo | $70/mo | $0 |
| **Total** | **$223/mo** | **$316/mo** | **+$93/mo** |

**ROI**: 2.5x more queries answered for 1.4x cost = **positive ROI**

---

## 🔍 Testing Checklist

### Functional Tests

- [ ] Immigration queries work (existing functionality)
- [ ] Employment queries work (existing functionality)
- [ ] Healthcare queries work (NEW - test NFZ, insurance, doctors)
- [ ] Banking queries work (NEW - test accounts, PESEL, BLIK)
- [ ] Police queries work (NEW - test meldunek, PESEL registration)
- [ ] Traffic queries work (NEW - test driving license, insurance, fines)

### Sample Test Queries

```bash
# Healthcare (NEW)
"Jak zarejestrować się w NFZ?"
"Ile kosztuje dobrowolne ubezpieczenie NFZ?"
"Gdzie mogę znaleźć lekarza mówiącego po angielsku?"

# Banking (NEW)
"Jak otworzyć konto bankowe bez PESEL?"
"Co to jest BLIK?"
"Jakie dokumenty potrzebne do konta bankowego?"

# Police/Traffic (NEW)
"Co to jest meldunek i jak się zarejestrować?"
"Jak wymienić prawo jazdy w Polsce?"
"Jakie są kary za przekroczenie prędkości?"

# Immigration (EXISTING - verify still works)
"Jak przedłużyć kartę pobytu?"
"Jakie dokumenty do zezwolenia na pracę?"

# Employment (EXISTING - verify still works)
"Jakie są obowiązki pracodawcy wobec cudzoziemców?"
```

### Performance Tests

- [ ] Response time <3s for p95
- [ ] Tier 1 success rate >60%
- [ ] Tier 2 fallback working (check debug_info)
- [ ] Query preprocessing active (check logs)
- [ ] Metrics collection working

---

## 🐛 Troubleshooting

### Issue: "No relevant documents found"

**Diagnosis**:
```bash
# Check if new index is being used
curl http://localhost:8000/api/v1/chat/health

# Check vector count
python3 -c "
from pinecone import Pinecone
import os
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
stats = pc.Index('polish-legal-kb-v2').describe_index_stats()
print(f'Vectors: {stats.total_vector_count}')
"
```

**Fix**:
- Ensure `.env` has `PINECONE_INDEX_NAME=polish-legal-kb-v2`
- Restart backend service
- Verify index has 251 vectors

### Issue: High latency (>5s)

**Diagnosis**:
```bash
# Check if tier parameters are too aggressive
curl http://localhost:8000/api/v1/metrics
# Look for high tier2_rate
```

**Fix**:
- If >40% queries use Tier 2, increase Tier 1 threshold to 0.60
- If latency persists, reduce tier2_top_k from 15 to 10

### Issue: Low accuracy/hallucinations

**Diagnosis**:
```bash
# Check similarity scores in metrics
curl http://localhost:8000/api/v1/metrics
# Look for tier2_avg < 0.50
```

**Fix**:
- Increase tier2_threshold from 0.50 to 0.55
- Review failed queries: `curl http://localhost:8000/api/v1/metrics | jq '.recent_failures'`
- May need to add more specific documents for failing topics

### Issue: Backend won't start

**Common causes**:
1. Missing environment variables
2. Pinecone index doesn't exist
3. Invalid API keys

**Fix**:
```bash
# Verify all env vars
cat .env

# Test API keys
python3 << 'EOF'
import os
from openai import OpenAI
from pinecone import Pinecone

# Test OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
models = client.models.list()
print("✓ OpenAI key valid")

# Test Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
indices = pc.list_indexes()
print(f"✓ Pinecone key valid, indices: {indices.names()}")
EOF
```

---

## 📊 Monitoring Post-Deployment

### Daily Checks (First Week)

```bash
# Morning check
curl http://localhost:8000/api/v1/metrics | jq '{
  total_queries,
  response_rate,
  tier1_rate: .tier_distribution.tier1_rate,
  tier2_rate: .tier_distribution.tier2_rate
}'

# Check failed queries
curl http://localhost:8000/api/v1/metrics | jq '.recent_failures[] | .query'
```

### Weekly Review

1. **Response Rate**: Should be >90%
2. **Tier Distribution**: Tier 1 should handle 60-70%
3. **Failed Queries**: Identify patterns, add missing docs if needed
4. **Category Distribution**: Ensure all 4 categories getting queries

### Monthly Optimization

1. Analyze metrics for query patterns
2. Identify knowledge gaps (failed queries)
3. Add documents for commonly failing topics
4. Fine-tune thresholds if needed

---

## 🔄 Rollback Plan

If issues arise, rollback to the old index:

```bash
# Step 1: Update .env
sed -i '' 's/polish-legal-kb-v2/polish-legal-kb/g' .env

# Step 2: Restart services
docker-compose restart backend
# OR if running manually:
# kill backend process and restart

# Step 3: Verify rollback
curl http://localhost:8000/health

# Step 4: Reset metrics (optional)
curl -X POST http://localhost:8000/api/v1/metrics/reset
```

---

## 📝 Success Criteria

Deployment is successful if after 24 hours:

- ✅ Response rate ≥ 85%
- ✅ System stable (no crashes)
- ✅ Tier 1 handling ≥ 50% of queries
- ✅ Latency p95 < 4 seconds
- ✅ All 4 categories receiving and answering queries
- ✅ No critical errors in logs

---

## 🎓 Next Steps After Deployment

1. **Week 1**: Monitor metrics daily, address any failing query patterns
2. **Week 2**: Fine-tune thresholds based on actual performance
3. **Week 3**: Gather user feedback, identify UX improvements
4. **Month 1**: Delete old index `polish-legal-kb` if V2 stable
5. **Ongoing**: Continue adding documents based on failed query analysis

---

## 📞 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f backend` or backend console
2. Review metrics: `curl http://localhost:8000/api/v1/metrics`
3. Test health: `curl http://localhost:8000/api/v1/chat/health`
4. Consult troubleshooting section above

---

## 📚 Additional Resources

- **Architecture Diagram**: `ARCHITECTURE_DIAGRAM.txt`
- **Codebase Analysis**: `CODEBASE_ANALYSIS.md`
- **Original Documentation**: `PROJECT_COMPLETE.md`
- **Running Guide**: `RUNNING.md`

---

**Deployment Date**: November 12, 2025
**Version**: 2.0.0
**Knowledge Base Size**: 248 documents, 251 vectors
**Expected Response Rate**: 90-95%
