import os
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from core.base_agent import BaseAgent


class DQNAgent(BaseAgent):

    def __init__(self, name, lr=0.001, gamma=0.95, epsilon=1.0,
                epsilon_min=0.05, epsilon_decay=0.9995, model_path=None):
        super().__init__(name)

        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # Red neuronal (solo CPU)
        self.model = nn.Sequential(
            nn.Linear(9, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 9)
        )

        self.target_model = nn.Sequential(
            nn.Linear(9, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 9)
        )

        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()

        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

        self.memory = []
        self.batch_size = 64
        self.max_memory = 50000
        self.update_target_steps = 500
        self.last_state = None
        self.train_step = 0

        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
            self.target_model.load_state_dict(self.model.state_dict())
            self.epsilon = 0.0  # inferencia pura

    # ------------------------------------------------------------------
    # Métodos del agente
    # ------------------------------------------------------------------

    def act(self, state, valid_actions):
        board = torch.tensor(state["board"].reshape(-1), dtype=torch.float32)

        if random.random() < self.epsilon:
            return random.choice(valid_actions)

        with torch.no_grad():
            q_values = self.model(board).cpu()

        return max(valid_actions, key=lambda a: q_values[a[0] * 3 + a[1]].item())


    def observe(self, next_state, reward, done, player_idx):
        if self.last_state is None:
            return

        if isinstance(reward, list):
            reward = reward[player_idx]

        self.memory.append((self.last_state, self.last_action, reward, next_state, done))
        if len(self.memory) > self.max_memory:
            self.memory.pop(0)


    def set_last(self, state, action):
        self.last_state = state
        self.last_action = action

    # ------------------------------------------------------------------
    # ✅ Double DQN + Target Network
    # ------------------------------------------------------------------
    def train_from_memory(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)

        boards = []
        targets = []

        for state, action, reward, next_state, done in batch:
            board = torch.tensor(state["board"].reshape(-1), dtype=torch.float32)
            next_board = torch.tensor(next_state["board"].reshape(-1), dtype=torch.float32)

            target = self.model(board).detach()
            action_index = action[0] * 3 + action[1]

            if done:
                target[action_index] = reward
            else:
                # DOUBLE DQN (target más estable)
                best_next_action = torch.argmax(self.model(next_board)).item()
                target[action_index] = reward + self.gamma * self.target_model(next_board)[best_next_action].item()

            boards.append(board)
            targets.append(target)

        boards_tensor = torch.stack(boards)
        targets_tensor = torch.stack(targets)

        pred = self.model(boards_tensor)
        loss = self.loss_fn(pred, targets_tensor)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # actualizar target network periódicamente
        self.train_step += 1
        if self.train_step % self.update_target_steps == 0:
            self.target_model.load_state_dict(self.model.state_dict())

        return loss.item()

    def update_target_network(self):
        self.target_model.load_state_dict(self.model.state_dict())


    def save(self, path="model.pth"):
        torch.save(self.model.state_dict(), path)
