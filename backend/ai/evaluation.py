"""
Position evaluation functions for Shogi AI.
"""

from typing import Dict
from game.pieces import Piece, PieceType, Player
from game.board import ShogiBoard


class PositionEvaluator:
    """Evaluates Shogi positions for the AI."""
    
    def __init__(self):
        # Piece values for evaluation
        self.piece_values = {
            PieceType.KING: 0,  # King is invaluable
            PieceType.ROOK: 500,
            PieceType.BISHOP: 450,
            PieceType.GOLD: 400,
            PieceType.SILVER: 350,
            PieceType.KNIGHT: 300,
            PieceType.LANCE: 250,
            PieceType.PAWN: 100,
            PieceType.PROMOTED_ROOK: 600,
            PieceType.PROMOTED_BISHOP: 550,
            PieceType.PROMOTED_SILVER: 450,
            PieceType.PROMOTED_KNIGHT: 400,
            PieceType.PROMOTED_LANCE: 350,
            PieceType.PROMOTED_PAWN: 200
        }
        
        # Position bonuses (encourage central control)
        self.position_bonus = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 5, 5, 5, 5, 5, 5, 5, 0],
            [0, 5, 10, 10, 10, 10, 10, 5, 0],
            [0, 5, 10, 15, 15, 15, 10, 5, 0],
            [0, 5, 10, 15, 20, 15, 10, 5, 0],
            [0, 5, 10, 15, 15, 15, 10, 5, 0],
            [0, 5, 10, 10, 10, 10, 10, 5, 0],
            [0, 5, 5, 5, 5, 5, 5, 5, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
    
    def evaluate_position(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate the current position from the perspective of the given player."""
        score = 0
        
        # Material evaluation
        score += self._evaluate_material(board, player)
        
        # Position evaluation
        score += self._evaluate_position(board, player)
        
        # King safety
        score += self._evaluate_king_safety(board, player)
        
        # Mobility (number of legal moves)
        score += self._evaluate_mobility(board, player)
        
        # Captured pieces (pieces in hand)
        score += self._evaluate_captured_pieces(board, player)
        
        return score
    
    def _evaluate_material(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate material balance."""
        score = 0
        
        for row in range(9):
            for col in range(9):
                piece = board.get_piece(row, col)
                if piece:
                    piece_value = self.piece_values.get(piece.piece_type, 0)
                    if piece.player == player:
                        score += piece_value
                    else:
                        score -= piece_value
        
        return score
    
    def _evaluate_position(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate piece positioning."""
        score = 0
        
        for row in range(9):
            for col in range(9):
                piece = board.get_piece(row, col)
                if piece:
                    position_value = self.position_bonus[row][col]
                    if piece.player == player:
                        score += position_value
                    else:
                        score -= position_value
        
        return score
    
    def _evaluate_king_safety(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate king safety."""
        score = 0
        
        # Find kings
        player_king_pos = None
        opponent_king_pos = None
        opponent = Player.GOTE if player == Player.SENTE else Player.SENTE
        
        for row in range(9):
            for col in range(9):
                piece = board.get_piece(row, col)
                if piece and piece.piece_type == PieceType.KING:
                    if piece.player == player:
                        player_king_pos = (row, col)
                    else:
                        opponent_king_pos = (row, col)
        
        # Penalty for being in check
        if board.is_in_check(player):
            score -= 100
        
        # Bonus for putting opponent in check
        if board.is_in_check(opponent):
            score += 50
        
        # King position evaluation (prefer corners/edges for safety)
        if player_king_pos:
            row, col = player_king_pos
            if player == Player.SENTE:
                # Sente king prefers bottom rows
                if row >= 7:
                    score += 20
                if col in [0, 1, 7, 8]:  # Edge files
                    score += 10
            else:
                # Gote king prefers top rows
                if row <= 1:
                    score += 20
                if col in [0, 1, 7, 8]:  # Edge files
                    score += 10
        
        return score
    
    def _evaluate_mobility(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate piece mobility (number of legal moves)."""
        player_moves = 0
        opponent_moves = 0
        opponent = Player.GOTE if player == Player.SENTE else Player.SENTE
        
        for row in range(9):
            for col in range(9):
                piece = board.get_piece(row, col)
                if piece:
                    moves = len(piece.get_moves(row, col, board))
                    if piece.player == player:
                        player_moves += moves
                    else:
                        opponent_moves += moves
        
        # Each move is worth 1 point
        return player_moves - opponent_moves
    
    def _evaluate_captured_pieces(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate captured pieces (pieces in hand)."""
        score = 0
        opponent = Player.GOTE if player == Player.SENTE else Player.SENTE
        
        # Player's captured pieces (positive)
        for piece in board.captured[player]:
            score += self.piece_values.get(piece.piece_type, 0) // 2
        
        # Opponent's captured pieces (negative)
        for piece in board.captured[opponent]:
            score -= self.piece_values.get(piece.piece_type, 0) // 2
        
        return score
    
    def get_detailed_evaluation(self, board: ShogiBoard, player: Player) -> Dict:
        """Get detailed evaluation breakdown."""
        material = self._evaluate_material(board, player)
        position = self._evaluate_position(board, player)
        king_safety = self._evaluate_king_safety(board, player)
        mobility = self._evaluate_mobility(board, player)
        captured = self._evaluate_captured_pieces(board, player)
        
        total = material + position + king_safety + mobility + captured
        
        return {
            'material_balance': material,
            'position_score': position,
            'king_safety': king_safety,
            'mobility': mobility,
            'captured_pieces': captured,
            'total_evaluation': total,
            'in_check': board.is_in_check(player),
            'checkmate': board.is_checkmate(player)
        }

