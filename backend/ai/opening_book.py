"""
Opening book for Shogi AI to improve early game play.
"""

from typing import Dict, List, Optional, Tuple
from backend.game.board import ShogiBoard
from backend.game.pieces import Player


class OpeningBook:
    def __init__(self):
        # Common opening moves in Shogi
        # Format: (from_row, from_col, to_row, to_col, promote)
        self.opening_moves = {
            # Initial position moves for SENTE (first player)
            'initial_sente': [
                (6, 6, 5, 6, False),  # P-7f (advance central pawn)
                (6, 2, 5, 2, False),  # P-3f (advance rook pawn)
                (6, 4, 5, 4, False),  # P-5f (advance king pawn)
                (8, 6, 7, 7, False),  # S-6h (silver up)
                (8, 2, 7, 3, False),  # S-3h (silver up)
            ],
            
            # Response moves for GOTE (second player)
            'initial_gote': [
                (2, 2, 3, 2, False),  # P-3d (mirror central pawn)
                (2, 6, 3, 6, False),  # P-7d (mirror rook pawn)
                (2, 4, 3, 4, False),  # P-5d (mirror king pawn)
                (0, 2, 1, 3, False),  # S-3b (silver up)
                (0, 6, 1, 5, False),  # S-7b (silver up)
            ],
            
            # Static Rook opening patterns
            'static_rook_sente': [
                (6, 6, 5, 6, False),  # P-7f
                (8, 6, 7, 7, False),  # S-6h
                (8, 2, 7, 3, False),  # S-3h
                (7, 7, 6, 6, False),  # S-7g
                (8, 5, 7, 6, False),  # G-6h
            ],
            
            # Ranging Rook opening patterns
            'ranging_rook_sente': [
                (6, 6, 5, 6, False),  # P-7f
                (7, 1, 5, 1, False),  # R-6h (rook to 6th file)
                (8, 6, 7, 7, False),  # S-6h
                (6, 5, 5, 5, False),  # P-6f
            ]
        }
        
        # Position patterns to recognize
        self.position_patterns = {}
        
        # Move counter for opening phase
        self.max_opening_moves = 10
    
    def get_opening_move(self, board: ShogiBoard, player: Player) -> Optional[Tuple[int, int, int, int, bool]]:
        """Get an opening book move if available."""
        move_count = len(board.move_history)
        
        # Only use opening book in the first few moves
        if move_count >= self.max_opening_moves:
            return None
        
        # Determine which opening to use based on position
        if move_count == 0 and player == Player.SENTE:
            # First move for SENTE
            moves = self.opening_moves['initial_sente']
            if moves:
                return moves[0]
        
        elif move_count == 1 and player == Player.GOTE:
            # First move for GOTE - respond to SENTE's move
            moves = self.opening_moves['initial_gote']
            if moves:
                return moves[0]
        
        # For subsequent moves, try to continue a coherent opening
        if player == Player.SENTE and move_count < len(self.opening_moves['static_rook_sente']) * 2:
            move_index = move_count // 2
            if move_index < len(self.opening_moves['static_rook_sente']):
                return self.opening_moves['static_rook_sente'][move_index]
        
        elif player == Player.GOTE and move_count < len(self.opening_moves['initial_gote']) * 2:
            move_index = (move_count - 1) // 2
            if move_index < len(self.opening_moves['initial_gote']):
                return self.opening_moves['initial_gote'][move_index]
        
        return None
    
    def is_valid_opening_move(self, board: ShogiBoard, move: Tuple[int, int, int, int, bool]) -> bool:
        """Check if an opening book move is valid in the current position."""
        from_row, from_col, to_row, to_col, promote = move
        
        # Check if there's a piece at the from position
        piece = board.get_piece(from_row, from_col)
        if not piece or piece.player != board.current_player:
            return False
        
        # Check if the move is legal
        legal_moves = piece.get_moves(from_row, from_col, board)
        if (to_row, to_col) not in legal_moves:
            return False
        
        # Check if move doesn't leave king in check
        captured_piece = board.get_piece(to_row, to_col)
        board.set_piece(to_row, to_col, piece)
        board.set_piece(from_row, from_col, None)
        
        in_check = board.is_in_check(board.current_player)
        
        # Undo the move
        board.set_piece(from_row, from_col, piece)
        board.set_piece(to_row, to_col, captured_piece)
        
        return not in_check
    
    def add_opening_line(self, name: str, moves: List[Tuple[int, int, int, int, bool]]):
        """Add a new opening line to the book."""
        self.opening_moves[name] = moves
    
    def get_book_move(self, board: ShogiBoard, player: Player) -> Optional[Dict]:
        """Get a move from the opening book in the format expected by the game."""
        opening_move = self.get_opening_move(board, player)
        
        if opening_move and self.is_valid_opening_move(board, opening_move):
            from_row, from_col, to_row, to_col, promote = opening_move
            return {
                'type': 'move',
                'from': (from_row, from_col),
                'to': (to_row, to_col),
                'promote': promote,
                'piece': board.get_piece(from_row, from_col)
            }
        
        return None

