"""
Main AI engine that combines all AI components.
"""

from typing import Dict, Optional
from game.board import ShogiBoard
from game.pieces import Player
from minimax import DifficultyAI
from opening_book import OpeningBook


class ShogiAI:
    def __init__(self, difficulty: str = 'medium', use_opening_book: bool = True):
        self.difficulty = difficulty
        self.use_opening_book = use_opening_book
        self.ai_engine = DifficultyAI(difficulty)
        self.opening_book = OpeningBook() if use_opening_book else None
        self.move_count = 0
    
    def get_move(self, board: ShogiBoard, player: Player) -> Optional[Dict]:
        """Get the best move for the AI player."""
        self.move_count = len(board.move_history)
        
        # Try opening book first (for hard difficulty or if explicitly enabled)
        if (self.opening_book and 
            (self.difficulty == 'hard' or self.use_opening_book) and 
            self.move_count < 10):
            
            book_move = self.opening_book.get_book_move(board, player)
            if book_move:
                return book_move
        
        # Fall back to minimax search
        return self.ai_engine.get_move(board, player)
    
    def set_difficulty(self, difficulty: str):
        """Change the AI difficulty level."""
        self.difficulty = difficulty
        self.ai_engine.set_difficulty(difficulty)
    
    def set_opening_book(self, use_book: bool):
        """Enable or disable opening book usage."""
        self.use_opening_book = use_book
        if use_book and not self.opening_book:
            self.opening_book = OpeningBook()
        elif not use_book:
            self.opening_book = None
    
    def get_difficulty(self) -> str:
        """Get current difficulty level."""
        return self.difficulty
    
    def get_analysis(self, board: ShogiBoard, player: Player) -> Dict:
        """Get analysis of the current position."""
        from evaluation import PositionEvaluator
        
        evaluator = PositionEvaluator()
        
        analysis = {
            'material_balance': evaluator.evaluate_material(board, player),
            'position_score': evaluator.evaluate_position(board, player),
            'king_safety': evaluator.evaluate_king_safety(board, player),
            'mobility': evaluator.evaluate_mobility(board, player),
            'threats': evaluator.evaluate_threats(board, player),
            'total_evaluation': evaluator.evaluate_position_full(board, player),
            'in_check': board.is_in_check(player),
            'checkmate': board.is_checkmate(player),
            'legal_moves_count': len(board.get_all_legal_moves(player))
        }
        
        return analysis
    
    def suggest_move(self, board: ShogiBoard, player: Player) -> Dict:
        """Get move suggestion with analysis."""
        best_move = self.get_move(board, player)
        analysis = self.get_analysis(board, player)
        
        return {
            'move': best_move,
            'analysis': analysis,
            'difficulty': self.difficulty,
            'using_opening_book': (self.opening_book is not None and 
                                 self.move_count < 10 and 
                                 self.use_opening_book)
        }

