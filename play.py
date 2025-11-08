from core.engine import GameEngine
from games.tic_tac_toe.game import TicTacToeGame
from core.base_agent import BaseAgent
from ui.replay_viewer_gui import ReplayViewerGUI
import os
import json
import importlib.util
import argparse
import itertools  # para ciclo infinito


def load_agent_from_file(filepath):
    """Carga dinámicamente una clase Agent desde un archivo .py"""

    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # buscamos la clase que herede de BaseAgent
    for obj in module.__dict__.values():
        if isinstance(obj, type) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
            return obj   # devolvemos la clase encontrada

    raise ValueError(f"No se encontró ninguna clase Agent válida en {filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cfg",
        required=True,
        help="ruta/al/fichero_conf.json"
    )
    args = parser.parse_args()
    conf_file_path = args.cfg

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

    switch_first_player = False
    # --- Loop infinito de partidas ---
    for _ in itertools.count():
        # Inicializamos el juego y los agentes
        game = TicTacToeGame(num_players=len(agent_configs))
        if switch_first_player:
            agents = [a["class"](a["name"], **a["params"]) for a in agent_configs]
        else:
            agents = [a["class"](a["name"], **a["params"]) for a in reversed(agent_configs)]
        
        switch_first_player = not switch_first_player

        # Ejecutar partida
        engine = GameEngine(game, agents)
        engine.run(verbose=True)

        # Reiniciamos el juego para la visualización
        game.reset()

        # Iniciar viewer
        viewer = ReplayViewerGUI(game, engine)
        # Flatten history: engine.history ya tiene la lista de turnos como (player, action, reward)
        viewer.history = engine.history.copy()
        viewer.run()
