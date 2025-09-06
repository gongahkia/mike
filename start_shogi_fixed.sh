#!/bin/bash

# Shogi Bot AI Startup Script - Fixed Version
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
if [ ! -f "backend/requirements.txt" ]; then
    print_error "requirements.txt not found in backend directory"
    exit 1
fi

# Install dependencies if needed
python3 -c "import flask, flask_cors" 2>/dev/null || {
    print_warning "Installing backend dependencies..."
    pip3 install -r backend/requirements.txt
}

# Check if backend port (5000) is available
if ! check_port 5000; then
    print_error "Port 5000 is already in use. Please stop the service using port 5000 or change the backend port."
    exit 1
fi

# Fix the import issue by updating app.py temporarily
print_status "Preparing backend for execution..."

# Create a temporary app.py with fixed imports
cat > backend/app_temp.py << 'EOF'
"""
Flask API server for Shogi Bot AI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from game.game import ShogiGame
from game.pieces import Player, PieceType
from ai.engine import ShogiAI

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store active games
games = {}
ai_engines = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'message': 'Shogi Bot AI is running'})

@app.route('/api/game/new', methods=['POST'])
def new_game():
    """Create a new game."""
    data = request.get_json() or {}
    difficulty = data.get('difficulty', 'medium')
    
    # Validate difficulty
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty level'}), 400
    
    game_id = str(uuid.uuid4())
    game = ShogiGame()
    game.new_game(game_id)
    
    # Create AI engine for this game
    ai_engine = ShogiAI(difficulty=difficulty)
    
    games[game_id] = game
    ai_engines[game_id] = ai_engine
    
    return jsonify({
        'game_id': game_id,
        'difficulty': difficulty,
        'game_state': game.get_game_state()
    })

@app.route('/api/game/<game_id>/state', methods=['GET'])
def get_game_state(game_id):
    """Get current game state."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    return jsonify(game.get_game_state())

@app.route('/api/game/<game_id>/move', methods=['POST'])
def make_move(game_id):
    """Make a move in the game."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No move data provided'}), 400
    
    # Handle regular moves
    if 'from' in data and 'to' in data:
        from_pos = data['from']
        to_pos = data['to']
        promote = data.get('promote', False)
        
        if (not isinstance(from_pos, list) or len(from_pos) != 2 or
            not isinstance(to_pos, list) or len(to_pos) != 2):
            return jsonify({'error': 'Invalid move format'}), 400
        
        result = game.make_move(from_pos[0], from_pos[1], to_pos[0], to_pos[1], promote)
        
        if not result['success']:
            return jsonify(result), 400
        
        response = {
            'success': True,
            'game_state': game.get_game_state(),
            'game_over': result.get('game_over', False)
        }
        
        if result.get('game_over'):
            response['winner'] = result.get('winner')
            response['reason'] = result.get('reason')
        
        return jsonify(response)
    
    # Handle piece drops
    elif 'drop' in data and 'to' in data:
        piece_type = data['drop']
        to_pos = data['to']
        
        if not isinstance(to_pos, list) or len(to_pos) != 2:
            return jsonify({'error': 'Invalid drop format'}), 400
        
        result = game.drop_piece(piece_type, to_pos[0], to_pos[1])
        
        if not result['success']:
            return jsonify(result), 400
        
        response = {
            'success': True,
            'game_state': game.get_game_state(),
            'game_over': result.get('game_over', False)
        }
        
        if result.get('game_over'):
            response['winner'] = result.get('winner')
            response['reason'] = result.get('reason')
        
        return jsonify(response)
    
    else:
        return jsonify({'error': 'Invalid move format'}), 400

@app.route('/api/game/<game_id>/legal-moves', methods=['POST'])
def get_legal_moves(game_id):
    """Get legal moves for a piece."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    data = request.get_json()
    
    if not data or 'position' not in data:
        return jsonify({'error': 'Position not provided'}), 400
    
    position = data['position']
    if not isinstance(position, list) or len(position) != 2:
        return jsonify({'error': 'Invalid position format'}), 400
    
    legal_moves = game.get_legal_moves(position[0], position[1])
    
    return jsonify({
        'legal_moves': legal_moves,
        'can_promote': False  # Will be calculated based on specific move
    })

