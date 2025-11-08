from core.base_agent import BaseAgent
import random

class RandomAgent(BaseAgent):
    def act(self, state, valid_actions):
        return random.choice(valid_actions)
