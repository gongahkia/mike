"""
Shogi piece definitions and movement logic.
"""

from enum import Enum
from typing import List, Tuple, Optional


class Player(Enum):
    SENTE = "sente"  # First player (bottom)
    GOTE = "gote"    # Second player (top)
    
    def opponent(self):
        return Player.GOTE if self == Player.SENTE else Player.SENTE


class PieceType(Enum):
    # Basic pieces
    KING = "king"
    ROOK = "rook"
    BISHOP = "bishop"
    GOLD = "gold"
    SILVER = "silver"
    KNIGHT = "knight"
    LANCE = "lance"
    PAWN = "pawn"
    
    # Promoted pieces
    PROMOTED_ROOK = "promoted_rook"    # Dragon
    PROMOTED_BISHOP = "promoted_bishop"  # Horse
    PROMOTED_SILVER = "promoted_silver"
    PROMOTED_KNIGHT = "promoted_knight"
    PROMOTED_LANCE = "promoted_lance"
    PROMOTED_PAWN = "promoted_pawn"    # Tokin


class Piece:
    def __init__(self, piece_type: PieceType, player: Player, promoted: bool = False):
        self.piece_type = piece_type
        self.player = player
        self.promoted = promoted
    
    def __str__(self):
        symbols = {
            PieceType.KING: "K",
            PieceType.ROOK: "R",
            PieceType.BISHOP: "B",
            PieceType.GOLD: "G",
            PieceType.SILVER: "S",
            PieceType.KNIGHT: "N",
            PieceType.LANCE: "L",
            PieceType.PAWN: "P",
            PieceType.PROMOTED_ROOK: "+R",
            PieceType.PROMOTED_BISHOP: "+B",
            PieceType.PROMOTED_SILVER: "+S",
            PieceType.PROMOTED_KNIGHT: "+N",
            PieceType.PROMOTED_LANCE: "+L",
            PieceType.PROMOTED_PAWN: "+P"
        }
        symbol = symbols[self.piece_type]
        return symbol.lower() if self.player == Player.GOTE else symbol
    
    def can_promote(self) -> bool:
        """Check if this piece can be promoted."""
        promotable = {
            PieceType.ROOK, PieceType.BISHOP, PieceType.SILVER,
            PieceType.KNIGHT, PieceType.LANCE, PieceType.PAWN
        }
        return self.piece_type in promotable and not self.promoted
    
    def promote(self) -> 'Piece':
        """Return a promoted version of this piece."""
        if not self.can_promote():
            return self
        
        promotion_map = {
            PieceType.ROOK: PieceType.PROMOTED_ROOK,
            PieceType.BISHOP: PieceType.PROMOTED_BISHOP,
            PieceType.SILVER: PieceType.PROMOTED_SILVER,
            PieceType.KNIGHT: PieceType.PROMOTED_KNIGHT,
            PieceType.LANCE: PieceType.PROMOTED_LANCE,
            PieceType.PAWN: PieceType.PROMOTED_PAWN
        }
        
        return Piece(promotion_map[self.piece_type], self.player, True)
    
    def demote(self) -> 'Piece':
        """Return the unpromoted version of this piece (for captures)."""
        demotion_map = {
            PieceType.PROMOTED_ROOK: PieceType.ROOK,
            PieceType.PROMOTED_BISHOP: PieceType.BISHOP,
            PieceType.PROMOTED_SILVER: PieceType.SILVER,
            PieceType.PROMOTED_KNIGHT: PieceType.KNIGHT,
            PieceType.PROMOTED_LANCE: PieceType.LANCE,
            PieceType.PROMOTED_PAWN: PieceType.PAWN
        }
        
        if self.piece_type in demotion_map:
            return Piece(demotion_map[self.piece_type], self.player, False)
        return Piece(self.piece_type, self.player, False)
    
    def get_moves(self, row: int, col: int, board) -> List[Tuple[int, int]]:
        """Get all possible moves for this piece from the given position."""
        moves = []
        
        # Direction multiplier based on player
        direction = 1 if self.player == Player.SENTE else -1
        
        if self.piece_type == PieceType.KING:
            # King moves one square in any direction
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    new_row, new_col = row + dr, col + dc
                    if board.is_valid_position(new_row, new_col):
                        if not board.get_piece(new_row, new_col) or \
                           board.get_piece(new_row, new_col).player != self.player:
                            moves.append((new_row, new_col))
        
        elif self.piece_type == PieceType.ROOK:
            # Rook moves horizontally and vertically
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dr, dc in directions:
                for i in range(1, 9):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not board.is_valid_position(new_row, new_col):
                        break
                    piece = board.get_piece(new_row, new_col)
                    if piece:
                        if piece.player != self.player:
                            moves.append((new_row, new_col))
                        break
                    moves.append((new_row, new_col))
        
        elif self.piece_type == PieceType.BISHOP:
            # Bishop moves diagonally
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, 9):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not board.is_valid_position(new_row, new_col):
                        break
                    piece = board.get_piece(new_row, new_col)
                    if piece:
                        if piece.player != self.player:
                            moves.append((new_row, new_col))
                        break
                    moves.append((new_row, new_col))
        
        elif self.piece_type == PieceType.GOLD or \
             self.piece_type in [PieceType.PROMOTED_SILVER, PieceType.PROMOTED_KNIGHT, 
                               PieceType.PROMOTED_LANCE, PieceType.PROMOTED_PAWN]:
            # Gold general movement (and promoted pieces except rook/bishop)
            gold_moves = [(-1*direction, -1), (-1*direction, 0), (-1*direction, 1),
                         (0, -1), (0, 1), (1*direction, 0)]
            for dr, dc in gold_moves:
                new_row, new_col = row + dr, col + dc
                if board.is_valid_position(new_row, new_col):
                    piece = board.get_piece(new_row, new_col)
                    if not piece or piece.player != self.player:
                        moves.append((new_row, new_col))
        
        elif self.piece_type == PieceType.SILVER:
            # Silver general movement
            silver_moves = [(-1*direction, -1), (-1*direction, 0), (-1*direction, 1),
                           (1*direction, -1), (1*direction, 1)]
            for dr, dc in silver_moves:
                new_row, new_col = row + dr, col + dc
                if board.is_valid_position(new_row, new_col):
                    piece = board.get_piece(new_row, new_col)
                    if not piece or piece.player != self.player:
                        moves.append((new_row, new_col))
        
        elif self.piece_type == PieceType.KNIGHT:
            # Knight moves in L-shape, forward only
            knight_moves = [(-2*direction, -1), (-2*direction, 1)]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if board.is_valid_position(new_row, new_col):
                    piece = board.get_piece(new_row, new_col)
                    if not piece or piece.player != self.player:
                        moves.append((new_row, new_col))
        
        elif self.piece_type == PieceType.LANCE:
            # Lance moves forward only
            for i in range(1, 9):
                new_row, new_col = row + (-1*direction) * i, col
                if not board.is_valid_position(new_row, new_col):
                    break
                piece = board.get_piece(new_row, new_col)
                if piece:
                    if piece.player != self.player:
                        moves.append((new_row, new_col))
                    break
                moves.append((new_row, new_col))
        
        elif self.piece_type == PieceType.PAWN:
            # Pawn moves one square forward
            new_row, new_col = row + (-1*direction), col
            if board.is_valid_position(new_row, new_col):
                piece = board.get_piece(new_row, new_col)
                if not piece or piece.player != self.player:
                    moves.append((new_row, new_col))
        
        elif self.piece_type == PieceType.PROMOTED_ROOK:
            # Dragon (promoted rook): rook + king
            # Rook moves
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dr, dc in directions:
                for i in range(1, 9):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not board.is_valid_position(new_row, new_col):
                        break
                    piece = board.get_piece(new_row, new_col)
                    if piece:
                        if piece.player != self.player:
                            moves.append((new_row, new_col))
                        break
                    moves.append((new_row, new_col))
            # King diagonal moves
            king_diagonals = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in king_diagonals:
                new_row, new_col = row + dr, col + dc
                if board.is_valid_position(new_row, new_col):
                    piece = board.get_piece(new_row, new_col)
                    if not piece or piece.player != self.player:
                        moves.append((new_row, new_col))
        
        elif self.piece_type == PieceType.PROMOTED_BISHOP:
            # Horse (promoted bishop): bishop + king
            # Bishop moves
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dr, dc in directions:
                for i in range(1, 9):
                    new_row, new_col = row + dr * i, col + dc * i
                    if not board.is_valid_position(new_row, new_col):
                        break
                    piece = board.get_piece(new_row, new_col)
                    if piece:
                        if piece.player != self.player:
                            moves.append((new_row, new_col))
                        break
                    moves.append((new_row, new_col))
            # King orthogonal moves
            king_orthogonals = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for dr, dc in king_orthogonals:
                new_row, new_col = row + dr, col + dc
                if board.is_valid_position(new_row, new_col):
                    piece = board.get_piece(new_row, new_col)
                    if not piece or piece.player != self.player:
                        moves.append((new_row, new_col))
        
        return moves