@app.route('/api/game/<game_id>/drop-positions', methods=['POST'])
def get_drop_positions(game_id):
    """Get valid drop positions for a piece type."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    data = request.get_json()
    
    if not data or 'piece_type' not in data:
        return jsonify({'error': 'Piece type not provided'}), 400
    
    piece_type = data['piece_type']
    drop_positions = game.get_drop_positions(piece_type)
    
    return jsonify({
        'drop_positions': drop_positions
    })

@app.route('/api/game/<game_id>/ai-move', methods=['POST'])
def get_ai_move(game_id):
    """Get AI move for the current player."""
    if game_id not in games or game_id not in ai_engines:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    ai_engine = ai_engines[game_id]
    
    if game.game_over:
        return jsonify({'error': 'Game is already over'}), 400
    
    current_player = game.board.current_player
    
    # Get AI move
    ai_move = ai_engine.get_move(game.board, current_player)
    
    if not ai_move:
        return jsonify({'error': 'No valid AI move found'}), 500
    
    # Make the AI move
    if ai_move['type'] == 'move':
        from_pos = ai_move['from']
        to_pos = ai_move['to']
        promote = ai_move.get('promote', False)
        result = game.make_move(from_pos[0], from_pos[1], to_pos[0], to_pos[1], promote)
    elif ai_move['type'] == 'drop':
        piece_type = ai_move['piece_type'].value
        to_pos = ai_move['to']
        result = game.drop_piece(piece_type, to_pos[0], to_pos[1])
    else:
        return jsonify({'error': 'Invalid AI move type'}), 500
    
    if not result['success']:
        return jsonify({'error': 'AI move failed: ' + result.get('error', 'Unknown error')}), 500
    
    response = {
        'success': True,
        'ai_move': ai_move,
        'game_state': game.get_game_state(),
        'game_over': result.get('game_over', False)
    }
    
    if result.get('game_over'):
        response['winner'] = result.get('winner')
        response['reason'] = result.get('reason')
    
    return jsonify(response)

@app.route('/api/game/<game_id>/analysis', methods=['GET'])
def get_position_analysis(game_id):
    """Get AI analysis of the current position."""
    if game_id not in games or game_id not in ai_engines:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    ai_engine = ai_engines[game_id]
    
    current_player = game.board.current_player
    analysis = ai_engine.get_analysis(game.board, current_player)
    
    return jsonify(analysis)

@app.route('/api/game/<game_id>/suggest', methods=['GET'])
def suggest_move(game_id):
    """Get move suggestion from AI."""
    if game_id not in games or game_id not in ai_engines:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    ai_engine = ai_engines[game_id]
    
    if game.game_over:
        return jsonify({'error': 'Game is already over'}), 400
    
    current_player = game.board.current_player
    suggestion = ai_engine.suggest_move(game.board, current_player)
    
    return jsonify(suggestion)

@app.route('/api/game/<game_id>/difficulty', methods=['POST'])
def set_difficulty(game_id):
    """Change AI difficulty for a game."""
    if game_id not in games or game_id not in ai_engines:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.get_json()
    if not data or 'difficulty' not in data:
        return jsonify({'error': 'Difficulty not provided'}), 400
    
    difficulty = data['difficulty']
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty level'}), 400
    
    ai_engine = ai_engines[game_id]
    ai_engine.set_difficulty(difficulty)
    
    return jsonify({
        'success': True,
        'difficulty': difficulty
    })

@app.route('/api/game/<game_id>/history', methods=['GET'])
def get_move_history(game_id):
    """Get move history for a game."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    history = game.get_move_history()
    
    return jsonify({
        'move_history': history,
        'move_count': len(history)
    })

@app.route('/api/games', methods=['GET'])
def list_games():
    """List all active games."""
    game_list = []
    for game_id, game in games.items():
        ai_engine = ai_engines.get(game_id)
        game_list.append({
            'game_id': game_id,
            'current_player': game.board.current_player.value,
            'game_over': game.game_over,
            'winner': game.winner.value if game.winner else None,
            'difficulty': ai_engine.get_difficulty() if ai_engine else 'unknown',
            'move_count': len(game.board.move_history)
        })
    
    return jsonify({
        'games': game_list,
        'total_games': len(game_list)
    })

@app.route('/api/game/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    """Delete a game."""
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    del games[game_id]
    if game_id in ai_engines:
        del ai_engines[game_id]
    
    return jsonify({'success': True, 'message': 'Game deleted'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF

# Also need to fix the imports in all the other files
print_status "Fixing import statements..."

# Fix game files
sed -i 's/from backend\.game\./from /g' backend/game/*.py
sed -i 's/from backend\.ai\./from ai./g' backend/game/*.py

# Fix AI files  
sed -i 's/from backend\.game\./from game./g' backend/ai/*.py
sed -i 's/from backend\.ai\./from /g' backend/ai/*.py

# Start backend server
print_status "Starting backend server on port 5000..."
cd backend
python3 app_temp.py &
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

