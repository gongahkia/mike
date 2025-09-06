"""
Position evaluation functions for Shogi AI.
"""

from typing import Dict
from game.pieces import Piece, PieceType, Player
from game.board import ShogiBoard


class PositionEvaluator:
    def __init__(self):
        # Piece values (in centipawns)
        self.piece_values = {
            PieceType.KING: 0,  # King has no material value
            PieceType.ROOK: 900,
            PieceType.BISHOP: 700,
            PieceType.GOLD: 600,
            PieceType.SILVER: 500,
            PieceType.KNIGHT: 400,
            PieceType.LANCE: 300,
            PieceType.PAWN: 100,
            PieceType.PROMOTED_ROOK: 1200,
            PieceType.PROMOTED_BISHOP: 1000,
            PieceType.PROMOTED_SILVER: 700,
            PieceType.PROMOTED_KNIGHT: 700,
            PieceType.PROMOTED_LANCE: 700,
            PieceType.PROMOTED_PAWN: 700
        }
        
        # Position bonuses for pieces (encourages development)
        self.position_bonuses = {
            PieceType.PAWN: [
                [0,  0,  0,  0,  0,  0,  0,  0,  0],
                [5,  5,  5,  5,  5,  5,  5,  5,  5],
                [10, 10, 10, 15, 15, 15, 10, 10, 10],
                [15, 15, 20, 25, 25, 25, 20, 15, 15],
                [20, 20, 25, 30, 30, 30, 25, 20, 20],
                [25, 25, 30, 35, 35, 35, 30, 25, 25],
                [30, 30, 35, 40, 40, 40, 35, 30, 30],
                [35, 35, 40, 45, 45, 45, 40, 35, 35],
                [0,  0,  0,  0,  0,  0,  0,  0,  0]
            ],
            PieceType.KNIGHT: [
                [-50, -40, -30, -30, -30, -30, -30, -40, -50],
                [-40, -20,   0,   0,   0,   0,   0, -20, -40],
                [-30,   0,  10,  15,  15,  15,  10,   0, -30],
                [-30,   5,  15,  20,  20,  20,  15,   5, -30],
                [-30,   0,  15,  20,  20,  20,  15,   0, -30],
                [-30,   5,  10,  15,  15,  15,  10,   5, -30],
                [-40, -20,   0,   5,   5,   5,   0, -20, -40],
                [-50, -40, -30, -30, -30, -30, -30, -40, -50],
                [-50, -40, -30, -30, -30, -30, -30, -40, -50]
            ]
        }
    
    def evaluate_material(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate material balance."""
        score = 0
        
        # Count pieces on board
        for row in range(9):
            for col in range(9):
                piece = board.get_piece(row, col)
                if piece:
                    value = self.piece_values[piece.piece_type]
                    if piece.player == player:
                        score += value
                    else:
                        score -= value
        
        # Count captured pieces (pieces in hand are more valuable)
        for piece in board.captured_pieces[player]:
            score += self.piece_values[piece.piece_type] * 1.2  # 20% bonus for pieces in hand
        
        for piece in board.captured_pieces[player.opponent()]:
            score -= self.piece_values[piece.piece_type] * 1.2
        
        return score
    
    def evaluate_position(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate positional factors."""
        score = 0
        
        for row in range(9):
            for col in range(9):
                piece = board.get_piece(row, col)
                if piece and piece.piece_type in self.position_bonuses:
                    bonus_table = self.position_bonuses[piece.piece_type]
                    # Flip table for GOTE pieces
                    if piece.player == Player.GOTE:
                        bonus = bonus_table[8 - row][col]
                    else:
                        bonus = bonus_table[row][col]
                    
                    if piece.player == player:
                        score += bonus
                    else:
                        score -= bonus
        
        return score
    
    def evaluate_king_safety(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate king safety."""
        score = 0
        king_pos = board.find_king(player)
        opponent_king_pos = board.find_king(player.opponent())
        
        if not king_pos or not opponent_king_pos:
            return 0
        
        # Penalty for exposed king
        king_row, king_col = king_pos
        
        # Count pieces around king
        friendly_pieces = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = king_row + dr, king_col + dc
                if board.is_valid_position(r, c):
                    piece = board.get_piece(r, c)
                    if piece and piece.player == player:
                        friendly_pieces += 1
        
        score += friendly_pieces * 10
        
        # Penalty for king in center
        if 2 <= king_row <= 6 and 2 <= king_col <= 6:
            score -= 50
        
        return score
    
    def evaluate_mobility(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate piece mobility."""
        score = 0
        
        # Count legal moves
        player_moves = len(board.get_all_legal_moves(player))
        opponent_moves = len(board.get_all_legal_moves(player.opponent()))
        
        score += (player_moves - opponent_moves) * 2
        
        return score
    
    def evaluate_threats(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate threats and attacks."""
        score = 0
        
        # Check if opponent king is in check
        if board.is_in_check(player.opponent()):
            score += 50
        
        # Check if our king is in check
        if board.is_in_check(player):
            score -= 50
        
        return score
    
    def evaluate_promotion_potential(self, board: ShogiBoard, player: Player) -> int:
        """Evaluate pieces that can promote."""
        score = 0
        
        for row in range(9):
            for col in range(9):
                piece = board.get_piece(row, col)
                if piece and piece.player == player and piece.can_promote():
                    # Check if piece is in or near promotion zone
                    if player == Player.SENTE and row <= 3:
                        score += 20
                    elif player == Player.GOTE and row >= 5:
                        score += 20
        
        return score
    
    def evaluate_position_full(self, board: ShogiBoard, player: Player) -> int:
        """Full position evaluation combining all factors."""
        if board.is_checkmate(player):
            return -10000
        if board.is_checkmate(player.opponent()):
            return 10000
        
        score = 0
        
        # Material evaluation (most important)
        score += self.evaluate_material(board, player)
        
        # Positional factors
        score += self.evaluate_position(board, player)
        score += self.evaluate_king_safety(board, player)
        score += self.evaluate_mobility(board, player)
        score += self.evaluate_threats(board, player)
        score += self.evaluate_promotion_potential(board, player)
        
        return score

