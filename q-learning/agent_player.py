import numpy as np
import json

from player import Player

class QLearningAgent(Player):
    def __init__(self, name):
        super().__init__(name)
        self.q_table = dict()
        self.episodes = []
        self.epsilon = 0.5
        self.epsilon_decay = 0.95
        self.alpha = 0.1
        self.gamma = 0.9

    def get_best_move(self, board):
        # 1. Get current state and legal moves
        state_str = board.to_fen()
        legal_moves = board.get_legal_moves()
        
        # Convert moves to strings so they can be JSON keys: "((x,y),(nx,ny))"
        move_strings = [str(m) for m in legal_moves]

        # 2. Initialize state in Q-table if new
        if state_str not in self.q_table:
            self.q_table[state_str] = {m_str: 0.0 for m_str in move_strings}
        else:
            # Update existing state with any new legal moves (if board logic changed)
            for m_str in move_strings:
                if m_str not in self.q_table[state_str]:
                    self.q_table[state_str][m_str] = 0.0

        # 3. Epsilon-Greedy Selection
        if np.random.rand() < self.epsilon:
            move_idx = np.random.choice(len(legal_moves))
            action_str = move_strings[move_idx]
            action_tuple = legal_moves[move_idx]
        else:
            q_values = self.q_table[state_str]
            # Filter Q-values to only include currently legal moves
            current_q = {m_str: q_values[m_str] for m_str in move_strings}
            max_q = max(current_q.values())
            best_actions = [m_str for m_str, q in current_q.items() if q == max_q]
            action_str = np.random.choice(best_actions)
            action_tuple = eval(action_str) # Convert string back to tuple

        # Record for training
        self.episodes.append((state_str, action_str))
        return action_tuple

    def update_q_values(self, final_reward):
        for i in reversed(range(len(self.episodes))):
            s, a = self.episodes[i]
            if i == len(self.episodes) - 1:
                target = final_reward
            else:
                s_next, _ = self.episodes[i+1]
                max_future_q = max(self.q_table[s_next].values()) if s_next in self.q_table else 0
                target = 0 + self.gamma * max_future_q
            
            self.q_table[s][a] += self.alpha * (target - self.q_table[s][a])
        self.episodes = []
    
    def set_q_table(self, json_file:str):   
        with open (json_file, "r") as file: 
            self.q_table = json.load(file)
        print("q table set")
        self.epsilon = 0
    
    def store_q_values(self, file_name:str):
        with open(file_name, "w") as file:
            json.dump(self.q_table, file, indent=2)