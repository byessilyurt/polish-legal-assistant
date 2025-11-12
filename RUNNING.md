# Polish Legal Assistant - Currently Running!

## 🎉 Your Application is Live!

Both the backend and frontend servers are currently running.

---

## 🌐 Access the Application

### Main Application
**URL:** http://localhost:3000

Open this URL in your browser to use the Polish Legal Assistant chatbot.

### Backend API
**URL:** http://localhost:8000

### API Documentation
**Swagger UI:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

---

## 📊 Current Status

✅ **Backend Server:** Running on port 8000
✅ **Frontend Server:** Running on port 3000
✅ **Pinecone Database:** Initialized with 91 vectors
✅ **Knowledge Base:** Immigration (58 docs) + Employment (30 docs)

---

## 🧪 Test the Application

1. Open http://localhost:3000 in your browser
2. You'll see the Polish Legal Assistant welcome screen
3. Try asking questions like:
   - "How do I apply for a residence permit in Poland?"
   - "What's the difference between B2B and employment contract?"
   - "How do I get a PESEL number?"
   - "Can I work while my residence permit application is pending?"

---

## 🔧 Managing the Servers

### Stop Servers
To stop the servers, press **Ctrl+C** in the terminal windows where they're running.

Or use:
```bash
# Find and kill backend
lsof -ti:8000 | xargs kill -9

# Find and kill frontend
lsof -ti:3000 | xargs kill -9
```

### Restart Servers

**Backend:**
```bash
cd /Users/yusufyesilyurt/Desktop/Folders/projects/polish-legal-assistant/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd /Users/yusufyesilyurt/Desktop/Folders/projects/polish-legal-assistant/frontend
npm run dev
```

**Or use the startup script:**
```bash
cd /Users/yusufyesilyurt/Desktop/Folders/projects/polish-legal-assistant
./start.sh
```

---

## 📝 Environment Configuration

Your API keys are configured in:
- `/Users/yusufyesilyurt/Desktop/Folders/projects/polish-legal-assistant/.env`
- `/Users/yusufyesilyurt/Desktop/Folders/projects/polish-legal-assistant/backend/.env`
- `/Users/yusufyesilyurt/Desktop/Folders/projects/polish-legal-assistant/frontend/.env.local`

---

## 🔍 Troubleshooting

### Backend Issues
- Check logs in the terminal where backend is running
- Verify API keys are set in `.env` files
- Check Pinecone index exists: http://localhost:8000/api/v1/chat/health

### Frontend Issues
- Check console for errors (F12 in browser)
- Verify backend is running and accessible
- Check CORS settings in backend/.env

### RAG/Chat Issues
- Verify vectors are in Pinecone (should show 91 vectors)
- Check OpenAI API key is valid and has credits
- Try test query at http://localhost:8000/docs

---

## 📚 Next Steps

1. **Test the chatbot** at http://localhost:3000
2. **Explore API docs** at http://localhost:8000/docs
3. **Add more knowledge** by running ingestion script again
4. **Deploy to production** using DEPLOYMENT.md guide

---

## 💰 API Usage

Remember you're using:
- **OpenAI API** for GPT-4o responses and embeddings
- **Pinecone** for vector storage (free tier: 1M vectors)

Monitor your usage in respective dashboards.

---

**Enjoy your Polish Legal Assistant! 🇵🇱**

Last updated: November 11, 2025
