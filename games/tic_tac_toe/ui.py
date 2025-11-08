import pygame
import sys
import numpy as np

CELL_SIZE = 120
GRID_COLOR = (50, 50, 50)
BG_COLOR = (240, 240, 240)
COLORS = [
    (200, 50, 50),    # Player 0
    (50, 50, 200),    # Player 1
    (50, 150, 50),    # Player 2 (si algún día hay más)
    (180, 120, 20),
]
LINE_WIDTH = 5


class TicTacToeUI:
    def __init__(self, game, agents=None):
        self.game = game
        self.agents = agents or []
        self.size = CELL_SIZE * 3
        pygame.init()
        self.screen = pygame.display.set_mode((self.size, self.size))
        pygame.display.set_caption("Tic Tac Toe")
        self.font = pygame.font.SysFont(None, 72)
        self.small_font = pygame.font.SysFont(None, 36)
        self.clock = pygame.time.Clock()

    # -----------------------------
    # Drawing helpers
    # -----------------------------

    def draw_board(self):
        self.screen.fill(BG_COLOR)
        for i in range(1, 3):
            pygame.draw.line(
                self.screen, GRID_COLOR, (0, i * CELL_SIZE), (self.size, i * CELL_SIZE), LINE_WIDTH
            )
            pygame.draw.line(
                self.screen, GRID_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, self.size), LINE_WIDTH
            )

    def draw_marks(self, state):
        for i in range(3):
            for j in range(3):
                mark = state[i, j]
                if mark == 0:
                    continue
                color = COLORS[(mark - 1) % len(COLORS)]
                symbol = self.get_symbol(mark - 1)
                text = self.font.render(symbol, True, color)
                rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2))
                self.screen.blit(text, rect)

    def get_symbol(self, player_idx):
        """Devuelve un símbolo o inicial del agente."""
        if not self.agents or player_idx >= len(self.agents):
            return chr(65 + player_idx)  # A, B, C...
        name = self.agents[player_idx].name
        return name[0].upper() if name else chr(65 + player_idx)

    # -----------------------------
    # Rendering
    # -----------------------------

    def render(self, state, current_player=None):
        self.draw_board()
        self.draw_marks(state)

        # Mostrar turno actual
        if current_player is not None and self.agents:
            name = self.agents[current_player].name
            info = f"Turn: {name}"
            text = self.small_font.render(info, True, (20, 20, 20))
            self.screen.blit(text, (10, 10))

        pygame.display.flip()

    def show_winner(self, winner_idx):
        pygame.time.wait(500)
        overlay = pygame.Surface((self.size, self.size))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        if winner_idx is None:
            msg = "Draw!"
        elif 0 <= winner_idx < len(self.agents):
            msg = f"{self.agents[winner_idx].name} wins!"
        else:
            msg = f"Player {winner_idx} wins!"

        text = self.font.render(msg, True, (255, 255, 255))
        rect = text.get_rect(center=(self.size // 2, self.size // 2))
        self.screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.wait(2000)

    # -----------------------------
    # Replay
    # -----------------------------

    def run_replay(self, engine):
        """Reproduce una partida ya jugada, paso a paso."""
        self.game.reset()
        for turn in engine.history:
            # cada turno puede contener varias acciones (en juegos simultáneos)
            for player_idx, action, _ in turn:
                i, j = action
                self.game.state[i, j] = player_idx + 1
                self.render(self.game.state, current_player=player_idx)
                self.clock.tick(1)  # 1 jugada por segundo
        self.show_winner(self.game.get_winner())
        self.wait_exit()

    # -----------------------------
    # Exit
    # -----------------------------

    def wait_exit(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.clock.tick(30)
