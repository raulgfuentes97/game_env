import numpy as np
from core.base_game import BaseGame

class TicTacToeGame(BaseGame):
    def __init__(self, num_players=2):
        super().__init__()
        self.num_players = num_players
        self.reset()

    def reset(self):
        self.board = np.zeros((3, 3), dtype=int)
        self.current_player = 0
        self.history = []
        self.done = False

    def get_state(self, player_index=None):
        """
        Devuelve el estado del juego desde la perspectiva del jugador:
          - board: tablero con 1 = mis fichas, -1 = oponentes, 0 = vacío
          - player_id: índice del jugador actual
        """
        if player_index is None:
            player_index = self.current_player

        normalized = np.zeros_like(self.board)
        normalized[self.board == player_index + 1] = 1
        normalized[(self.board != 0) & (self.board != player_index + 1)] = -1

        return {
            "board": normalized.copy(),
            "player_id": player_index
        }

    def valid_actions(self, player_index=None):
        """Acciones válidas: cualquier casilla vacía."""
        return [(i, j) for i in range(3) for j in range(3) if self.board[i, j] == 0]

    def get_current_players(self):
        """Devuelve qué jugadores deben actuar en este turno."""
        return [] if self.done else [self.current_player]

    def step(self, player_actions):
        """
        player_actions: lista de (player_index, action)
        """
        for player_index, action in player_actions:
            i, j = action
            if self.board[i, j] != 0:
                raise ValueError("Invalid move")

            # player_index + 1 => visible en tablero como (1,2,...)
            self.board[i, j] = player_index + 1
            self.history.append((player_index, action))

        self.done = self.is_terminal()

        # Recompensas
        reward = [0] * self.num_players
        if self.done:
            winner = self.get_winner()
            if winner is not None:
                reward[winner] = 1

        # Siguiente jugador
        self.current_player = (self.current_player + 1) % self.num_players

        return self.get_state(), reward, self.done

    def is_terminal(self):
        board = self.board

        for i in range(3):
            if len(set(board[i, :])) == 1 and board[i, 0] != 0:
                return True
            if len(set(board[:, i])) == 1 and board[0, i] != 0:
                return True

        if len(set(board.diagonal())) == 1 and board[0, 0] != 0:
            return True
        if len(set(np.fliplr(board).diagonal())) == 1 and board[0, 2] != 0:
            return True

        # Tablero lleno
        return not any(board.flatten() == 0)

    def get_winner(self):
        board = self.board
        for i in range(3):
            if len(set(board[i, :])) == 1 and board[i, 0] != 0:
                return board[i, 0] - 1
            if len(set(board[:, i])) == 1 and board[0, i] != 0:
                return board[0, i] - 1

        if len(set(board.diagonal())) == 1 and board[0, 0] != 0:
            return board[0, 0] - 1

        if len(set(np.fliplr(board).diagonal())) == 1 and board[0, 2] != 0:
            return board[0, 2] - 1

        return None  # empate o partida no terminada

    def get_metrics(self):
        return {
            "Total turns": len(self.history),
            "Winner": self.get_winner(),
            "Board fill %": round((np.count_nonzero(self.board) / 9) * 100, 1),
        }
