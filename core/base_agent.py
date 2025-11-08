from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Define la interfaz que cualquier 'jugador' debe implementar.
    """
    def __init__(self, name="Agent"):
        self.name = name

    @abstractmethod
    def act(self, state, valid_actions):
        """Recibe el estado y devuelve una acción válida."""
        pass

    def observe(self, state, reward, done, player_idx):
        """Se puede sobreescribir para aprendizaje online."""
        pass

    def set_last(self, state, action):
        pass
