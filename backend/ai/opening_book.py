"""
Opening book for Shogi AI to improve early game play.
"""

from typing import Dict, List, Optional, Tuple
from game.board import ShogiBoard
from game.pieces import Player


class OpeningBook:
    """Opening book containing common Shogi opening sequences."""
    
    def __init__(self):
        self.openings = self._initialize_openings()
    
    def _initialize_openings(self) -> Dict[str, List[Dict]]:
        """Initialize common Shogi openings."""
        openings = {}
        
        # Static Rook (Ibisha) openings
        openings['static_rook'] = [
            # P-7f (Pawn to 7f)
            {'from': (6, 6), 'to': (5, 6), 'type': 'move'},
            # P-3d (opponent response)
            # P-2f
            {'from': (6, 7), 'to': (5, 7), 'type': 'move'},
            # G-3b (opponent)
            # S-4h
            {'from': (8, 6), 'to': (7, 5), 'type': 'move'},
        ]
        
        # Ranging Rook (Furibisha) openings
        openings['ranging_rook'] = [
            # P-7f
            {'from': (6, 6), 'to': (5, 6), 'type': 'move'},
            # P-3d (opponent)
            # R-6h (Rook to 6th file)
            {'from': (7, 1), 'to': (7, 3), 'type': 'move'},
        ]
        
        # Central Rook
        openings['central_rook'] = [
            # P-5f
            {'from': (6, 4), 'to': (5, 4), 'type': 'move'},
            # P-5d (opponent)
            # R-5h
            {'from': (7, 1), 'to': (7, 4), 'type': 'move'},
        ]
        
        return openings
    
    def get_opening_move(self, board: ShogiBoard, player: Player) -> Optional[Dict]:
        """Get an opening move if applicable."""
        move_count = len(board.move_history)
        
        # Only use opening book for first few moves
        if move_count > 6:
            return None
        
        # Simple opening book logic
        if move_count == 0 and player == Player.SENTE:
            # First move: P-7f (most common)
            return {'from': (6, 6), 'to': (5, 6), 'type': 'move'}
        
        if move_count == 2 and player == Player.SENTE:
            # Second move: P-2f or R-6h depending on strategy
            import random
            if random.random() < 0.7:
                return {'from': (6, 7), 'to': (5, 7), 'type': 'move'}  # P-2f
            else:
                return {'from': (7, 1), 'to': (7, 3), 'type': 'move'}  # R-6h
        
        # For Gote (second player), respond to Sente's moves
        if move_count == 1 and player == Player.GOTE:
            # Respond to P-7f with P-3d
            last_move = board.move_history[-1]
            if (last_move.get('from') == (6, 6) and last_move.get('to') == (5, 6)):
                return {'from': (2, 2), 'to': (3, 2), 'type': 'move'}  # P-3d
        
        return None
    
    def is_known_position(self, board: ShogiBoard) -> bool:
        """Check if the current position is in the opening book."""
        move_count = len(board.move_history)
        return move_count <= 6
    
    def get_opening_name(self, board: ShogiBoard) -> Optional[str]:
        """Get the name of the current opening if known."""
        if len(board.move_history) < 2:
            return None
        
        # Analyze first few moves to determine opening type
        first_move = board.move_history[0]
        
        if first_move.get('from') == (6, 6) and first_move.get('to') == (5, 6):
            # Started with P-7f
            if len(board.move_history) >= 4:
                third_move = board.move_history[2]
                if third_move.get('from') == (7, 1):  # Rook move
                    return "Ranging Rook"
                else:
                    return "Static Rook"
            return "Standard Opening"
        
        elif first_move.get('from') == (6, 4) and first_move.get('to') == (5, 4):
            return "Central Rook"
        
        return "Non-standard Opening"

