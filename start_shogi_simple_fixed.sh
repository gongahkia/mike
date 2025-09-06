#!/bin/bash

# Simple Shogi Bot AI Startup Script - Fixed Version

echo "🎌 Starting Shogi Bot AI..."

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install -r backend/requirements.txt >/dev/null 2>&1

# Fix imports in backend files
echo "🔧 Fixing import statements..."

# Fix game files
sed -i 's/from backend\.game\./from /g' backend/game/*.py
sed -i 's/from backend\.ai\./from ai./g' backend/game/*.py

# Fix AI files  
sed -i 's/from backend\.game\./from game./g' backend/ai/*.py
sed -i 's/from backend\.ai\./from /g' backend/ai/*.py

# Start backend directly
echo "🚀 Starting backend server..."
cd backend
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🌐 Starting frontend server..."
cd frontend
python3 -m http.server 8080 >/dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 2

echo "✅ Shogi Bot AI is now running!"
echo "🔗 Backend: http://localhost:5000"
echo "🔗 Frontend: http://localhost:8080"
echo "🌐 Open http://localhost:8080 in your browser to play!"
echo ""
echo "Press Ctrl+C to stop both servers"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handler
trap cleanup SIGINT SIGTERM

# Keep script running
while true; do
    sleep 1
done

