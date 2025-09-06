/**
 * Main application initialization and setup
 */

class ShogiApp {
    constructor() {
        this.game = null;
        this.init();
    }

    async init() {
        console.log('Initializing mike...');
        
        // Check if backend is available
        try {
            await shogiAPI.healthCheck();
            console.log('Backend connection successful');
        } catch (error) {
            console.error('Backend connection failed:', error);
            this.showConnectionError();
            return;
        }

        // Initialize game
        this.game = new ShogiGame();
        
        // Start a new game automatically
        await this.game.startNewGame();
        
        console.log('mike initialized successfully');
    }

    showConnectionError() {
        const gameMessage = document.getElementById('game-message');
        gameMessage.textContent = 'Cannot connect to backend server. Please make sure the server is running on localhost:5000';
        gameMessage.style.color = '#f44336';
        
        // Disable all game controls
        const buttons = document.querySelectorAll('button');
        buttons.forEach(btn => btn.disabled = true);
        
        const select = document.getElementById('difficulty-select');
        select.disabled = true;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.shogiApp = new ShogiApp();
});

// Add some global utility functions
window.utils = {
    // Convert position to algebraic notation
    positionToAlgebraic: (row, col) => {
        const files = ['9', '8', '7', '6', '5', '4', '3', '2', '1'];
        const ranks = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'];
        return files[col] + ranks[row];
    },
    
    // Convert algebraic notation to position
    algebraicToPosition: (notation) => {
        const files = ['9', '8', '7', '6', '5', '4', '3', '2', '1'];
        const ranks = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'];
        
        const file = notation[0];
        const rank = notation[1];
        
        const col = files.indexOf(file);
        const row = ranks.indexOf(rank);
        
        return [row, col];
    },
    
    // Format move for display
    formatMove: (move) => {
        if (move.type === 'move') {
            const from = utils.positionToAlgebraic(move.from[0], move.from[1]);
            const to = utils.positionToAlgebraic(move.to[0], move.to[1]);
            return `${from}-${to}${move.promote ? '+' : ''}`;
        } else if (move.type === 'drop') {
            const to = utils.positionToAlgebraic(move.to[0], move.to[1]);
            return `${move.piece_type}*${to}`;
        }
        return 'Unknown move';
    }
};

