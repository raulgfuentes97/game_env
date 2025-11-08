import pygame
import pygame_gui
import sys
import time
from pygame_gui.elements import UIButton, UILabel, UIHorizontalSlider, UIPanel

CELL_SIZE = 120
GRID_COLOR = (50, 50, 50)
X_COLOR = (200, 50, 50)
O_COLOR = (50, 50, 200)
BG_COLOR = (240, 240, 240)

class ReplayViewerGUI:
    def __init__(self, game, engine, width=600, height=360):
        pygame.init()
        self.game = game
        self.engine = engine
        self.history = engine.history
        self.index = 0
        self.playing = False
        self.cell_size = CELL_SIZE
        self.board_size = self.cell_size * 3
        self.window_size = (self.board_size + 250, self.board_size)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Replay Viewer GUI")

        # Mapping dinámico de jugadores
        self.agent_map = {agent.name: i+1 for i, agent in enumerate(engine.agents)}


        # UI Manager
        self.ui_manager = pygame_gui.UIManager(self.window_size, 'ui/theme.json')

        # Panel lateral
        self.panel = UIPanel(
            relative_rect=pygame.Rect(self.board_size, 0, 250, self.board_size),
            manager=self.ui_manager,
            object_id="#panel",
            anchors={"left": "left", "right": "right", "top": "top", "bottom": "bottom"}
        )

        # Botones
        self.btn_prev = UIButton(
            relative_rect=pygame.Rect(10, 10, 100, 40),
            text='Prev',
            manager=self.ui_manager,
            container=self.panel,
            object_id="#boton_prev"
        )

        self.btn_play = UIButton(
            relative_rect=pygame.Rect(120, 10, 100, 40),
            text='Play',
            manager=self.ui_manager,
            container=self.panel,
            object_id="#boton_play"
        )

        self.btn_next = UIButton(
            relative_rect=pygame.Rect(10, 60, 100, 40),
            text='Next',
            manager=self.ui_manager,
            container=self.panel,
            object_id="#boton_next"
        )

        self.btn_end = UIButton(
            relative_rect=pygame.Rect(120, 60, 100, 40),
            text='Quit',
            manager=self.ui_manager,
            container=self.panel,
            object_id="#boton_end"
        )

        # Slider
        self.slider = UIHorizontalSlider(relative_rect=pygame.Rect(10, 110, 220, 30),
                                         start_value=0, value_range=(0, len(self.history)),
                                         manager=self.ui_manager, container=self.panel)

        # Labels métricas y logs
        self.label_metrics = UILabel(relative_rect=pygame.Rect(10, 150, 230, 80),
                                     text="Metrics", manager=self.ui_manager, container=self.panel)
        self.label_logs = UILabel(relative_rect=pygame.Rect(10, 240, 230, 120),
                                  text="Logs", manager=self.ui_manager, container=self.panel)

        self.clock = pygame.time.Clock()
        self.last_update = time.time()
        self.delay = 0.8  # segundos entre turnos
        self.game.reset()  # reseteamos tablero para visualizar desde 0
        self.update_labels()

    # --- Tablero ---
    def draw_board(self):
        self.screen.fill(BG_COLOR)
        # Líneas
        for i in range(1, 3):
            pygame.draw.line(self.screen, GRID_COLOR, (0, i*self.cell_size), (self.board_size, i*self.cell_size), 4)
            pygame.draw.line(self.screen, GRID_COLOR, (i*self.cell_size, 0), (i*self.cell_size, self.board_size), 4)
        # Marcas
        for i in range(3):
            for j in range(3):
                val = self.game.board[i, j]
                if val != 0:
                    text = 'X' if val == 1 else 'O'
                    color = X_COLOR if val == 1 else O_COLOR
                    font = pygame.font.SysFont(None, 72)
                    surf = font.render(text, True, color)
                    rect = surf.get_rect(center=(j*self.cell_size+self.cell_size//2, i*self.cell_size+self.cell_size//2))
                    self.screen.blit(surf, rect)

    # --- Turnos ---
    def step_forward(self):
        if self.index < len(self.history):
            agent_name, action, _ = self.history[self.index]
            player = self.agent_map.get(agent_name, 0)
            i, j = action
            self.game.board[i, j] = player
            self.index += 1
            self.slider.set_current_value(self.index)

    def step_back(self):
        if self.index > 0:
            self.index -= 1
            self.game.reset()
            for i in range(self.index):
                agent_name, action, _ = self.history[i]
                player = self.agent_map.get(agent_name, 0)
                ii, jj = action
                self.game.board[ii, jj] = player
            self.slider.set_current_value(self.index)

    # --- Actualizar métricas y logs ---
    def update_labels(self):
        # Métricas dinámicas
        if hasattr(self.game, "get_metrics"):
            metrics = self.game.get_metrics()
            winner = metrics["Winner"]
            if winner:
                metrics["Winner"] = self.engine.agents[winner].name
            # Corregimos Total turns
            metrics["Total turns"] = len(self.history)  # total jugadas de la partida
            text = "\n".join([f"{k}: {v}" for k,v in metrics.items()])
            self.label_metrics.set_text(text)

        # Logs últimos movimientos
        logs = self.history[max(0, self.index - 6):self.index]
        log_text = "\n".join([f"{p}: {a}" for p,a,_ in reversed(logs)])
        self.label_logs.set_text(log_text)

        # Slider
        self.slider.set_current_value(self.index)

    def toggle_play(self):
        self.playing = not self.playing
        self.btn_play.set_text("Pause" if self.playing else "Play")

    # --- Loop principal ---
    def run(self):
        running = True
        while running:
            if self.playing:
                self.btn_play.set_text("Pause")
            else:
                self.btn_play.set_text("Play")

            time_delta = self.clock.tick(30)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Botones Play/Prev/Next
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.btn_prev:
                        self.step_back()
                        self.playing = False
                    elif event.ui_element == self.btn_play:
                        self.toggle_play()
                    elif event.ui_element == self.btn_next:
                        self.step_forward()
                        self.playing = False
                    elif event.ui_element == self.btn_end:
                        pygame.quit()
                        sys.exit()

                # Slider
                if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == self.slider:
                        self.index = int(min(max(event.value, 0), len(self.history)))
                        self.game.reset()
                        for i in range(self.index):
                            p, a, _ = self.history[i]
                            ii, jj = a
                            self.game.board[ii, jj] = p

                self.ui_manager.process_events(event)

            # Avanzar automáticamente si play
            if self.playing and time.time() - self.last_update > self.delay:
                self.step_forward()
                self.last_update = time.time()
                if self.index >= len(self.history):
                    self.playing = False
                    self.btn_play.set_text("Play")

            self.draw_board()
            self.update_labels()
            self.ui_manager.update(time_delta)
            self.ui_manager.draw_ui(self.screen)
            pygame.display.update()

        pygame.quit()
        # sys.exit()
