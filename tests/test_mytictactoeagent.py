import json
import os
from agents.tic_tac_toe_agent import MyTicTacToeAgent

def load_test_cases():
    path = os.path.join(os.path.dirname(__file__), "test_cases_tictactoe.json")
    with open(path, "r") as f:
        return json.load(f)

def test_agent_using_json_cases():
    agent = MyTicTacToeAgent("TestAgent", write_logs=True)

    for case in load_test_cases():
        state = case["state"]
        valid_actions = [tuple(a) for a in case["valid_actions"]]
        expected_actions = [tuple(a) for a in case["expected_actions"]]

        action = agent.act(state, valid_actions)

        assert action in expected_actions, \
            f"❌ Test '{case['name']}' failed.\nAction returned: {action}\nExpected one of: {expected_actions}"

        print(f"✅ Passed case: {case['name']} → action {action}")
