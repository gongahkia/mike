/**
 * API communication layer for Shogi Bot AI
 */

class ShogiAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Health check
    async healthCheck() {
        return this.request('/api/health');
    }

    // Game management
    async createNewGame(difficulty = 'medium') {
        return this.request('/api/game/new', {
            method: 'POST',
            body: JSON.stringify({ difficulty })
        });
    }

    async getGameState(gameId) {
        return this.request(`/api/game/${gameId}/state`);
    }

    async deleteGame(gameId) {
        return this.request(`/api/game/${gameId}`, {
            method: 'DELETE'
        });
    }

    // Move operations
    async makeMove(gameId, from, to, promote = false) {
        return this.request(`/api/game/${gameId}/move`, {
            method: 'POST',
            body: JSON.stringify({ from, to, promote })
        });
    }

    async dropPiece(gameId, pieceType, to) {
        return this.request(`/api/game/${gameId}/move`, {
            method: 'POST',
            body: JSON.stringify({ drop: pieceType, to })
        });
    }

    async getLegalMoves(gameId, position) {
        return this.request(`/api/game/${gameId}/legal-moves`, {
            method: 'POST',
            body: JSON.stringify({ position })
        });
    }

    async getDropPositions(gameId, pieceType) {
        return this.request(`/api/game/${gameId}/drop-positions`, {
            method: 'POST',
            body: JSON.stringify({ piece_type: pieceType })
        });
    }

    // AI operations
    async getAIMove(gameId) {
        return this.request(`/api/game/${gameId}/ai-move`, {
            method: 'POST'
        });
    }

    async suggestMove(gameId) {
        return this.request(`/api/game/${gameId}/suggest`);
    }

    async getAnalysis(gameId) {
        return this.request(`/api/game/${gameId}/analysis`);
    }

    async setDifficulty(gameId, difficulty) {
        return this.request(`/api/game/${gameId}/difficulty`, {
            method: 'POST',
            body: JSON.stringify({ difficulty })
        });
    }

    // Game history
    async getMoveHistory(gameId) {
        return this.request(`/api/game/${gameId}/history`);
    }

    async listGames() {
        return this.request('/api/games');
    }
}

// Create global API instance
window.shogiAPI = new ShogiAPI();

