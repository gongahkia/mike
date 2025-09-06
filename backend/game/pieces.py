"""
Shogi piece definitions and movement logic.
"""

from enum import Enum
from typing import List, Tuple, Optional


class Player(Enum):
    """Player enumeration."""
    SENTE = "sente"  # First player (bottom)
    GOTE = "gote"    # Second player (top)


class PieceType(Enum):
    """Piece type enumeration."""
    KING = "king"
    ROOK = "rook"
    BISHOP = "bishop"
    GOLD = "gold"
    SILVER = "silver"
    KNIGHT = "knight"
    LANCE = "lance"
    PAWN = "pawn"
    PROMOTED_ROOK = "promoted_rook"
    PROMOTED_BISHOP = "promoted_bishop"
    PROMOTED_SILVER = "promoted_silver"
    PROMOTED_KNIGHT = "promoted_knight"
    PROMOTED_LANCE = "promoted_lance"
    PROMOTED_PAWN = "promoted_pawn"


class Piece:
    """Represents a Shogi piece."""
    
    def __init__(self, piece_type: PieceType, player: Player, promoted: bool = False):
        self.piece_type = piece_type
        self.player = player
        self.promoted = promoted
    
    def can_promote(self, from_row: int, to_row: int) -> bool:
        """Check if piece can promote based on move."""
        if self.promoted:
            return False
        
        # Pieces that cannot promote
        if self.piece_type in [PieceType.KING, PieceType.GOLD]:
            return False
        
        # Check if move involves promotion zone
        if self.player == Player.SENTE:
            # Sente promotes in rows 0-2 (top 3 rows)
            return from_row <= 2 or to_row <= 2
        else:
            # Gote promotes in rows 6-8 (bottom 3 rows)
            return from_row >= 6 or to_row >= 6
    
    def must_promote(self, to_row: int) -> bool:
        """Check if piece must promote (cannot move further without promoting)."""
        if self.promoted:
            return False
        
        if self.piece_type == PieceType.PAWN:
            if self.player == Player.SENTE and to_row == 0:
                return True
            if self.player == Player.GOTE and to_row == 8:
                return True
        
        if self.piece_type == PieceType.LANCE:
            if self.player == Player.SENTE and to_row == 0:
                return True
            if self.player == Player.GOTE and to_row == 8:
                return True
        
        if self.piece_type == PieceType.KNIGHT:
            if self.player == Player.SENTE and to_row <= 1:
                return True
            if self.player == Player.GOTE and to_row >= 7:
                return True
        
        return False
    
    def get_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get all possible moves for this piece from the given position."""
        moves = []
        
        if self.piece_type == PieceType.KING:
            moves = self._get_king_moves(row, col, board)
        elif self.piece_type == PieceType.ROOK:
            moves = self._get_rook_moves(row, col, board)
        elif self.piece_type == PieceType.BISHOP:
            moves = self._get_bishop_moves(row, col, board)
        elif self.piece_type == PieceType.GOLD or self.promoted:
            moves = self._get_gold_moves(row, col, board)
        elif self.piece_type == PieceType.SILVER:
            moves = self._get_silver_moves(row, col, board)
        elif self.piece_type == PieceType.KNIGHT:
            moves = self._get_knight_moves(row, col, board)
        elif self.piece_type == PieceType.LANCE:
            moves = self._get_lance_moves(row, col, board)
        elif self.piece_type == PieceType.PAWN:
            moves = self._get_pawn_moves(row, col, board)
        elif self.piece_type == PieceType.PROMOTED_ROOK:
            moves = self._get_promoted_rook_moves(row, col, board)
        elif self.piece_type == PieceType.PROMOTED_BISHOP:
            moves = self._get_promoted_bishop_moves(row, col, board)
        
        # Filter out moves that would put own king in check
        valid_moves = []
        for move_row, move_col in moves:
            if self._is_valid_move(row, col, move_row, move_col, board):
                valid_moves.append((move_row, move_col))
        
        return valid_moves
    
    def _is_valid_move(self, from_row: int, from_col: int, to_row: int, to_col: int, board) -> bool:
        """Check if move is valid (doesn't put own king in check)."""
        # Make temporary move
        original_piece = board.get_piece(to_row, to_col)
        board.set_piece(to_row, to_col, self)
        board.set_piece(from_row, from_col, None)
        
        # Check if own king is in check
        in_check = board.is_in_check(self.player)
        
        # Restore board
        board.set_piece(from_row, from_col, self)
        board.set_piece(to_row, to_col, original_piece)
        
        return not in_check
    
    def _get_king_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get king moves (one square in any direction)."""
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 9 and 0 <= new_col < 9:
                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None or target_piece.player != self.player:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_rook_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get rook moves (horizontal and vertical lines)."""
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, 9):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 9 and 0 <= new_col < 9):
                    break
                
                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None:
                    moves.append((new_row, new_col))
                elif target_piece.player != self.player:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def _get_bishop_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get bishop moves (diagonal lines)."""
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 9):
                new_row, new_col = row + dr * i, col + dc * i
                if not (0 <= new_row < 9 and 0 <= new_col < 9):
                    break
                
                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None:
                    moves.append((new_row, new_col))
                elif target_piece.player != self.player:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def _get_gold_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get gold general moves (6 directions)."""
        moves = []
        
        if self.player == Player.SENTE:
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0)]
        else:
            directions = [(1, -1), (1, 0), (1, 1), (0, -1), (0, 1), (-1, 0)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 9 and 0 <= new_col < 9:
                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None or target_piece.player != self.player:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_silver_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get silver general moves (5 directions)."""
        moves = []
        
        if self.player == Player.SENTE:
            directions = [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 1)]
        else:
            directions = [(1, -1), (1, 0), (1, 1), (-1, -1), (-1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 9 and 0 <= new_col < 9:
                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None or target_piece.player != self.player:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_knight_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get knight moves (L-shaped, forward only)."""
        moves = []
        
        if self.player == Player.SENTE:
            directions = [(-2, -1), (-2, 1)]
        else:
            directions = [(2, -1), (2, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 9 and 0 <= new_col < 9:
                target_piece = board.get_piece(new_row, new_col)
                if target_piece is None or target_piece.player != self.player:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_lance_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get lance moves (forward line)."""
        moves = []
        
        if self.player == Player.SENTE:
            direction = -1
        else:
            direction = 1
        
        for i in range(1, 9):
            new_row = row + direction * i
            if not (0 <= new_row < 9):
                break
            
            target_piece = board.get_piece(new_row, col)
            if target_piece is None:
                moves.append((new_row, col))
            elif target_piece.player != self.player:
                moves.append((new_row, col))
                break
            else:
                break
        
        return moves
    
    def _get_pawn_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get pawn moves (one square forward)."""
        moves = []
        
        if self.player == Player.SENTE:
            new_row = row - 1
        else:
            new_row = row + 1
        
        if 0 <= new_row < 9:
            target_piece = board.get_piece(new_row, col)
            if target_piece is None or target_piece.player != self.player:
                moves.append((new_row, col))
        
        return moves
    
    def _get_promoted_rook_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get promoted rook moves (rook + king)."""
        moves = self._get_rook_moves(row, col, board)
        moves.extend(self._get_king_moves(row, col, board))
        return list(set(moves))  # Remove duplicates
    
    def _get_promoted_bishop_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get promoted bishop moves (bishop + king)."""
        moves = self._get_bishop_moves(row, col, board)
        moves.extend(self._get_king_moves(row, col, board))
        return list(set(moves))  # Remove duplicates
    
    def to_dict(self) -> dict:
        """Convert piece to dictionary representation."""
        return {
            'type': self.piece_type.value,
            'player': self.player.value,
            'promoted': self.promoted
        }
    
    def __str__(self) -> str:
        """String representation of the piece."""
        piece_symbols = {
            PieceType.KING: '王' if self.player == Player.SENTE else '玉',
            PieceType.ROOK: '飛',
            PieceType.BISHOP: '角',
            PieceType.GOLD: '金',
            PieceType.SILVER: '銀',
            PieceType.KNIGHT: '桂',
            PieceType.LANCE: '香',
            PieceType.PAWN: '歩',
            PieceType.PROMOTED_ROOK: '龍',
            PieceType.PROMOTED_BISHOP: '馬',
            PieceType.PROMOTED_SILVER: '成銀',
            PieceType.PROMOTED_KNIGHT: '成桂',
            PieceType.PROMOTED_LANCE: '成香',
            PieceType.PROMOTED_PAWN: 'と'
        }
        
        return piece_symbols.get(self.piece_type, '?')

