#!/bin/bash

# Shogi Bot AI Startup Script - Final Working Version

echo "🎌 Starting Shogi Bot AI..."

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r backend/requirements.txt >/dev/null 2>&1

# Fix all import statements in backend files
echo "🔧 Fixing import statements..."

# Backup original files first
cp backend/app.py backend/app.py.backup 2>/dev/null || true

# Fix app.py imports
sed -i 's/from backend\.game\.game import ShogiGame/from game.game import ShogiGame/g' backend/app.py
sed -i 's/from backend\.game\.pieces import Player, PieceType/from game.pieces import Player, PieceType/g' backend/app.py
sed -i 's/from backend\.ai\.engine import ShogiAI/from ai.engine import ShogiAI/g' backend/app.py

# Fix game module imports
sed -i 's/from backend\.game\.pieces import/from game.pieces import/g' backend/game/*.py
sed -i 's/from backend\.game\.board import/from game.board import/g' backend/game/*.py
sed -i 's/from \.pieces import/from game.pieces import/g' backend/game/*.py
sed -i 's/from \.board import/from game.board import/g' backend/game/*.py

# Fix AI module imports  
sed -i 's/from backend\.game\.pieces import/from game.pieces import/g' backend/ai/*.py
sed -i 's/from backend\.game\.board import/from game.board import/g' backend/ai/*.py
sed -i 's/from backend\.ai\.evaluation import/from ai.evaluation import/g' backend/ai/*.py
sed -i 's/from backend\.ai\.minimax import/from ai.minimax import/g' backend/ai/*.py
sed -i 's/from backend\.ai\.opening_book import/from ai.opening_book import/g' backend/ai/*.py
sed -i 's/from \.evaluation import/from ai.evaluation import/g' backend/ai/*.py
sed -i 's/from \.minimax import/from ai.minimax import/g' backend/ai/*.py
sed -i 's/from \.opening_book import/from ai.opening_book import/g' backend/ai/*.py

echo "✅ Import statements fixed"

# Start backend
echo "🚀 Starting backend server..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Checking for errors..."
    exit 1
fi

# Test backend health
echo "🔍 Testing backend connection..."
for i in {1..10}; do
    if curl -s http://localhost:5000/api/health >/dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Backend not responding"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Start frontend
echo "🌐 Starting frontend server..."
cd frontend
python3 -m http.server 8080 >/dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 2

echo ""
echo "🎉 Shogi Bot AI is now running successfully!"
echo "=================================="
echo "🔗 Backend API: http://localhost:5000"
echo "🔗 Frontend: http://localhost:8080"
echo "🌐 Open http://localhost:8080 in your browser to play!"
echo "=================================="
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    
    # Restore original files
    if [ -f "backend/app.py.backup" ]; then
        echo "🔄 Restoring original files..."
        mv backend/app.py.backup backend/app.py
    fi
    
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handler
trap cleanup SIGINT SIGTERM

# Keep script running
while true; do
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend stopped unexpectedly"
        cleanup
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend stopped unexpectedly"
        cleanup
    fi
    sleep 5
done