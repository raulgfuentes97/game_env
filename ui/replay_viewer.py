import pygame
import sys
import time
import json
import os

BTN_W, BTN_H = 100, 40
FONT_SIZE = 28
LOG_LINES = 6

class ReplayViewer:
    def __init__(self, game, engine=None, cell_size=120):
        self.game = game
        self.engine = engine
        self.history = engine.history if engine else []
        self.index = 0
        self.playing = False
        self.cell_size = cell_size
        self.size = cell_size * 3
        self.total_turns = len(self.history)
        self.slider_drag = False

        pygame.init()
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.screen = pygame.display.set_mode((self.size + 300, self.size))
        pygame.display.set_caption("Replay Viewer")
        self.clock = pygame.time.Clock()

        # Colors
        self.bg = (245, 245, 245)
        self.button_color = (210, 210, 210)
        self.button_hover = (180, 180, 180)
        self.text_color = (40, 40, 40)

        self.last_update = 0
        self.delay = 0.8

    # --- Button utils ---
    def _button(self, x, y, text):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        color = self.button_hover if x < mouse[0] < x+BTN_W and y < mouse[1] < y+BTN_H else self.button_color
        pygame.draw.rect(self.screen, color, (x, y, BTN_W, BTN_H))
        label = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(label, (x + (BTN_W - label.get_width())//2, y + 5))
        if click[0] and x < mouse[0] < x+BTN_W and y < mouse[1] < y+BTN_H:
            return True
        return False

    # --- Replay logic ---
    def reset_game(self):
        self.game.reset()
        for i in range(self.index):
            player, action, _ = self.history[i]
            i_, j_ = action
            self.game.board[i_, j_] = player

    def step_forward(self):
        if self.index < self.total_turns:
            player, action, _ = self.history[self.index]
            i, j = action
            self.game.board[i, j] = player
            self.index += 1

    def step_back(self):
        if self.index > 0:
            self.index -= 1
            self.reset_game()

    def toggle_play(self):
        self.playing = not self.playing

    # --- File operations ---
    def save_replay(self, filename="replay.json"):
        # Calculamos métricas finales
        metrics = {}
        if hasattr(self.game, "get_metrics"):
            metrics = self.game.get_metrics()

        data = {
            "history": [{"player": p, "action": a, "reward": r} for p, a, r in self.history],
            "metrics": metrics
        }
        os.makedirs("replays", exist_ok=True)
        path = os.path.join("replays", filename)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Replay saved to {path}")

    def load_replay(self, filename="replay.json"):
        path = os.path.join("replays", filename)
        if not os.path.exists(path):
            print(f"No replay file found at {path}")
            return
        with open(path, "r") as f:
            data = json.load(f)
        self.history = [(d["player"], tuple(d["action"]), d["reward"]) for d in data["history"]]
        self.total_turns = len(self.history)
        self.index = 0
        self.reset_game()

        # Métricas guardadas
        self.loaded_metrics = data.get("metrics", {})
        print(f"Replay loaded from {path}")


    # --- Rendering ---
    def draw_board(self):
        cell = self.cell_size
        for i in range(1, 3):
            pygame.draw.line(self.screen, (50, 50, 50), (0, i*cell), (self.size, i*cell), 4)
            pygame.draw.line(self.screen, (50, 50, 50), (i*cell, 0), (i*cell, self.size), 4)

    def draw_marks(self):
        cell = self.cell_size
        for i in range(3):
            for j in range(3):
                x = j * cell + cell // 2
                y = i * cell + cell // 2
                val = self.game.board[i, j]
                if val != 0:
                    text = self.font.render("X" if val == 1 else "O", True, (200, 50, 50) if val == 1 else (50, 50, 200))
                    rect = text.get_rect(center=(x, y))
                    self.screen.blit(text, rect)

    def draw_slider(self, x, y, width=240, height=6):
        if self.total_turns <= 1:
            return

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        ratio = self.index / max(1, self.total_turns)
        knob_x = x + int(ratio * width)

        # Base line
        pygame.draw.rect(self.screen, (180, 180, 180), (x, y, width, height))
        # Knob
        pygame.draw.circle(self.screen, (80, 80, 80), (knob_x, y + height // 2), 8)

        # Dragging
        if click[0]:
            if abs(mouse[0] - knob_x) < 10 and abs(mouse[1] - (y + height // 2)) < 10:
                self.slider_drag = True
            if self.slider_drag:
                rel = max(0, min(1, (mouse[0] - x) / width))
                self.index = int(rel * self.total_turns)
                self.reset_game()
        else:
            self.slider_drag = False

    def draw_sidebar(self):
        start_x = self.size + 20
        y = 30
        label = self.font.render(f"Turn {self.index}/{self.total_turns}", True, self.text_color)
        self.screen.blit(label, (start_x, y))
        y += 50

        # Buttons
        if self._button(start_x, y, "← Prev"):
            self.step_back()
        if self._button(start_x + BTN_W + 10, y, "▶ Play" if not self.playing else "⏸ Pause"):
            self.toggle_play()
        if self._button(start_x + 2*(BTN_W + 10), y, "Next →"):
            self.step_forward()
        y += 70

        # Slider
        self.draw_slider(start_x, y)
        y += 50

        # File operations
        if self._button(start_x, y, "💾 Save"):
            self.save_replay()
        if self._button(start_x + BTN_W + 10, y, "📂 Load"):
            self.load_replay()
        y += 70

        # --- Metrics panel ---
        # --- Metrics panel ---
        y += 20
        metrics = {}
        if hasattr(self.game, "get_metrics"):
            metrics = self.game.get_metrics()  # se llama en cada render, reflejando el estado actual
        if metrics:
            pygame.draw.rect(self.screen, (245, 235, 210), (self.size, y, 300, 150))
            label = self.font.render("Metrics", True, (60, 40, 0))
            self.screen.blit(label, (start_x, y + 10))
            for i, (k, v) in enumerate(metrics.items()):
                text = self.font.render(f"{k}: {v}", True, (50, 50, 50))
                self.screen.blit(text, (start_x, y + 40 + i * 30))
            y += 170
        else:
            y += 20

        # Log section
        pygame.draw.rect(self.screen, (230, 230, 230), (self.size, y, 300, self.size - y))
        logs = self.history[max(0, self.index - LOG_LINES):self.index]
        for k, move in enumerate(reversed(logs)):
            player, action, _ = move
            msg = f"P{1 if player == 1 else 2}: {action}"
            log_text = self.font.render(msg, True, (80, 80, 80))
            self.screen.blit(log_text, (start_x, y + 20 + k*30))

    def render(self):
        self.screen.fill(self.bg)
        self.draw_board()
        self.draw_marks()
        self.draw_sidebar()
        pygame.display.flip()

    # --- Main loop ---
    def run(self):
        running = True
        while running:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            now = time.time()
            if self.playing and now - self.last_update > self.delay:
                self.step_forward()
                self.last_update = now
                if self.index >= self.total_turns:
                    self.playing = False

            self.render()

        pygame.quit()
        sys.exit()
