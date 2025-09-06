"""
Shogi board representation and game state management.
"""

from typing import List, Optional, Dict, Tuple
from game.pieces import Piece, PieceType, Player


class ShogiBoard:
    """Represents a Shogi board and game state."""
    
    def __init__(self):
        self.board = [[None for _ in range(9)] for _ in range(9)]
        self.captured = {Player.SENTE: [], Player.GOTE: []}
        self.current_player = Player.SENTE
        self.move_history = []
        self.setup_initial_position()
    
    def setup_initial_position(self):
        """Set up the initial Shogi position."""
        # Clear board
        self.board = [[None for _ in range(9)] for _ in range(9)]
        
        # Place Gote pieces (top, rows 0-2)
        # Back row (row 0)
        self.board[0][0] = Piece(PieceType.LANCE, Player.GOTE)
        self.board[0][1] = Piece(PieceType.KNIGHT, Player.GOTE)
        self.board[0][2] = Piece(PieceType.SILVER, Player.GOTE)
        self.board[0][3] = Piece(PieceType.GOLD, Player.GOTE)
        self.board[0][4] = Piece(PieceType.KING, Player.GOTE)
        self.board[0][5] = Piece(PieceType.GOLD, Player.GOTE)
        self.board[0][6] = Piece(PieceType.SILVER, Player.GOTE)
        self.board[0][7] = Piece(PieceType.KNIGHT, Player.GOTE)
        self.board[0][8] = Piece(PieceType.LANCE, Player.GOTE)
        
        # Second row (row 1) - Rook and Bishop
        self.board[1][1] = Piece(PieceType.BISHOP, Player.GOTE)
        self.board[1][7] = Piece(PieceType.ROOK, Player.GOTE)
        
        # Third row (row 2) - Pawns
        for col in range(9):
            self.board[2][col] = Piece(PieceType.PAWN, Player.GOTE)
        
        # Place Sente pieces (bottom, rows 6-8)
        # Seventh row (row 6) - Pawns
        for col in range(9):
            self.board[6][col] = Piece(PieceType.PAWN, Player.SENTE)
        
        # Eighth row (row 7) - Rook and Bishop
        self.board[7][1] = Piece(PieceType.ROOK, Player.SENTE)
        self.board[7][7] = Piece(PieceType.BISHOP, Player.SENTE)
        
        # Ninth row (row 8) - Back row
        self.board[8][0] = Piece(PieceType.LANCE, Player.SENTE)
        self.board[8][1] = Piece(PieceType.KNIGHT, Player.SENTE)
        self.board[8][2] = Piece(PieceType.SILVER, Player.SENTE)
        self.board[8][3] = Piece(PieceType.GOLD, Player.SENTE)
        self.board[8][4] = Piece(PieceType.KING, Player.SENTE)
        self.board[8][5] = Piece(PieceType.GOLD, Player.SENTE)
        self.board[8][6] = Piece(PieceType.SILVER, Player.SENTE)
        self.board[8][7] = Piece(PieceType.KNIGHT, Player.SENTE)
        self.board[8][8] = Piece(PieceType.LANCE, Player.SENTE)
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get piece at the specified position."""
        if 0 <= row < 9 and 0 <= col < 9:
            return self.board[row][col]
        return None
    
    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        """Set piece at the specified position."""
        if 0 <= row < 9 and 0 <= col < 9:
            self.board[row][col] = piece
    
    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int, promote: bool = False) -> Dict:
        """Move a piece from one position to another."""
        piece = self.get_piece(from_row, from_col)
        if not piece:
            return {'success': False, 'error': 'No piece at source position'}
        
        if piece.player != self.current_player:
            return {'success': False, 'error': 'Not your piece'}
        
        # Check if move is legal
        legal_moves = piece.get_moves(from_row, from_col, self)
        if (to_row, to_col) not in legal_moves:
            return {'success': False, 'error': 'Illegal move'}
        
        # Check promotion
        if promote and not piece.can_promote(from_row, to_row):
            return {'success': False, 'error': 'Cannot promote this piece'}
        
        if piece.must_promote(to_row) and not promote:
            return {'success': False, 'error': 'Must promote this piece'}
        
        # Capture piece if present
        captured_piece = self.get_piece(to_row, to_col)
        if captured_piece:
            # Convert promoted pieces back to original type when captured
            if captured_piece.promoted:
                original_type = self._get_original_type(captured_piece.piece_type)
                captured_piece.piece_type = original_type
                captured_piece.promoted = False
            
            # Change ownership
            captured_piece.player = self.current_player
            self.captured[self.current_player].append(captured_piece)
        
        # Promote piece if requested
        if promote:
            piece.promoted = True
            piece.piece_type = self._get_promoted_type(piece.piece_type)
        
        # Make the move
        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, None)
        
        # Record move
        move_record = {
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'piece': piece.piece_type.value,
            'captured': captured_piece.piece_type.value if captured_piece else None,
            'promoted': promote,
            'player': self.current_player.value
        }
        self.move_history.append(move_record)
        
        # Switch players
        self.current_player = Player.GOTE if self.current_player == Player.SENTE else Player.SENTE
        
        return {'success': True, 'move': move_record}
    
    def drop_piece(self, piece_type: str, row: int, col: int) -> Dict:
        """Drop a captured piece onto the board."""
        # Check if position is empty
        if self.get_piece(row, col) is not None:
            return {'success': False, 'error': 'Position is not empty'}
        
        # Find piece in captured pieces
        piece_type_enum = PieceType(piece_type)
        captured_pieces = self.captured[self.current_player]
        
        piece_to_drop = None
        for i, piece in enumerate(captured_pieces):
            if piece.piece_type == piece_type_enum:
                piece_to_drop = captured_pieces.pop(i)
                break
        
        if not piece_to_drop:
            return {'success': False, 'error': 'Piece not available for drop'}
        
        # Check drop restrictions
        if not self._is_valid_drop(piece_type_enum, row, col):
            # Put piece back
            captured_pieces.append(piece_to_drop)
            return {'success': False, 'error': 'Invalid drop position'}
        
        # Place piece
        self.set_piece(row, col, piece_to_drop)
        
        # Record move
        move_record = {
            'type': 'drop',
            'piece_type': piece_type,
            'to': (row, col),
            'player': self.current_player.value
        }
        self.move_history.append(move_record)
        
        # Switch players
        self.current_player = Player.GOTE if self.current_player == Player.SENTE else Player.SENTE
        
        return {'success': True, 'move': move_record}
    
    def _is_valid_drop(self, piece_type: PieceType, row: int, col: int) -> bool:
        """Check if piece drop is valid."""
        # Pawns cannot be dropped in files that already have a pawn
        if piece_type == PieceType.PAWN:
            for r in range(9):
                piece = self.get_piece(r, col)
                if (piece and piece.piece_type == PieceType.PAWN and 
                    piece.player == self.current_player and not piece.promoted):
                    return False
        
        # Pieces cannot be dropped where they cannot move
        if piece_type == PieceType.PAWN:
            if self.current_player == Player.SENTE and row == 0:
                return False
            if self.current_player == Player.GOTE and row == 8:
                return False
        
        if piece_type == PieceType.LANCE:
            if self.current_player == Player.SENTE and row == 0:
                return False
            if self.current_player == Player.GOTE and row == 8:
                return False
        
        if piece_type == PieceType.KNIGHT:
            if self.current_player == Player.SENTE and row <= 1:
                return False
            if self.current_player == Player.GOTE and row >= 7:
                return False
        
        return True
    
    def _get_promoted_type(self, piece_type: PieceType) -> PieceType:
        """Get the promoted version of a piece type."""
        promotion_map = {
            PieceType.ROOK: PieceType.PROMOTED_ROOK,
            PieceType.BISHOP: PieceType.PROMOTED_BISHOP,
            PieceType.SILVER: PieceType.PROMOTED_SILVER,
            PieceType.KNIGHT: PieceType.PROMOTED_KNIGHT,
            PieceType.LANCE: PieceType.PROMOTED_LANCE,
            PieceType.PAWN: PieceType.PROMOTED_PAWN
        }
        return promotion_map.get(piece_type, piece_type)
    
    def _get_original_type(self, piece_type: PieceType) -> PieceType:
        """Get the original version of a promoted piece type."""
        demotion_map = {
            PieceType.PROMOTED_ROOK: PieceType.ROOK,
            PieceType.PROMOTED_BISHOP: PieceType.BISHOP,
            PieceType.PROMOTED_SILVER: PieceType.SILVER,
            PieceType.PROMOTED_KNIGHT: PieceType.KNIGHT,
            PieceType.PROMOTED_LANCE: PieceType.LANCE,
            PieceType.PROMOTED_PAWN: PieceType.PAWN
        }
        return demotion_map.get(piece_type, piece_type)
    
    def is_in_check(self, player: Player) -> bool:
        """Check if the specified player's king is in check."""
        # Find the king
        king_pos = None
        for row in range(9):
            for col in range(9):
                piece = self.get_piece(row, col)
                if piece and piece.piece_type == PieceType.KING and piece.player == player:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False  # No king found
        
        # Check if any opponent piece can attack the king
        opponent = Player.GOTE if player == Player.SENTE else Player.SENTE
        for row in range(9):
            for col in range(9):
                piece = self.get_piece(row, col)
                if piece and piece.player == opponent:
                    moves = piece.get_moves(row, col, self)
                    if king_pos in moves:
                        return True
        
        return False
    
    def is_checkmate(self, player: Player) -> bool:
        """Check if the specified player is in checkmate."""
        if not self.is_in_check(player):
            return False
        
        # Try all possible moves to see if any can escape check
        for row in range(9):
            for col in range(9):
                piece = self.get_piece(row, col)
                if piece and piece.player == player:
                    moves = piece.get_moves(row, col, self)
                    for move_row, move_col in moves:
                        # Try the move
                        original_piece = self.get_piece(move_row, move_col)
                        self.set_piece(move_row, move_col, piece)
                        self.set_piece(row, col, None)
                        
                        # Check if still in check
                        still_in_check = self.is_in_check(player)
                        
                        # Restore board
                        self.set_piece(row, col, piece)
                        self.set_piece(move_row, move_col, original_piece)
                        
                        if not still_in_check:
                            return False  # Found a move that escapes check
        
        # Try dropping pieces
        for piece_type in [PieceType.PAWN, PieceType.LANCE, PieceType.KNIGHT, 
                          PieceType.SILVER, PieceType.GOLD, PieceType.BISHOP, PieceType.ROOK]:
            if any(p.piece_type == piece_type for p in self.captured[player]):
                for row in range(9):
                    for col in range(9):
                        if self.get_piece(row, col) is None and self._is_valid_drop(piece_type, row, col):
                            # Try the drop
                            temp_piece = Piece(piece_type, player)
                            self.set_piece(row, col, temp_piece)
                            
                            # Check if still in check
                            still_in_check = self.is_in_check(player)
                            
                            # Restore board
                            self.set_piece(row, col, None)
                            
                            if not still_in_check:
                                return False  # Found a drop that escapes check
        
        return True  # No moves can escape check
    
    def get_all_legal_moves(self, player: Player) -> List[Dict]:
        """Get all legal moves for a player."""
        moves = []
        
        # Regular moves
        for row in range(9):
            for col in range(9):
                piece = self.get_piece(row, col)
                if piece and piece.player == player:
                    legal_moves = piece.get_moves(row, col, self)
                    for move_row, move_col in legal_moves:
                        move = {
                            'type': 'move',
                            'from': (row, col),
                            'to': (move_row, move_col),
                            'piece': piece
                        }
                        moves.append(move)
        
        # Drop moves
        for piece_type in [PieceType.PAWN, PieceType.LANCE, PieceType.KNIGHT, 
                          PieceType.SILVER, PieceType.GOLD, PieceType.BISHOP, PieceType.ROOK]:
            if any(p.piece_type == piece_type for p in self.captured[player]):
                for row in range(9):
                    for col in range(9):
                        if self.get_piece(row, col) is None and self._is_valid_drop(piece_type, row, col):
                            move = {
                                'type': 'drop',
                                'piece_type': piece_type,
                                'to': (row, col)
                            }
                            moves.append(move)
        
        return moves
    
    def to_dict(self) -> Dict:
        """Convert board to dictionary representation."""
        board_dict = []
        for row in range(9):
            row_dict = []
            for col in range(9):
                piece = self.get_piece(row, col)
                if piece:
                    row_dict.append(piece.to_dict())
                else:
                    row_dict.append(None)
            board_dict.append(row_dict)
        
        captured_dict = {}
        for player in [Player.SENTE, Player.GOTE]:
            captured_dict[player.value] = [piece.to_dict() for piece in self.captured[player]]
        
        return {
            'board': board_dict,
            'captured': captured_dict,
            'current_player': self.current_player.value,
            'in_check': {
                'sente': self.is_in_check(Player.SENTE),
                'gote': self.is_in_check(Player.GOTE)
            },
            'checkmate': {
                'sente': self.is_checkmate(Player.SENTE),
                'gote': self.is_checkmate(Player.GOTE)
            }
        }

