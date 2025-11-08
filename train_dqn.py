from core.engine import GameEngine
from games.tic_tac_toe.game import TicTacToeGame
from agents.dqn_agent import DQNAgent
from agents.random_agent import RandomAgent
from agents.tic_tac_toe_agent import MyTicTacToeAgent
import numpy as np
from tqdm import tqdm
from torch.utils.tensorboard import SummaryWriter
import os

EPISODES = 30000
EVAL_INTERVAL = 500
EVAL_EPISODES = 50

# --- Inicialización agentes (self-play) ---
agent1 = DQNAgent("DQN-1")
agent2 = DQNAgent("DQN-2")
agents = [agent1, agent2]

# --- Writer TensorBoard ---
writer = SummaryWriter()
best_winrate = 0.0

# --- Inicialización juego (se crearán nuevos objetos por partida) ---
# engine no es necesario aquí para el loop de training; lo crearemos en evaluate si procede


def evaluate_against_fixed(agent, opponent_class, game_class, episodes=50):
    """
    Evalúa `agent` contra un oponente fijo (RandomAgent o custom).
    Devuelve winrate del `agent` (porcentaje de victorias del agent en estas partidas).
    """
    wins = 0
    prev_epsilon = agent.epsilon
    agent.epsilon = 0.0  # solo explotación durante la evaluación

    for _ in range(episodes):
        game = game_class(num_players=2)
        game.reset()
        done = False
        opponent = opponent_class("Rival")
        eval_agents = [agent, opponent]  # agent siempre en posición 0 para esta evaluación

        while not done:
            current_players = game.get_current_players()
            player_actions = []
            for p_idx in current_players:
                valid = game.valid_actions(p_idx)
                # pedimos el estado completo a los agentes (API: act(state, valid_actions))
                action = eval_agents[p_idx].act(game.get_state(), valid)
                player_actions.append((p_idx, action))
            _, rewards, done = game.step(player_actions)

        # rewards es lista de recompensas por jugador; si rewards[0] == 1, agent ganó
        if isinstance(rewards, list):
            if rewards[0] == 1:
                wins += 1
        else:
            # Si por algún motivo reward viene como escalar (versiones antiguas), asumimos index 0
            if rewards == 1:
                wins += 1

    agent.epsilon = prev_epsilon
    return wins / episodes


# --- Loop de entrenamiento ---
for episode in tqdm(range(1, EPISODES + 1)):

    game = TicTacToeGame(num_players=2)
    game.reset()
    state = game.get_state()
    done = False
    losses = []

    while not done:
        current_players = game.get_current_players()  # lista de índices de jugadores que deben actuar
        player_actions = []

        for p_idx in current_players:
            valid = game.valid_actions(p_idx)
            action = agents[p_idx].act(state, valid)
            agents[p_idx].set_last(state, action)
            player_actions.append((p_idx, action))

        # Ejecutar el turno
        next_state, rewards, done = game.step(player_actions)

        # Almacenar experiencia y entrenar (ambos agentes si corresponde)
        for p_idx, reward in enumerate(rewards):
            agents[p_idx].observe(next_state, reward, done, p_idx)
            loss = agents[p_idx].train_from_memory()
            if loss is not None:
                losses.append(loss)

        state = next_state

    # Decay epsilon para ambos agentes (solo aquí)
    for a in agents:
        a.epsilon = max(a.epsilon_min, a.epsilon * a.epsilon_decay)
        # Log epsilon individual
        writer.add_scalar(f"epsilon/{a.name}", a.epsilon, episode)

    # Log de pérdida promedio por episodio
    if losses:
        writer.add_scalar("loss", np.mean(losses), episode)

    # --- Evaluación periódica ---
    if episode % EVAL_INTERVAL == 0:
        winrate = evaluate_against_fixed(agent1, MyTicTacToeAgent, TicTacToeGame, episodes=EVAL_EPISODES)
        writer.add_scalar("winrate_vs_fixed", winrate, episode)
        print(f"[EVAL] Ep {episode} → winrate vs {MyTicTacToeAgent.__name__}: {winrate:.2f} | ε={agent1.epsilon:.3f}")

        # Guardar modelo si mejora
        if winrate > best_winrate:
            best_winrate = winrate
            os.makedirs("models", exist_ok=True)
            save_path = f"models/best_model_vs_{MyTicTacToeAgent.__name__}.pth"
            agent1.save(save_path)
            print(f"💾 Nuevo MEJOR modelo guardado contra {MyTicTacToeAgent.__name__}! -> {save_path}")

# Cerrar writer al final
writer.close()
