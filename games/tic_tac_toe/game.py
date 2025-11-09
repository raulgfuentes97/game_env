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
    
    def evaluate_move(self, player_index, action):
        """
        Reward intermedio:
        +0.3 si esta jugada crea 2 o más líneas con 2 fichas propias
        +0.2 si esta jugada crea línea con 2 fichas propias (casi gana)
        +0.2 si bloquea línea del oponente con 2 fichas
        +0.02 por fila, columna y/o diagonal vacía desde la que se coloca la ficha
        """
        i, j = action
        reward = 0.0

        my_mark = player_index + 1               # 1 o 2
        opp_mark = 2 if my_mark == 1 else 1

        # -------------------------
        # 1) Detectar casi-victoria propia y bloqueo al rival
        # -------------------------
        my_two_in_line = 0
        block_two_line = 0

        # FILA
        row = self.board[i, :]
        if list(row).count(my_mark) == 2 and list(row).count(0) == 1:
            my_two_in_line += 1
        if list(row).count(opp_mark) == 2 and list(row).count(0) == 1:
            block_two_line += 1

        # COLUMNA
        col = self.board[:, j]
        if list(col).count(my_mark) == 2 and list(col).count(0) == 1:
            my_two_in_line += 1
        if list(col).count(opp_mark) == 2 and list(col).count(0) == 1:
            block_two_line += 1

        # DIAGONAL PRINCIPAL
        if i == j:
            diag = [self.board[x, x] for x in range(3)]
            if diag.count(my_mark) == 2 and diag.count(0) == 1:
                my_two_in_line += 1
            if diag.count(opp_mark) == 2 and diag.count(0) == 1:
                block_two_line += 1

        # DIAGONAL SECUNDARIA
        if i + j == 2:
            diag = [self.board[x, 2 - x] for x in range(3)]
            if diag.count(my_mark) == 2 and diag.count(0) == 1:
                my_two_in_line += 1
            if diag.count(opp_mark) == 2 and diag.count(0) == 1:
                block_two_line += 1

        # Aplicar reglas del reward shaping
        if my_two_in_line >= 2:
            reward += 0.3                     # crea dos amenazas simultáneas → brutal
        elif my_two_in_line == 1:
            reward += 0.2                     # casi gana

        if block_two_line >= 1:
            reward += 0.2                     # bloquea jugada del rival

        # -------------------------
        # 2) Bonus por posiciones "útiles"
        #    (fila / columna / diagonal totalmente abiertas)
        # -------------------------
        emptiness_bonus = 0

        if all(self.board[i, x] == 0 for x in range(3)):
            emptiness_bonus += 1
        if all(self.board[x, j] == 0 for x in range(3)):
            emptiness_bonus += 1
        if i == j and all(self.board[x, x] == 0 for x in range(3)):
            emptiness_bonus += 1
        if i + j == 2 and all(self.board[x, 2 - x] == 0 for x in range(3)):
            emptiness_bonus += 1

        reward += emptiness_bonus * 0.02

        return reward



    def step(self, player_actions):
        rewards = [0.0] * self.num_players

        for player_index, action in player_actions:
            i, j = action
            self.board[i, j] = player_index + 1
            self.history.append((player_index, action))

        # Check terminal
        self.done = self.is_terminal()

        # Reward shaping
        for player_index, action in player_actions:
            if self.done:
                winner = self.get_winner()
                if winner == player_index:
                    rewards[player_index] += 3.0
                elif winner is None:
                    rewards[player_index] = 0.0  # empate
                else:
                    rewards[player_index] -= 3.0
            else:
                # Recompensa intermedia
                rewards[player_index] += self.evaluate_move(player_index, action)

        # Siguiente jugador
        self.current_player = (self.current_player + 1) % self.num_players
        return self.get_state(), rewards, self.done

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
