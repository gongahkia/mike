"""
Minimax algorithm with alpha-beta pruning for Shogi AI.
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from game.board import ShogiBoard
from game.pieces import Player, PieceType
from evaluation import PositionEvaluator


class MinimaxAI:
    def __init__(self, max_depth: int = 3, time_limit: float = 5.0):
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.evaluator = PositionEvaluator()
        self.nodes_searched = 0
        self.start_time = 0
        self.transposition_table = {}
    
    def get_best_move(self, board: ShogiBoard, player: Player) -> Optional[Dict]:
        """Get the best move for the given player."""
        self.nodes_searched = 0
        self.start_time = time.time()
        self.transposition_table.clear()
        
        legal_moves = board.get_all_legal_moves(player)
        if not legal_moves:
            return None
        
        best_move = None
        best_score = float('-inf')
        
        # Try iterative deepening for better time management
        for depth in range(1, self.max_depth + 1):
            if time.time() - self.start_time > self.time_limit * 0.8:
                break
            
            current_best = None
            current_best_score = float('-inf')
            
            for move in legal_moves:
                if time.time() - self.start_time > self.time_limit:
                    break
                
                # Make the move
                board_copy = self._copy_board(board)
                self._make_move_on_board(board_copy, move)
                
                # Evaluate the position
                score = self._minimax(board_copy, depth - 1, float('-inf'), float('inf'), 
                                    False, player)
                
                if score > current_best_score:
                    current_best_score = score
                    current_best = move
            
            if current_best:
                best_move = current_best
                best_score = current_best_score
        
        return best_move
    
    def _minimax(self, board: ShogiBoard, depth: int, alpha: float, beta: float, 
                maximizing: bool, original_player: Player) -> float:
        """Minimax algorithm with alpha-beta pruning."""
        self.nodes_searched += 1
        
        # Check time limit
        if time.time() - self.start_time > self.time_limit:
            return self.evaluator.evaluate_position_full(board, original_player)
        
        # Base case: depth 0 or game over
        if depth == 0:
            return self.evaluator.evaluate_position_full(board, original_player)
        
        current_player = board.current_player
        
        # Check for checkmate
        if board.is_checkmate(current_player):
            if current_player == original_player:
                return -10000 - depth  # Prefer faster checkmates when losing
            else:
                return 10000 + depth   # Prefer faster checkmates when winning
        
        legal_moves = board.get_all_legal_moves(current_player)
        if not legal_moves:
            return self.evaluator.evaluate_position_full(board, original_player)
        
        if maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                if time.time() - self.start_time > self.time_limit:
                    break
                
                board_copy = self._copy_board(board)
                self._make_move_on_board(board_copy, move)
                
                eval_score = self._minimax(board_copy, depth - 1, alpha, beta, False, original_player)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                if time.time() - self.start_time > self.time_limit:
                    break
                
                board_copy = self._copy_board(board)
                self._make_move_on_board(board_copy, move)
                
                eval_score = self._minimax(board_copy, depth - 1, alpha, beta, True, original_player)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            return min_eval
    
    def _copy_board(self, board: ShogiBoard) -> ShogiBoard:
        """Create a deep copy of the board."""
        new_board = ShogiBoard()
        
        # Copy board state
        for row in range(9):
            for col in range(9):
                piece = board.get_piece(row, col)
                if piece:
                    from game.pieces import Piece
                    new_piece = Piece(piece.piece_type, piece.player, piece.promoted)
                    new_board.set_piece(row, col, new_piece)
                else:
                    new_board.set_piece(row, col, None)
        
        # Copy captured pieces
        for player in [Player.SENTE, Player.GOTE]:
            new_board.captured_pieces[player] = []
            for piece in board.captured_pieces[player]:
                from game.pieces import Piece
                new_piece = Piece(piece.piece_type, piece.player, piece.promoted)
                new_board.captured_pieces[player].append(new_piece)
        
        # Copy other state
        new_board.current_player = board.current_player
        new_board.move_history = board.move_history.copy()
        
        return new_board
    
    def _make_move_on_board(self, board: ShogiBoard, move: Dict):
        """Make a move on the board."""
        if move['type'] == 'move':
            from_row, from_col = move['from']
            to_row, to_col = move['to']
            promote = move.get('promote', False)
            board.make_move(from_row, from_col, to_row, to_col, promote)
        elif move['type'] == 'drop':
            piece_type = move['piece_type']
            to_row, to_col = move['to']
            board.drop_piece(piece_type, to_row, to_col)


class DifficultyAI:
    """AI with different difficulty levels."""
    
    def __init__(self, difficulty: str = 'medium'):
        self.difficulty = difficulty.lower()
        
        # Configure AI based on difficulty
        if self.difficulty == 'easy':
            self.ai = MinimaxAI(max_depth=2, time_limit=1.0)
        elif self.difficulty == 'medium':
            self.ai = MinimaxAI(max_depth=3, time_limit=3.0)
        elif self.difficulty == 'hard':
            self.ai = MinimaxAI(max_depth=4, time_limit=5.0)
        else:
            self.ai = MinimaxAI(max_depth=3, time_limit=3.0)
    
    def get_move(self, board: ShogiBoard, player: Player) -> Optional[Dict]:
        """Get AI move based on difficulty level."""
        if self.difficulty == 'easy':
            # Easy: Sometimes make random moves
            import random
            legal_moves = board.get_all_legal_moves(player)
            if legal_moves and random.random() < 0.3:  # 30% chance of random move
                return random.choice(legal_moves)
        
        # Use minimax for all difficulties
        return self.ai.get_best_move(board, player)
    
    def set_difficulty(self, difficulty: str):
        """Change the difficulty level."""
        self.__init__(difficulty)

