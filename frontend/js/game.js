/**
 * Game logic and state management for Shogi Bot AI
 */

class ShogiGame {
    constructor() {
        this.gameId = null;
        this.gameState = null;
        this.board = new ShogiBoard('shogi-board');
        this.difficulty = 'medium';
        this.isPlayerTurn = true;
        this.gameOver = false;
        
        // Bind event handlers
        this.board.onSquareClick = this.handleSquareClick.bind(this);
        this.board.onCapturedPieceClick = this.handleCapturedPieceClick.bind(this);
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // New game button
        document.getElementById('new-game-btn').addEventListener('click', () => {
            this.startNewGame();
        });

        // Difficulty selector
        document.getElementById('difficulty-select').addEventListener('change', (e) => {
            this.changeDifficulty(e.target.value);
        });

        // AI move button
        document.getElementById('ai-move-btn').addEventListener('click', () => {
            this.makeAIMove();
        });

        // Suggest move button
        document.getElementById('suggest-move-btn').addEventListener('click', () => {
            this.suggestMove();
        });

        // Analysis button
        document.getElementById('analysis-btn').addEventListener('click', () => {
            this.showAnalysis();
        });

        // Close analysis panel
        document.getElementById('close-analysis').addEventListener('click', () => {
            this.hideAnalysis();
        });
    }

    async startNewGame() {
        try {
            this.showLoading('Starting new game...');
            
            const response = await shogiAPI.createNewGame(this.difficulty);
            this.gameId = response.game_id;
            this.gameState = response.game_state;
            this.gameOver = false;
            this.isPlayerTurn = true;
            
            this.updateDisplay();
            this.hideLoading();
            
            console.log('New game started:', this.gameId);
        } catch (error) {
            this.hideLoading();
            this.showError('Failed to start new game: ' + error.message);
        }
    }

    async changeDifficulty(newDifficulty) {
        this.difficulty = newDifficulty;
        
        if (this.gameId) {
            try {
                await shogiAPI.setDifficulty(this.gameId, newDifficulty);
                console.log('Difficulty changed to:', newDifficulty);
            } catch (error) {
                console.error('Failed to change difficulty:', error);
            }
        }
    }

    async handleSquareClick(row, col, event) {
        if (this.gameOver || !this.isPlayerTurn) return;

        // If we have a captured piece selected, try to drop it
        if (this.board.selectedCapturedPiece) {
            await this.handleDrop(row, col);
            return;
        }

        // If clicking on a legal move, make the move
        if (this.board.selectedSquare && this.board.isLegalMove(row, col)) {
            await this.makeMove(this.board.selectedSquare.row, this.board.selectedSquare.col, row, col);
            return;
        }

        // If clicking on our own piece, select it
        const piece = this.gameState.board[row][col];
        if (piece && piece.player === this.gameState.current_player) {
            await this.selectPiece(row, col);
            return;
        }

        // Otherwise, clear selection
        this.board.clearAllSelection();
    }

    async handleCapturedPieceClick(pieceType, player, event) {
        if (this.gameOver || !this.isPlayerTurn) return;
        if (player !== this.gameState.current_player) return;

        try {
            // Get valid drop positions
            const response = await shogiAPI.getDropPositions(this.gameId, pieceType);
            
            this.board.clearAllSelection();
            this.board.selectCapturedPiece(pieceType, player);
            this.board.showLegalMoves(response.drop_positions);
            
        } catch (error) {
            console.error('Failed to get drop positions:', error);
        }
    }

    async selectPiece(row, col) {
        try {
            const response = await shogiAPI.getLegalMoves(this.gameId, [row, col]);
            
            this.board.clearAllSelection();
            this.board.selectSquare(row, col);
            this.board.showLegalMoves(response.legal_moves);
            
        } catch (error) {
            console.error('Failed to get legal moves:', error);
        }
    }

    async makeMove(fromRow, fromCol, toRow, toCol, promote = false) {
        try {
            this.showLoading('Making move...');
            
            const response = await shogiAPI.makeMove(this.gameId, [fromRow, fromCol], [toRow, toCol], promote);
            
            if (response.success) {
                this.gameState = response.game_state;
                this.board.clearAllSelection();
                this.updateDisplay();
                
                if (response.game_over) {
                    this.handleGameOver(response.winner, response.reason);
                } else {
                    this.isPlayerTurn = false;
                    // Auto-play AI move after a short delay
                    setTimeout(() => this.makeAIMove(), 1000);
                }
            }
            
            this.hideLoading();
        } catch (error) {
            this.hideLoading();
            this.showError('Invalid move: ' + error.message);
        }
    }

    async handleDrop(row, col) {
        if (!this.board.selectedCapturedPiece) return;
        
        const { pieceType } = this.board.selectedCapturedPiece;
        
        try {
            this.showLoading('Dropping piece...');
            
            const response = await shogiAPI.dropPiece(this.gameId, pieceType, [row, col]);
            
            if (response.success) {
                this.gameState = response.game_state;
                this.board.clearAllSelection();
                this.updateDisplay();
                
                if (response.game_over) {
                    this.handleGameOver(response.winner, response.reason);
                } else {
                    this.isPlayerTurn = false;
                    // Auto-play AI move after a short delay
                    setTimeout(() => this.makeAIMove(), 1000);
                }
            }
            
            this.hideLoading();
        } catch (error) {
            this.hideLoading();
            this.showError('Invalid drop: ' + error.message);
        }
    }

