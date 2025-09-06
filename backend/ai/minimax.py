"""
Minimax algorithm implementation for Shogi AI.
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from game.board import ShogiBoard
from game.pieces import Player, PieceType, Piece
from ai.evaluation import PositionEvaluator


class MinimaxAI:
    """Minimax AI with alpha-beta pruning."""
    
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.evaluator = PositionEvaluator()
        self.nodes_evaluated = 0
        self.time_limit = 5.0  # 5 seconds per move
    
    def get_best_move(self, board: ShogiBoard, player: Player) -> Optional[Dict]:
        """Get the best move using minimax with alpha-beta pruning."""
        self.nodes_evaluated = 0
        start_time = time.time()
        
        best_move = None
        best_score = float('-inf')
        
        # Get all legal moves
        legal_moves = board.get_all_legal_moves(player)
        
        if not legal_moves:
            return None
        
        # Sort moves for better alpha-beta pruning
        legal_moves = self._order_moves(board, legal_moves, player)
        
        alpha = float('-inf')
        beta = float('inf')
        
        for move in legal_moves:
            # Check time limit
            if time.time() - start_time > self.time_limit:
                break
            
            # Make the move
            board_copy = self._copy_board(board)
            self._make_move_on_board(board_copy, move)
            
            # Evaluate the position
            opponent = Player.GOTE if player == Player.SENTE else Player.SENTE
            score = self._minimax(board_copy, self.max_depth - 1, alpha, beta, False, opponent, start_time)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)
        
        return best_move
    
    def _minimax(self, board: ShogiBoard, depth: int, alpha: float, beta: float, 
                maximizing: bool, player: Player, start_time: float) -> float:
        """Minimax algorithm with alpha-beta pruning."""
        self.nodes_evaluated += 1
        
        # Check time limit
        if time.time() - start_time > self.time_limit:
            return self.evaluator.evaluate_position(board, player)
        
        # Base case: depth 0 or game over
        if depth == 0 or board.is_checkmate(player) or board.is_checkmate(
            Player.GOTE if player == Player.SENTE else Player.SENTE):
            return self.evaluator.evaluate_position(board, player)
        
        legal_moves = board.get_all_legal_moves(player)
        if not legal_moves:
            return self.evaluator.evaluate_position(board, player)
        
        # Sort moves for better pruning
        legal_moves = self._order_moves(board, legal_moves, player)
        
        if maximizing:
            max_eval = float('-inf')
            for move in legal_moves:
                # Check time limit
                if time.time() - start_time > self.time_limit:
                    break
                
                board_copy = self._copy_board(board)
                self._make_move_on_board(board_copy, move)
                
                opponent = Player.GOTE if player == Player.SENTE else Player.SENTE
                eval_score = self._minimax(board_copy, depth - 1, alpha, beta, False, opponent, start_time)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                # Check time limit
                if time.time() - start_time > self.time_limit:
                    break
                
                board_copy = self._copy_board(board)
                self._make_move_on_board(board_copy, move)
                
                opponent = Player.GOTE if player == Player.SENTE else Player.SENTE
                eval_score = self._minimax(board_copy, depth - 1, alpha, beta, True, opponent, start_time)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            return min_eval
    
    def _order_moves(self, board: ShogiBoard, moves: List[Dict], player: Player) -> List[Dict]:
        """Order moves for better alpha-beta pruning."""
        def move_priority(move):
            priority = 0
            
            if move['type'] == 'move':
                from_pos = move['from']
                to_pos = move['to']
                piece = move['piece']
                
                # Prioritize captures
                target_piece = board.get_piece(to_pos[0], to_pos[1])
                if target_piece:
                    priority += self.evaluator.piece_values.get(target_piece.piece_type, 0)
                
                # Prioritize moves to center
                center_distance = abs(to_pos[0] - 4) + abs(to_pos[1] - 4)
                priority += (8 - center_distance) * 5
                
                # Prioritize piece value (move valuable pieces less)
                priority -= self.evaluator.piece_values.get(piece.piece_type, 0) // 10
            
            elif move['type'] == 'drop':
                # Prioritize dropping more valuable pieces
                priority += self.evaluator.piece_values.get(move['piece_type'], 0) // 2
            
            return priority
        
        return sorted(moves, key=move_priority, reverse=True)
    
    def _copy_board(self, board: ShogiBoard) -> ShogiBoard:
        """Create a deep copy of the board."""
        new_board = ShogiBoard()
        
        # Copy board state
        for row in range(9):
            for col in range(9):
                piece = board.get_piece(row, col)
                if piece:
                    new_piece = Piece(piece.piece_type, piece.player, piece.promoted)
                    new_board.set_piece(row, col, new_piece)
                else:
                    new_board.set_piece(row, col, None)
        
        # Copy captured pieces
        for player in [Player.SENTE, Player.GOTE]:
            new_board.captured[player] = []
            for piece in board.captured[player]:
                new_piece = Piece(piece.piece_type, piece.player, piece.promoted)
                new_board.captured[player].append(new_piece)
        
        # Copy other state
        new_board.current_player = board.current_player
        new_board.move_history = board.move_history.copy()
        
        return new_board
    
    def _make_move_on_board(self, board: ShogiBoard, move: Dict):
        """Make a move on the board."""
        if move['type'] == 'move':
            from_pos = move['from']
            to_pos = move['to']
            piece = move['piece']
            
            # Check if piece can promote
            promote = False
            if hasattr(piece, 'can_promote') and piece.can_promote(from_pos[0], to_pos[0]):
                # Simple promotion logic: promote if beneficial
                if piece.piece_type in [PieceType.PAWN, PieceType.LANCE, PieceType.KNIGHT, PieceType.SILVER]:
                    promote = True
            
            board.move_piece(from_pos[0], from_pos[1], to_pos[0], to_pos[1], promote)
        
        elif move['type'] == 'drop':
            piece_type = move['piece_type']
            to_pos = move['to']
            board.drop_piece(piece_type.value, to_pos[0], to_pos[1])


class DifficultyAI:
    """AI with adjustable difficulty levels."""
    
    def __init__(self, difficulty: str = 'medium'):
        self.difficulty = difficulty
        self.minimax_ai = None
        self._setup_difficulty()
    
    def _setup_difficulty(self):
        """Setup AI parameters based on difficulty."""
        if self.difficulty == 'easy':
            self.minimax_ai = MinimaxAI(max_depth=1)
            self.minimax_ai.time_limit = 1.0
            self.random_move_chance = 0.3  # 30% chance of random move
        elif self.difficulty == 'medium':
            self.minimax_ai = MinimaxAI(max_depth=3)
            self.minimax_ai.time_limit = 3.0
            self.random_move_chance = 0.1  # 10% chance of random move
        elif self.difficulty == 'hard':
            self.minimax_ai = MinimaxAI(max_depth=5)
            self.minimax_ai.time_limit = 8.0
            self.random_move_chance = 0.0  # No random moves
        else:
            # Default to medium
            self.difficulty = 'medium'
            self._setup_difficulty()
    
    def get_move(self, board: ShogiBoard, player: Player) -> Optional[Dict]:
        """Get a move based on the current difficulty."""
        import random
        
        # Sometimes make random moves for easier difficulties
        if random.random() < self.random_move_chance:
            legal_moves = board.get_all_legal_moves(player)
            if legal_moves:
                return random.choice(legal_moves)
        
        # Use minimax for the best move
        return self.minimax_ai.get_best_move(board, player)
    
    def set_difficulty(self, difficulty: str):
        """Change the difficulty level."""
        self.difficulty = difficulty
        self._setup_difficulty()
    
    def get_difficulty(self) -> str:
        """Get the current difficulty level."""
        return self.difficulty

