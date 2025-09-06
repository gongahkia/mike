"""
Main AI engine that combines all AI components.
"""

from typing import Dict, Optional
from game.board import ShogiBoard
from game.pieces import Player
from ai.minimax import DifficultyAI
from ai.opening_book import OpeningBook
from ai.evaluation import PositionEvaluator


class ShogiAI:
    """Main AI engine for Shogi."""
    
    def __init__(self, difficulty: str = 'medium'):
        self.difficulty = difficulty
        self.minimax_ai = DifficultyAI(difficulty)
        self.opening_book = OpeningBook()
        self.evaluator = PositionEvaluator()
    
    def get_move(self, board: ShogiBoard, player: Player) -> Optional[Dict]:
        """Get the best move for the current position."""
        # Try opening book first
        opening_move = self.opening_book.get_opening_move(board, player)
        if opening_move:
            # Validate the opening move is legal
            if self._is_legal_move(board, opening_move, player):
                opening_move['using_opening_book'] = True
                return opening_move
        
        # Use minimax AI
        move = self.minimax_ai.get_move(board, player)
        if move:
            move['using_opening_book'] = False
        
        return move
    
    def _is_legal_move(self, board: ShogiBoard, move: Dict, player: Player) -> bool:
        """Check if a move is legal."""
        if move['type'] == 'move':
            from_pos = move['from']
            to_pos = move['to']
            
            piece = board.get_piece(from_pos[0], from_pos[1])
            if not piece or piece.player != player:
                return False
            
            legal_moves = piece.get_moves(from_pos[0], from_pos[1], board)
            return to_pos in legal_moves
        
        elif move['type'] == 'drop':
            piece_type = move['piece_type']
            to_pos = move['to']
            
            # Check if piece is available and drop is valid
            captured_pieces = board.captured[player]
            if not any(p.piece_type == piece_type for p in captured_pieces):
                return False
            
            if board.get_piece(to_pos[0], to_pos[1]) is not None:
                return False
            
            return board._is_valid_drop(piece_type, to_pos[0], to_pos[1])
        
        return False
    
    def suggest_move(self, board: ShogiBoard, player: Player) -> Dict:
        """Get a move suggestion with analysis."""
        move = self.get_move(board, player)
        analysis = self.get_analysis(board, player)
        
        return {
            'move': move,
            'analysis': analysis,
            'difficulty': self.difficulty,
            'using_opening_book': move.get('using_opening_book', False) if move else False
        }
    
    def set_difficulty(self, difficulty: str):
        """Change the AI difficulty level."""
        self.difficulty = difficulty
        self.minimax_ai.set_difficulty(difficulty)
    
    def get_difficulty(self) -> str:
        """Get the current difficulty level."""
        return self.difficulty
    
    def get_analysis(self, board: ShogiBoard, player: Player) -> Dict:
        """Get analysis of the current position."""
        
        evaluator = PositionEvaluator()
        
        # Get detailed evaluation
        evaluation = evaluator.get_detailed_evaluation(board, player)
        
        # Add move count
        evaluation['move_count'] = len(board.move_history)
        
        # Add legal moves count
        legal_moves = board.get_all_legal_moves(player)
        evaluation['legal_moves_count'] = len(legal_moves)
        
        # Add opening information
        if self.opening_book.is_known_position(board):
            opening_name = self.opening_book.get_opening_name(board)
            evaluation['opening'] = opening_name
        
        return evaluation