    async makeAIMove() {
        if (this.gameOver || this.isPlayerTurn) return;

        try {
            this.showLoading('AI is thinking...');
            
            const response = await shogiAPI.getAIMove(this.gameId);
            
            if (response.success) {
                this.gameState = response.game_state;
                this.updateDisplay();
                
                if (response.game_over) {
                    this.handleGameOver(response.winner, response.reason);
                } else {
                    this.isPlayerTurn = true;
                }
            }
            
            this.hideLoading();
        } catch (error) {
            this.hideLoading();
            this.showError('AI move failed: ' + error.message);
            this.isPlayerTurn = true; // Allow player to continue
        }
    }

    async suggestMove() {
        if (this.gameOver || !this.gameId) return;

        try {
            this.showLoading('Getting move suggestion...');
            
            const response = await shogiAPI.suggestMove(this.gameId);
            
            if (response.move) {
                const move = response.move;
                let suggestion = '';
                
                if (move.type === 'move') {
                    const [fromRow, fromCol] = move.from;
                    const [toRow, toCol] = move.to;
                    suggestion = `Move from (${fromRow},${fromCol}) to (${toRow},${toCol})`;
                    if (move.promote) {
                        suggestion += ' with promotion';
                    }
                } else if (move.type === 'drop') {
                    const [toRow, toCol] = move.to;
                    suggestion = `Drop ${move.piece_type.value} at (${toRow},${toCol})`;
                }
                
                this.showMessage(`Suggested move: ${suggestion}`, 'info');
            }
            
            this.hideLoading();
        } catch (error) {
            this.hideLoading();
            this.showError('Failed to get suggestion: ' + error.message);
        }
    }

    async showAnalysis() {
        if (!this.gameId) return;

        try {
            const response = await shogiAPI.getAnalysis(this.gameId);
            
            document.getElementById('material-balance').textContent = response.material_balance;
            document.getElementById('position-score').textContent = response.position_score;
            document.getElementById('king-safety').textContent = response.king_safety;
            document.getElementById('mobility').textContent = response.mobility;
            document.getElementById('total-evaluation').textContent = response.total_evaluation;
            
            document.getElementById('analysis-panel').classList.remove('hidden');
        } catch (error) {
            this.showError('Failed to get analysis: ' + error.message);
        }
    }

    hideAnalysis() {
        document.getElementById('analysis-panel').classList.add('hidden');
    }

    updateDisplay() {
        if (!this.gameState) return;

        // Update board
        this.board.updateBoard(this.gameState);

        // Update current player indicator
        const currentPlayerElement = document.getElementById('current-player');
        currentPlayerElement.textContent = this.gameState.current_player.toUpperCase();
        currentPlayerElement.className = `player-indicator ${this.gameState.current_player}`;

        // Update game message
        const gameMessageElement = document.getElementById('game-message');
        if (this.gameState.checkmate.sente) {
            gameMessageElement.textContent = 'GOTE wins by checkmate!';
        } else if (this.gameState.checkmate.gote) {
            gameMessageElement.textContent = 'SENTE wins by checkmate!';
        } else if (this.gameState.in_check.sente) {
            gameMessageElement.textContent = 'SENTE is in check!';
        } else if (this.gameState.in_check.gote) {
            gameMessageElement.textContent = 'GOTE is in check!';
        } else {
            gameMessageElement.textContent = 'Game in progress';
        }

        // Update button states
        this.updateButtonStates();
    }

    updateButtonStates() {
        const aiMoveBtn = document.getElementById('ai-move-btn');
        const suggestBtn = document.getElementById('suggest-move-btn');
        const analysisBtn = document.getElementById('analysis-btn');

        if (this.gameOver) {
            aiMoveBtn.disabled = true;
            suggestBtn.disabled = true;
        } else {
            aiMoveBtn.disabled = this.isPlayerTurn;
            suggestBtn.disabled = false;
        }
        
        analysisBtn.disabled = !this.gameId;
    }

    handleGameOver(winner, reason) {
        this.gameOver = true;
        this.isPlayerTurn = false;
        
        const winnerText = winner === 'sente' ? 'SENTE' : 'GOTE';
        const message = `Game Over! ${winnerText} wins by ${reason}!`;
        
        this.showMessage(message, 'success');
        this.updateButtonStates();
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        const text = overlay.querySelector('.loading-text');
        text.textContent = message;
        overlay.classList.remove('hidden');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.add('hidden');
    }

    showMessage(message, type = 'info') {
        // Simple message display - could be enhanced with a proper notification system
        const gameMessage = document.getElementById('game-message');
        const originalText = gameMessage.textContent;
        
        gameMessage.textContent = message;
        gameMessage.style.color = type === 'error' ? '#f44336' : type === 'success' ? '#4caf50' : '#333';
        
        setTimeout(() => {
            gameMessage.textContent = originalText;
            gameMessage.style.color = '#333';
        }, 3000);
    }

    showError(message) {
        this.showMessage(message, 'error');
        console.error(message);
    }
}

