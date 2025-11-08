from core.base_agent import BaseAgent
import random

class MyTicTacToeAgent(BaseAgent):

    def __init__(self, name="Yo", write_logs=False):
        super().__init__(name)
        self.write_logs = write_logs

    def act(self, state, valid_actions):
        board = state["board"]
        board_size = len(board[0])
        minimax = dict()
        with open("logfile.log", "a") as f:
            for action in valid_actions:
                i, j = action
                # cells where I can win (check row, column & diagonals)
                if (sum([board[i][x] for x in range(board_size)]) == (board_size - 1)) or \
                    (sum([board[x][j] for x in range(board_size)]) == (board_size - 1)) or \
                    ((i == j and sum([board[x][x] for x in range(board_size)]) == (board_size - 1))) or \
                    (i == (board_size - j - 1) and sum([board[x][board_size - x - 1] for x in range(board_size)]) == (board_size - 1)):
                    if self.write_logs:
                        f.write("---> I WIN!\n")
                    return action

                # cells where opponent can win (check row, column & diagonals)
                if (sum([board[i][x] for x in range(board_size)]) == -(board_size - 1)) or \
                    (sum([board[x][j] for x in range(board_size)]) == -(board_size - 1)) or \
                    (i == j and sum([board[x][x] for x in range(board_size)]) == -(board_size - 1)) or \
                    (i == (board_size - j - 1) and sum([board[x][board_size - x - 1] for x in range(board_size)]) == -(board_size - 1)):
                    if self.write_logs:
                        f.write("---> I PREVENT YOU FROM WINNING!\n")
                    return action

                # check minimax value of action
                # +1 point for every enemy cell
                # +1 point for every player cell
                # 0 points if shared row/col/diagonal
                # check row
                # for x in range(board_size):

                # check col
                # check diagonal 1 ?
                # check diagonal 2 ?

                # cells that create the most chances to win next turn
                # TODO
            if self.write_logs:
                f.write("---> RANDOM ACTION\n")
            return random.choice(valid_actions)
        
