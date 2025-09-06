"""
Main game controller for Shogi game management.
"""

from typing import Dict, List, Optional, Tuple
from game.board import ShogiBoard
from game.pieces import Player, PieceType


class ShogiGame:
    """Main game controller for Shogi."""
    
    def __init__(self):
        self.board = ShogiBoard()
        self.game_id = None
        self.game_over = False
        self.winner = None
        self.game_result = None
    
    def new_game(self, game_id: str):
        """Start a new game."""
        self.game_id = game_id
        self.board = ShogiBoard()
        self.game_over = False
        self.winner = None
        self.game_result = None
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int, promote: bool = False) -> Dict:
        """Make a move in the game."""
        if self.game_over:
            return {'success': False, 'error': 'Game is already over'}
        
        result = self.board.move_piece(from_row, from_col, to_row, to_col, promote)
        
        if result['success']:
            # Check for game end conditions
            self._check_game_end()
        
        return result
    
    def drop_piece(self, piece_type: str, row: int, col: int) -> Dict:
        """Drop a captured piece."""
        if self.game_over:
            return {'success': False, 'error': 'Game is already over'}
        
        result = self.board.drop_piece(piece_type, row, col)
        
        if result['success']:
            # Check for game end conditions
            self._check_game_end()
        
        return result
    
    def get_legal_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get legal moves for a piece at the specified position."""
        piece = self.board.get_piece(row, col)
        if not piece:
            return []
        
        if piece.player != self.board.current_player:
            return []
        
        return piece.get_moves(row, col, self.board)
    
    def get_drop_positions(self, piece_type: str) -> List[Tuple[int, int]]:
        """Get valid drop positions for a piece type."""
        try:
            piece_type_enum = PieceType(piece_type)
        except ValueError:
            return []
        
        # Check if player has this piece type in captured pieces
        captured_pieces = self.board.captured[self.board.current_player]
        if not any(p.piece_type == piece_type_enum for p in captured_pieces):
            return []
        
        positions = []
        for row in range(9):
            for col in range(9):
                if (self.board.get_piece(row, col) is None and 
                    self.board._is_valid_drop(piece_type_enum, row, col)):
                    positions.append((row, col))
        
        return positions
    
    def _check_game_end(self):
        """Check if the game has ended."""
        # Check for checkmate
        if self.board.is_checkmate(Player.SENTE):
            self.game_over = True
            self.winner = Player.GOTE
            self.game_result = "Checkmate - Gote wins"
        elif self.board.is_checkmate(Player.GOTE):
            self.game_over = True
            self.winner = Player.SENTE
            self.game_result = "Checkmate - Sente wins"
        
        # Could add other end conditions like repetition, time, etc.
    
    def get_game_state(self) -> Dict:
        """Get the current game state."""
        board_state = self.board.to_dict()
        
        return {
            **board_state,
            'game_over': self.game_over,
            'winner': self.winner.value if self.winner else None,
            'game_result': self.game_result,
            'game_id': self.game_id
        }
    
    def get_move_history(self) -> List[Dict]:
        """Get the move history."""
        return self.board.move_history.copy()
    
    def is_valid_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if a move is valid."""
        piece = self.board.get_piece(from_row, from_col)
        if not piece:
            return False
        
        if piece.player != self.board.current_player:
            return False
        
        legal_moves = piece.get_moves(from_row, from_col, self.board)
        return (to_row, to_col) in legal_moves
    
    def can_promote(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if a piece can promote with this move."""
        piece = self.board.get_piece(from_row, from_col)
        if not piece:
            return False
        
        return piece.can_promote(from_row, to_row)
    
    def must_promote(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if a piece must promote with this move."""
        piece = self.board.get_piece(from_row, from_col)
        if not piece:
            return False
        
        return piece.must_promote(to_row)

