from abc import ABC, abstractmethod

class BaseGame(ABC):
    """
    Interfaz general para cualquier juego por turnos.
    """
    def __init__(self):
        self.state = None
        self.current_player = 0
        self.history = []

    @abstractmethod
    def reset(self):
        """Inicializa el estado del juego."""
        pass

    @abstractmethod
    def valid_actions(self):
        """Devuelve las acciones válidas para el jugador actual."""
        pass

    @abstractmethod
    def step(self, action):
        """Ejecuta una acción, avanza el turno y devuelve el nuevo estado, recompensa y si terminó."""
        pass

    @abstractmethod
    def is_terminal(self):
        """Devuelve True si la partida terminó."""
        pass

    @abstractmethod
    def get_winner(self):
        """Devuelve el índice del ganador, o None si empate."""
        pass

    def get_state(self):
        """Devuelve una copia del estado actual."""
        return self.state

    def get_metrics(self):
        """
        Devuelve un diccionario con métricas personalizadas del juego.
        Cada juego puede sobreescribirlo si lo desea.
        Ejemplo:
            return {"turns": len(self.history), "winner": self.get_winner()}
        """
        return {}