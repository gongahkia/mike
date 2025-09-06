"""
Main game controller for Shogi game management.
"""

from typing import Dict, List, Optional, Tuple
from backend.game.board import ShogiBoard
from backend.game.pieces import Player, PieceType


class ShogiGame:
    def __init__(self):
        self.board = ShogiBoard()
        self.game_over = False
        self.winner = None
        self.game_id = None
    
    def new_game(self, game_id: str = None):
        """Start a new game."""
        self.board = ShogiBoard()
        self.game_over = False
        self.winner = None
        self.game_id = game_id
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int, 
                  promote: bool = False) -> Dict:
        """Make a move and return the result."""
        if self.game_over:
            return {
                'success': False,
                'error': 'Game is already over'
            }
        
        success = self.board.make_move(from_row, from_col, to_row, to_col, promote)
        
        if not success:
            return {
                'success': False,
                'error': 'Invalid move'
            }
        
        # Check for game over conditions
        current_player = self.board.current_player
        if self.board.is_checkmate(current_player):
            self.game_over = True
            self.winner = current_player.opponent()
            return {
                'success': True,
                'game_over': True,
                'winner': self.winner.value,
                'reason': 'checkmate'
            }
        
        return {
            'success': True,
            'game_over': False
        }
    
    def drop_piece(self, piece_type: str, row: int, col: int) -> Dict:
        """Drop a captured piece and return the result."""
        if self.game_over:
            return {
                'success': False,
                'error': 'Game is already over'
            }
        
        try:
            piece_type_enum = PieceType(piece_type)
        except ValueError:
            return {
                'success': False,
                'error': 'Invalid piece type'
            }
        
        success = self.board.drop_piece(piece_type_enum, row, col)
        
        if not success:
            return {
                'success': False,
                'error': 'Invalid drop'
            }
        
        # Check for game over conditions
        current_player = self.board.current_player
        if self.board.is_checkmate(current_player):
            self.game_over = True
            self.winner = current_player.opponent()
            return {
                'success': True,
                'game_over': True,
                'winner': self.winner.value,
                'reason': 'checkmate'
            }
        
        return {
            'success': True,
            'game_over': False
        }
    
    def get_legal_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get legal moves for a piece at the given position."""
        piece = self.board.get_piece(row, col)
        if not piece or piece.player != self.board.current_player:
            return []
        
        moves = piece.get_moves(row, col, self.board)
        legal_moves = []
        
        # Filter out moves that would leave king in check
        for to_row, to_col in moves:
            captured_piece = self.board.get_piece(to_row, to_col)
            self.board.set_piece(to_row, to_col, piece)
            self.board.set_piece(row, col, None)
            
            if not self.board.is_in_check(piece.player):
                legal_moves.append((to_row, to_col))
            
            # Undo the move
            self.board.set_piece(row, col, piece)
            self.board.set_piece(to_row, to_col, captured_piece)
        
        return legal_moves
    
    def get_drop_positions(self, piece_type: str) -> List[Tuple[int, int]]:
        """Get valid drop positions for a piece type."""
        try:
            piece_type_enum = PieceType(piece_type)
        except ValueError:
            return []
        
        positions = []
        current_player = self.board.current_player
        
        for row in range(9):
            for col in range(9):
                if self.board.can_drop_piece(piece_type_enum, row, col, current_player):
                    # Test the drop to make sure it doesn't leave king in check
                    piece = next((p for p in self.board.captured_pieces[current_player] 
                                if p.piece_type == piece_type_enum), None)
                    if piece:
                        self.board.set_piece(row, col, piece)
                        if not self.board.is_in_check(current_player):
                            positions.append((row, col))
                        self.board.set_piece(row, col, None)
        
        return positions
    
    def can_promote(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if a piece can promote with the given move."""
        piece = self.board.get_piece(from_row, from_col)
        if not piece or not piece.can_promote():
            return False
        
        # Check if move involves promotion zone
        if piece.player == Player.SENTE:
            return from_row <= 2 or to_row <= 2
        else:
            return from_row >= 6 or to_row >= 6
    
    def get_game_state(self) -> Dict:
        """Get the current game state."""
        state = self.board.to_dict()
        state.update({
            'game_over': self.game_over,
            'winner': self.winner.value if self.winner else None,
            'game_id': self.game_id
        })
        return state
    
    def get_move_history(self) -> List[Dict]:
        """Get the move history."""
        return self.board.move_history.copy()
    
    def is_valid_move(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Check if a move is valid without making it."""
        piece = self.board.get_piece(from_row, from_col)
        if not piece or piece.player != self.board.current_player:
            return False
        
        valid_moves = piece.get_moves(from_row, from_col, self.board)
        if (to_row, to_col) not in valid_moves:
            return False
        
        # Check if move would leave king in check
        captured_piece = self.board.get_piece(to_row, to_col)
        self.board.set_piece(to_row, to_col, piece)
        self.board.set_piece(from_row, from_col, None)
        
        in_check = self.board.is_in_check(self.board.current_player)
        
        # Undo the move
        self.board.set_piece(from_row, from_col, piece)
        self.board.set_piece(to_row, to_col, captured_piece)
        
        return not in_check

