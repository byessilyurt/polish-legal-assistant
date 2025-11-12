#!/bin/bash

# Polish Legal Assistant - Startup Script

echo "========================================"
echo "Polish Legal Assistant"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it from .env.example"
    exit 1
fi

echo "Starting backend server..."
cd backend

# Activate virtual environment and start backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "✓ Backend starting at http://localhost:8000"
echo "  PID: $BACKEND_PID"
echo ""

cd ..
cd frontend

echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo "✓ Frontend starting at http://localhost:3000"
echo "  PID: $FRONTEND_PID"
echo ""
echo "========================================"
echo "Polish Legal Assistant is running!"
echo "========================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
