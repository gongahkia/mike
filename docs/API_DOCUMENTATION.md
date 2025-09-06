# Shogi Bot AI - API Documentation

## Overview

The Shogi Bot AI backend provides a RESTful API for managing shogi games and interacting with the AI engine. All endpoints return JSON responses and support CORS for cross-origin requests.

## Base URL

```
http://localhost:5000/api
```

## Endpoints

### Health Check

#### GET /health
Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Shogi Bot AI is running"
}
```

### Game Management

#### POST /game/new
Create a new game session.

**Request Body:**
```json
{
  "difficulty": "medium"  // Optional: "easy", "medium", "hard"
}
```

**Response:**
```json
{
  "game_id": "uuid-string",
  "difficulty": "medium",
  "game_state": {
    "board": [...],
    "captured": {...},
    "current_player": "sente",
    "in_check": {...},
    "checkmate": {...},
    "game_over": false,
    "winner": null,
    "game_id": "uuid-string"
  }
}
```

#### GET /game/{game_id}/state
Get the current state of a game.

**Response:**
```json
{
  "board": [
    [null, {"type": "piece_type", "player": "sente", "promoted": false}, ...],
    ...
  ],
  "captured": {
    "sente": [...],
    "gote": [...]
  },
  "current_player": "sente",
  "in_check": {
    "sente": false,
    "gote": false
  },
  "checkmate": {
    "sente": false,
    "gote": false
  },
  "game_over": false,
  "winner": null,
  "game_id": "uuid-string"
}
```

#### DELETE /game/{game_id}
Delete a game session.

**Response:**
```json
{
  "success": true,
  "message": "Game deleted"
}
```

### Move Operations

#### POST /game/{game_id}/move
Make a move in the game.

**Request Body (Regular Move):**
```json
{
  "from": [row, col],
  "to": [row, col],
  "promote": false  // Optional
}
```

**Request Body (Piece Drop):**
```json
{
  "drop": "piece_type",
  "to": [row, col]
}
```

**Response:**
```json
{
  "success": true,
  "game_state": {...},
  "game_over": false,
  "winner": null,     // Only if game_over is true
  "reason": null      // Only if game_over is true
}
```

#### POST /game/{game_id}/legal-moves
Get legal moves for a piece at a specific position.

**Request Body:**
```json
{
  "position": [row, col]
}
```

**Response:**
```json
{
  "legal_moves": [[row, col], ...],
  "can_promote": false
}
```

#### POST /game/{game_id}/drop-positions
Get valid drop positions for a piece type.

**Request Body:**
```json
{
  "piece_type": "pawn"
}
```

**Response:**
```json
{
  "drop_positions": [[row, col], ...]
}
```

### AI Operations

#### POST /game/{game_id}/ai-move
Get and execute an AI move for the current player.

**Response:**
```json
{
  "success": true,
  "ai_move": {
    "type": "move",
    "from": [row, col],
    "to": [row, col],
    "promote": false,
    "piece": {...}
  },
  "game_state": {...},
  "game_over": false,
  "winner": null,
  "reason": null
}
```

#### GET /game/{game_id}/suggest
Get a move suggestion from the AI without executing it.

**Response:**
```json
{
  "move": {
    "type": "move",
    "from": [row, col],
    "to": [row, col],
    "promote": false,
    "piece": {...}
  },
  "analysis": {...},
  "difficulty": "medium",
  "using_opening_book": true
}
```

#### GET /game/{game_id}/analysis
Get AI analysis of the current position.

**Response:**
```json
{
  "material_balance": 150,
  "position_score": 25,
  "king_safety": 30,
  "mobility": 10,
  "threats": 0,
  "total_evaluation": 215,
  "in_check": false,
  "checkmate": false,
  "legal_moves_count": 42
}
```

#### POST /game/{game_id}/difficulty
Change the AI difficulty level for a game.

**Request Body:**
```json
{
  "difficulty": "hard"
}
```

**Response:**
```json
{
  "success": true,
  "difficulty": "hard"
}
```

### Game History

#### GET /game/{game_id}/history
Get the move history for a game.

**Response:**
```json
{
  "move_history": [
    {
      "from": [6, 6],
      "to": [5, 6],
      "piece": {...},
      "captured": null,
      "promoted": false,
      "player": "sente"
    },
    ...
  ],
  "move_count": 10
}
```

#### GET /games
List all active games.

**Response:**
```json
{
  "games": [
    {
      "game_id": "uuid-string",
      "current_player": "sente",
      "game_over": false,
      "winner": null,
      "difficulty": "medium",
      "move_count": 5
    },
    ...
  ],
  "total_games": 3
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Game or endpoint not found
- `500 Internal Server Error`: Server error

## Piece Types

Valid piece types for the API:
- `king`
- `rook`
- `bishop`
- `gold`
- `silver`
- `knight`
- `lance`
- `pawn`
- `promoted_rook`
- `promoted_bishop`
- `promoted_silver`
- `promoted_knight`
- `promoted_lance`
- `promoted_pawn`

## Players

- `sente`: First player (bottom of board)
- `gote`: Second player (top of board)

## Board Coordinates

The board uses a 9x9 coordinate system:
- Rows: 0-8 (top to bottom)
- Columns: 0-8 (left to right)
- Position [0,0] is the top-left corner
- Position [8,8] is the bottom-right corner

