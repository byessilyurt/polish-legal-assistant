# Polish Legal Assistant for Foreigners

An AI-powered chatbot with RAG (Retrieval Augmented Generation) to help foreigners navigate legal and daily life issues in Poland.

## 🎯 Project Overview

This application provides accurate, up-to-date information about Polish legal procedures, employment, immigration, healthcare, and daily life matters specifically for foreigners living in or moving to Poland.

### Key Features

- **Extensive Legal Knowledge Base**: Comprehensive information from official Polish government sources
- **July 2025 Law Updates**: Includes latest changes to foreigner regulations
- **RAG-Powered Responses**: Accurate answers with source citations
- **Multi-Category Support**: Immigration, Employment, Healthcare, Banking, Traffic, and more
- **English Interface**: All content translated and presented in English

## 🏗️ Architecture

- **Frontend**: Next.js 14+ with TypeScript and Tailwind CSS
- **Backend**: Python FastAPI with LangChain
- **Vector Database**: Pinecone
- **LLM**: OpenAI GPT-4o
- **Embeddings**: OpenAI text-embedding-3-large

## 📁 Project Structure

```
polish-legal-assistant/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── knowledge-pipeline/ # Data collection & processing
├── scripts/           # Utility scripts
├── data/             # Knowledge base documents
└── docs/             # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- OpenAI API key
- Pinecone account

### Environment Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your API keys
3. Install dependencies:

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Running the Application

```bash
# Start backend (from backend/)
uvicorn app.main:app --reload --port 8000

# Start frontend (from frontend/)
npm run dev
```

Visit `http://localhost:3000` to use the chatbot.

## 📚 Knowledge Base

The knowledge base is built from official Polish government sources including:

- **Immigration**: udsc.gov.pl, mswia.gov.pl
- **Employment**: pip.gov.pl, zus.pl, biznes.gov.pl
- **Healthcare**: nfz.gov.pl
- **Banking**: knf.gov.pl
- **Traffic & Police**: policja.pl, gitd.gov.pl

### Updating Knowledge Base

```bash
cd knowledge-pipeline
python orchestrator.py --category all --refresh
```

## 🔧 Configuration

See `.env.example` for all configuration options.

Key settings:
- `EMBEDDING_DIMENSION`: Vector size (1536 recommended)
- `CHUNK_SIZE`: Document chunk size (800 tokens)
- `TOP_K_RETRIEVAL`: Number of documents to retrieve (20)

## ⚠️ Important Notes

- This tool provides informational guidance only, not legal advice
- Always verify critical information with official sources
- Information is current as of the last knowledge base update
- For complex legal matters, consult with qualified professionals

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## 📞 Support

For issues and questions, please open a GitHub issue.
