#!/bin/bash

# Shogi Bot AI Startup Script
# This script starts both the backend server and opens the frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to cleanup background processes
cleanup() {
    print_status "Cleaning up background processes..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend server stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

print_status "Starting Shogi Bot AI..."
echo "=================================="

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the project root directory"
    print_error "Expected structure: ./backend/ and ./frontend/"
    exit 1
fi

# Check Python installation
if ! command_exists python3; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

print_success "Python 3 found: $(python3 --version)"

# Check if backend dependencies are installed
print_status "Checking backend dependencies..."
cd backend
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found in backend directory"
    exit 1
fi

# Try to import required modules
python3 -c "import flask, flask_cors" 2>/dev/null || {
    print_warning "Installing backend dependencies..."
    pip3 install -r requirements.txt
}

cd ..

# Check if backend port (5000) is available
if ! check_port 5000; then
    print_error "Port 5000 is already in use. Please stop the service using port 5000 or change the backend port."
    exit 1
fi

# Start backend server
print_status "Starting backend server on port 5000..."
cd backend
python3 -m backend.run &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend server failed to start"
    exit 1
fi

# Test backend health
print_status "Testing backend connection..."
for i in {1..10}; do
    if curl -s http://localhost:5000/api/health >/dev/null 2>&1; then
        print_success "Backend server is running and healthy"
        break
    fi
    if [ $i -eq 10 ]; then
        print_error "Backend server is not responding after 10 attempts"
        cleanup
        exit 1
    fi
    sleep 1
done

# Start frontend server
print_status "Starting frontend server..."

# Check if we can use Python's built-in server
if check_port 8080; then
    cd frontend
    print_status "Starting frontend on http://localhost:8080"
    python3 -m http.server 8080 >/dev/null 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    sleep 2
    
    FRONTEND_URL="http://localhost:8080"
else
    print_warning "Port 8080 is in use, serving frontend as file://"
    FRONTEND_URL="file://$(pwd)/frontend/index.html"
fi

print_success "Shogi Bot AI is now running!"
echo "=================================="
print_status "Backend API: http://localhost:5000"
print_status "Frontend: $FRONTEND_URL"
echo "=================================="

# Try to open frontend in browser
if command_exists xdg-open; then
    print_status "Opening frontend in default browser..."
    xdg-open "$FRONTEND_URL" >/dev/null 2>&1 &
elif command_exists open; then
    print_status "Opening frontend in default browser..."
    open "$FRONTEND_URL" >/dev/null 2>&1 &
elif command_exists start; then
    print_status "Opening frontend in default browser..."
    start "$FRONTEND_URL" >/dev/null 2>&1 &
else
    print_warning "Could not auto-open browser. Please manually open: $FRONTEND_URL"
fi

print_status "Press Ctrl+C to stop both servers"

# Keep script running and wait for interrupt
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Backend server has stopped unexpectedly"
        cleanup
        exit 1
    fi
    
    # Check if frontend is still running (if we started it)
    if [ ! -z "$FRONTEND_PID" ] && ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_warning "Frontend server has stopped"
        FRONTEND_PID=""
    fi
    
    sleep 5
done

