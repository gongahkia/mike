"""
Shogi board representation and game state management.
"""

from typing import List, Optional, Dict, Tuple
from backend.game.pieces import Piece, PieceType, Player


class ShogiBoard:
    def __init__(self):
        self.board = [[None for _ in range(9)] for _ in range(9)]
        self.captured_pieces = {Player.SENTE: [], Player.GOTE: []}
        self.current_player = Player.SENTE
        self.move_history = []
        self.setup_initial_position()
    
    def setup_initial_position(self):
        """Set up the initial shogi board position."""
        # Clear the board
        self.board = [[None for _ in range(9)] for _ in range(9)]
        
        # GOTE pieces (top, rows 0-2)
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
        
        # Second row (row 1) - Bishop and Rook
        self.board[1][1] = Piece(PieceType.BISHOP, Player.GOTE)
        self.board[1][7] = Piece(PieceType.ROOK, Player.GOTE)
        
        # Third row (row 2) - Pawns
        for col in range(9):
            self.board[2][col] = Piece(PieceType.PAWN, Player.GOTE)
        
        # SENTE pieces (bottom, rows 6-8)
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
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if the given position is valid on the board."""
        return 0 <= row < 9 and 0 <= col < 9
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get the piece at the given position."""
        if not self.is_valid_position(row, col):
            return None
        return self.board[row][col]
    
    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        """Set a piece at the given position."""
        if self.is_valid_position(row, col):
            self.board[row][col] = piece
    
    def find_king(self, player: Player) -> Optional[Tuple[int, int]]:
        """Find the position of the king for the given player."""
        for row in range(9):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece.piece_type == PieceType.KING and piece.player == player:
                    return (row, col)
        return None
    
    def is_in_check(self, player: Player) -> bool:
        """Check if the given player's king is in check."""
        king_pos = self.find_king(player)
        if not king_pos:
            return False
        
        king_row, king_col = king_pos
        opponent = player.opponent()
        
        # Check if any opponent piece can attack the king
        for row in range(9):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece.player == opponent:
                    moves = piece.get_moves(row, col, self)
                    if (king_row, king_col) in moves:
                        return True
        
        return False
    
    def is_checkmate(self, player: Player) -> bool:
        """Check if the given player is in checkmate."""
        if not self.is_in_check(player):
            return False
        
        # Try all possible moves to see if any can escape check
        for row in range(9):
            for col in range(9):
                piece = self.board[row][col]
                if piece and piece.player == player:
                    moves = piece.get_moves(row, col, self)
                    for new_row, new_col in moves:
                        # Try the move
                        original_piece = self.board[new_row][new_col]
                        self.board[new_row][new_col] = piece
                        self.board[row][col] = None
                        
                        # Check if still in check
                        still_in_check = self.is_in_check(player)
                        
                        # Undo the move
                        self.board[row][col] = piece
                        self.board[new_row][new_col] = original_piece
                        
                        if not still_in_check:
                            return False
        
        return True
    
    def can_drop_piece(self, piece_type: PieceType, row: int, col: int, player: Player) -> bool:
        """Check if a piece can be dropped at the given position."""
        # Position must be empty
        if self.board[row][col] is not None:
            return False
        
        # Special rules for pawns
        if piece_type == PieceType.PAWN:
            # Cannot drop pawn in same column as another pawn
            for r in range(9):
                existing_piece = self.board[r][col]
                if (existing_piece and existing_piece.piece_type == PieceType.PAWN and 
                    existing_piece.player == player):
                    return False
            
            # Cannot drop pawn for immediate checkmate (nifu rule)
            # This is a simplified check - full implementation would be more complex
        
        # Cannot drop pieces that cannot move (like pawns on back rank)
        if piece_type == PieceType.PAWN:
            if (player == Player.SENTE and row == 0) or (player == Player.GOTE and row == 8):
                return False
        elif piece_type == PieceType.LANCE:
            if (player == Player.SENTE and row == 0) or (player == Player.GOTE and row == 8):
                return False
        elif piece_type == PieceType.KNIGHT:
            if (player == Player.SENTE and row <= 1) or (player == Player.GOTE and row >= 7):
                return False
        
        return True
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int, 
                  promote: bool = False) -> bool:
        """Make a move on the board. Returns True if successful."""
        piece = self.get_piece(from_row, from_col)
        if not piece or piece.player != self.current_player:
            return False
        
        # Check if the move is valid
        valid_moves = piece.get_moves(from_row, from_col, self)
        if (to_row, to_col) not in valid_moves:
            return False
        
        # Check if move would leave king in check
        captured_piece = self.get_piece(to_row, to_col)
        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, None)
        
        if self.is_in_check(self.current_player):
            # Undo the move
            self.set_piece(from_row, from_col, piece)
            self.set_piece(to_row, to_col, captured_piece)
            return False
        
        # Handle capture
        if captured_piece:
            demoted_piece = captured_piece.demote()
            self.captured_pieces[self.current_player].append(demoted_piece)
        
        # Handle promotion
        if promote and piece.can_promote():
            promoted_piece = piece.promote()
            self.set_piece(to_row, to_col, promoted_piece)
        
        # Record the move
        move = {
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'piece': piece,
            'captured': captured_piece,
            'promoted': promote,
            'player': self.current_player
        }
        self.move_history.append(move)
        
        # Switch players
        self.current_player = self.current_player.opponent()
        
        return True
    
    def drop_piece(self, piece_type: PieceType, row: int, col: int) -> bool:
        """Drop a captured piece onto the board."""
        if not self.can_drop_piece(piece_type, row, col, self.current_player):
            return False
        
        # Find the piece in captured pieces
        captured = self.captured_pieces[self.current_player]
        piece_to_drop = None
        for i, piece in enumerate(captured):
            if piece.piece_type == piece_type:
                piece_to_drop = captured.pop(i)
                break
        
        if not piece_to_drop:
            return False
        
        # Place the piece
        self.set_piece(row, col, piece_to_drop)
        
        # Check if this would leave king in check
        if self.is_in_check(self.current_player):
            # Undo the drop
            self.set_piece(row, col, None)
            self.captured_pieces[self.current_player].append(piece_to_drop)
            return False
        
        # Record the drop
        move = {
            'drop': True,
            'piece_type': piece_type,
            'to': (row, col),
            'player': self.current_player
        }
        self.move_history.append(move)
        
        # Switch players
        self.current_player = self.current_player.opponent()
        
        return True
    
    def get_all_legal_moves(self, player: Player) -> List[Dict]:
        """Get all legal moves for the given player."""
        moves = []
        
        # Regular moves
        for row in range(9):
            for col in range(9):
                piece = self.get_piece(row, col)
                if piece and piece.player == player:
                    valid_moves = piece.get_moves(row, col, self)
                    for to_row, to_col in valid_moves:
                        # Check if move is legal (doesn't leave king in check)
                        captured_piece = self.get_piece(to_row, to_col)
                        self.set_piece(to_row, to_col, piece)
                        self.set_piece(row, col, None)
                        
                        if not self.is_in_check(player):
                            move = {
                                'type': 'move',
                                'from': (row, col),
                                'to': (to_row, to_col),
                                'piece': piece,
                                'promote': False
                            }
                            moves.append(move)
                            
                            # Check for promotion possibility
                            if piece.can_promote():
                                # Check if piece is in promotion zone
                                in_promotion_zone = False
                                if player == Player.SENTE and (row <= 2 or to_row <= 2):
                                    in_promotion_zone = True
                                elif player == Player.GOTE and (row >= 6 or to_row >= 6):
                                    in_promotion_zone = True
                                
                                if in_promotion_zone:
                                    promote_move = move.copy()
                                    promote_move['promote'] = True
                                    moves.append(promote_move)
                        
                        # Undo the move
                        self.set_piece(row, col, piece)
                        self.set_piece(to_row, to_col, captured_piece)
        
        # Drop moves
        for piece in self.captured_pieces[player]:
            for row in range(9):
                for col in range(9):
                    if self.can_drop_piece(piece.piece_type, row, col, player):
                        # Test the drop
                        self.set_piece(row, col, piece)
                        if not self.is_in_check(player):
                            moves.append({
                                'type': 'drop',
                                'piece_type': piece.piece_type,
                                'to': (row, col)
                            })
                        self.set_piece(row, col, None)
        
        return moves
    
    def to_dict(self) -> Dict:
        """Convert board state to dictionary for JSON serialization."""
        board_dict = []
        for row in range(9):
            row_dict = []
            for col in range(9):
                piece = self.board[row][col]
                if piece:
                    row_dict.append({
                        'type': piece.piece_type.value,
                        'player': piece.player.value,
                        'promoted': piece.promoted
                    })
                else:
                    row_dict.append(None)
            board_dict.append(row_dict)
        
        captured_dict = {}
        for player in [Player.SENTE, Player.GOTE]:
            captured_dict[player.value] = []
            for piece in self.captured_pieces[player]:
                captured_dict[player.value].append({
                    'type': piece.piece_type.value,
                    'player': piece.player.value
                })
        
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
    
    def __str__(self) -> str:
        """String representation of the board."""
        result = "  0 1 2 3 4 5 6 7 8\n"
        for row in range(9):
            result += f"{row} "
            for col in range(9):
                piece = self.board[row][col]
                if piece:
                    result += f"{str(piece):>2}"
                else:
                    result += " ."
            result += "\n"
        
        # Show captured pieces
        result += f"\nSENTE captured: {[str(p) for p in self.captured_pieces[Player.SENTE]]}\n"
        result += f"GOTE captured: {[str(p) for p in self.captured_pieces[Player.GOTE]]}\n"
        result += f"Current player: {self.current_player.value}\n"
        
        return result

