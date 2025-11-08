import os
import json
import importlib.util
import argparse
from tqdm import tqdm
from games.tic_tac_toe.game import TicTacToeGame
from core.base_agent import BaseAgent
from core.engine import GameEngine

def load_agent_from_file(filepath):
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for obj in module.__dict__.values():
        if isinstance(obj, type) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
            return obj
    raise ValueError(f"No se encontró ninguna clase Agent válida en {filepath}")


def start_versus(conf_file_path):
    if not os.path.exists(conf_file_path):
        raise ValueError("No existe un fichero de configuración en el path indicado.")

    with open(conf_file_path, "r") as cfg:
        config = json.load(cfg)

    # Cargar jugadores (agent_configs)
    agent_configs = []
    for player in config["players"]:
        agent_configs.append({
            "class": load_agent_from_file(player["path"]),
            "name": player["name"],
            "params": player["params"]
        })

    # cargar otras configuraciones
    rounds = config["rounds"]

    # --- Estadísticas globales ---
    agent_names = [a["name"] for a in agent_configs]
    wins_global = {name: 0 for name in agent_names}
    draws_global = 0

    # --- Estadísticas por orden de inicio ---
    first_start_wins = {name: 0 for name in agent_names}
    first_start_draws = 0
    second_start_wins = {name: 0 for name in agent_names}
    second_start_draws = 0

    half = rounds // 2
    remaining = rounds - half  # para caso de número impar

    for i in tqdm(range(rounds)):
        # Alternar quién empieza
        if i < half:
            # jugador 1 empieza primero
            agents = [a["class"](a["name"], **a["params"]) for a in agent_configs]
            first_start = True
        else:
            # jugador 2 empieza primero
            agents = [a["class"](a["name"], **a["params"]) for a in reversed(agent_configs)]
            first_start = False

        # Jugar partida
        game = TicTacToeGame(num_players=2)
        engine = GameEngine(game, agents, ui=None)
        winner_idx = engine.run(verbose=False)

        # Global
        if winner_idx is None:
            draws_global += 1
        else:
            winner_name = agents[winner_idx].name
            wins_global[winner_name] += 1

        # Estadísticas por orden de inicio
        if first_start:
            if winner_idx is None:
                first_start_draws += 1
            else:
                first_start_wins[agents[winner_idx].name] += 1
        else:
            if winner_idx is None:
                second_start_draws += 1
            else:
                second_start_wins[agents[winner_idx].name] += 1

    # --- Resultados ---
    print(f"\n--- EVALUATION ({rounds} partidas) ---\n")

    # Global
    print("Winrate global:")
    for name in agent_names:
        print(f"  {name}: {wins_global[name]/rounds:.2f}")
    print(f"Draw rate global: {draws_global/rounds:.2f}\n")

    # Jugador 1 empieza primero
    print(f"Resultados cuando jugador {agent_names[0]} empieza primero ({half} partidas):")
    for name in agent_names:
        print(f"  {name}: {first_start_wins[name]/half:.2f}")
    print(f"  Draw rate: {first_start_draws/half:.2f}\n")

    # Jugador 2 empieza primero
    print(f"Resultados cuando jugador {agent_names[-1]} empieza primero ({remaining} partidas):")
    for name in reversed(agent_names):
        print(f"  {name}: {second_start_wins[name]/remaining:.2f}")
    print(f"  Draw rate: {second_start_draws/remaining:.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cfg",
        required=True,
        help="ruta/al/fichero_conf.json"
    )
    args = parser.parse_args()

    start_versus(args.cfg)
