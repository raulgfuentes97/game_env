import time
import pygame

class GameEngine:
    """
    Motor genérico que coordina el flujo del juego:
    - Pregunta al juego qué jugadores deben actuar (turno o fase)
    - Solicita las acciones a cada agente
    - Ejecuta esas acciones en el juego
    - Actualiza la interfaz (si existe)
    """
    def __init__(self, game, agents, ui=None, delay=0.6):
        self.game = game
        self.agents = agents
        self.ui = ui
        self.delay = delay
        self.history = []

    def run(self, verbose=False):
        self.game.reset()
        done = False

        if self.ui:
            self.ui.render(self.game.get_state())
            pygame.display.flip()

        while not done:
            # Mantener viva la ventana si hay UI
            if self.ui:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return

            # Consultar quiénes deben actuar ahora
            current_players = self.game.get_current_players()
            if not current_players:
                break

            player_actions = []
            for player_idx in current_players:
                agent = self.agents[player_idx]
                state = self.game.get_state(player_idx)
                valid = self.game.valid_actions(player_idx)
                action = agent.act(state, valid)
                player_actions.append((player_idx, action))
                
                agent.set_last(state, action)
                next_state, reward, done = self.game.step([(player_idx, action)])
                agent.observe(next_state, reward, done, player_idx)

            # next_state, reward, done = self.game.step(player_actions)
            # for idx, r in enumerate(reward):
            #     self.agents[idx].observe(next_state, r, done)

            # Log para depuración
            for idx, action in player_actions:
                name = getattr(self.agents[idx], "name", f"Agent {idx}")
                if verbose:
                    print(f"{name} played {action} | reward: {reward[idx]}")

            self.history.append(*[(self.agents[idx].name, action, reward[idx]) for idx, action in player_actions])

            if self.ui:
                self.ui.render(self.game.get_state())
                pygame.display.flip()
                time.sleep(self.delay)

        winner = self.game.get_winner()
        if verbose and winner:
            print(f"Game over. Winner: {self.agents[winner].name}")

        if self.ui:
            self.ui.show_winner(winner)
            self.ui.wait_exit()

        return winner
