/**
 * Shogi board rendering and interaction logic
 */

class ShogiBoard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.squares = [];
        this.selectedSquare = null;
        this.selectedCapturedPiece = null;
        this.legalMoves = [];
        this.onSquareClick = null;
        this.onCapturedPieceClick = null;
        
        // Piece symbols mapping
        this.pieceSymbols = {
            'king': '王',
            'rook': '飛',
            'bishop': '角',
            'gold': '金',
            'silver': '銀',
            'knight': '桂',
            'lance': '香',
            'pawn': '歩',
            'promoted_rook': '龍',
            'promoted_bishop': '馬',
            'promoted_silver': '全',
            'promoted_knight': '圭',
            'promoted_lance': '杏',
            'promoted_pawn': 'と'
        };
        
        this.initializeBoard();
    }

    initializeBoard() {
        this.container.innerHTML = '';
        this.squares = [];

        // Create 9x9 grid of squares
        for (let row = 0; row < 9; row++) {
            const rowSquares = [];
            for (let col = 0; col < 9; col++) {
                const square = document.createElement('div');
                square.className = 'square';
                square.dataset.row = row;
                square.dataset.col = col;
                
                square.addEventListener('click', (e) => {
                    if (this.onSquareClick) {
                        this.onSquareClick(row, col, e);
                    }
                });

                this.container.appendChild(square);
                rowSquares.push(square);
            }
            this.squares.push(rowSquares);
        }
    }

    updateBoard(gameState) {
        const board = gameState.board;
        
        // Clear all squares
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                const square = this.squares[row][col];
                square.innerHTML = '';
                square.className = 'square';
            }
        }

        // Place pieces
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                const piece = board[row][col];
                if (piece) {
                    this.placePiece(row, col, piece);
                }
            }
        }

        // Update captured pieces
        this.updateCapturedPieces('sente', gameState.captured.sente);
        this.updateCapturedPieces('gote', gameState.captured.gote);
    }

    placePiece(row, col, piece) {
        const square = this.squares[row][col];
        const pieceElement = document.createElement('div');
        pieceElement.className = `piece ${piece.player}`;
        
        if (piece.promoted) {
            pieceElement.classList.add('promoted');
        }
        
        const symbol = this.pieceSymbols[piece.type] || '?';
        pieceElement.textContent = symbol;
        
        square.appendChild(pieceElement);
    }

    updateCapturedPieces(player, capturedPieces) {
        const container = document.getElementById(`${player}-captured`);
        container.innerHTML = '';

        // Group pieces by type and count them
        const pieceCounts = {};
        capturedPieces.forEach(piece => {
            const type = piece.type;
            pieceCounts[type] = (pieceCounts[type] || 0) + 1;
        });

        // Create captured piece elements
        Object.entries(pieceCounts).forEach(([type, count]) => {
            for (let i = 0; i < count; i++) {
                const pieceElement = document.createElement('div');
                pieceElement.className = 'captured-piece';
                pieceElement.dataset.pieceType = type;
                pieceElement.dataset.player = player;
                
                const symbol = this.pieceSymbols[type] || '?';
                pieceElement.textContent = symbol;
                
                pieceElement.addEventListener('click', (e) => {
                    if (this.onCapturedPieceClick) {
                        this.onCapturedPieceClick(type, player, e);
                    }
                });

                container.appendChild(pieceElement);
            }
        });
    }

    selectSquare(row, col) {
        this.clearSelection();
        this.selectedSquare = { row, col };
        this.squares[row][col].classList.add('selected');
    }

    selectCapturedPiece(pieceType, player) {
        this.clearCapturedSelection();
        this.selectedCapturedPiece = { pieceType, player };
        
        // Find and select the first piece of this type
        const capturedContainer = document.getElementById(`${player}-captured`);
        const pieces = capturedContainer.querySelectorAll(`[data-piece-type="${pieceType}"]`);
        if (pieces.length > 0) {
            pieces[0].classList.add('selected');
        }
    }

    clearSelection() {
        if (this.selectedSquare) {
            const { row, col } = this.selectedSquare;
            this.squares[row][col].classList.remove('selected');
            this.selectedSquare = null;
        }
        this.clearLegalMoves();
    }

    clearCapturedSelection() {
        if (this.selectedCapturedPiece) {
            const { player } = this.selectedCapturedPiece;
            const capturedContainer = document.getElementById(`${player}-captured`);
            const selectedPieces = capturedContainer.querySelectorAll('.selected');
            selectedPieces.forEach(piece => piece.classList.remove('selected'));
            this.selectedCapturedPiece = null;
        }
        this.clearLegalMoves();
    }

    clearAllSelection() {
        this.clearSelection();
        this.clearCapturedSelection();
    }

    showLegalMoves(moves) {
        this.clearLegalMoves();
        this.legalMoves = moves;
        
        moves.forEach(([row, col]) => {
            const square = this.squares[row][col];
            square.classList.add('legal-move');
            
            // Check if square is occupied
            if (square.querySelector('.piece')) {
                square.classList.add('occupied');
            }
        });
    }

    clearLegalMoves() {
        this.legalMoves.forEach(([row, col]) => {
            const square = this.squares[row][col];
            square.classList.remove('legal-move', 'occupied');
        });
        this.legalMoves = [];
    }

    isLegalMove(row, col) {
        return this.legalMoves.some(([r, c]) => r === row && c === col);
    }

    highlightSquare(row, col, className = 'highlight') {
        this.squares[row][col].classList.add(className);
    }

    removeHighlight(row, col, className = 'highlight') {
        this.squares[row][col].classList.remove(className);
    }

    animateMove(fromRow, fromCol, toRow, toCol) {
        // Simple animation - could be enhanced with CSS transitions
        const fromSquare = this.squares[fromRow][fromCol];
        const toSquare = this.squares[toRow][toCol];
        
        // Add animation class
        fromSquare.classList.add('moving');
        
        setTimeout(() => {
            fromSquare.classList.remove('moving');
        }, 300);
    }

    getPieceAt(row, col) {
        const square = this.squares[row][col];
        const pieceElement = square.querySelector('.piece');
        
        if (!pieceElement) return null;
        
        return {
            player: pieceElement.classList.contains('sente') ? 'sente' : 'gote',
            promoted: pieceElement.classList.contains('promoted')
        };
    }

    // Utility methods
    getSquareElement(row, col) {
        return this.squares[row][col];
    }

    forEachSquare(callback) {
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                callback(row, col, this.squares[row][col]);
            }
        }
    }
}

