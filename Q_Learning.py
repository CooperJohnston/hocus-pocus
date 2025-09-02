import numpy as np
import random

class QLearner:

    def __init__(self, user_csv, num_states=4, num_actions=7, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.num_states = num_states
        self.num_actions = num_actions
        self.alpha = alpha        # Learning rate
        self.gamma = gamma        # Discount factor
        self.epsilon = epsilon    # Exploration rate
        self.Q_table = np.zeros((num_states, num_actions))
        self.q_table_path = user_csv
        self.load_q_table()

    def save_q_table(self):
        np.save(self.q_table_path, self.Q_table)

    def load_q_table(self):
        try:
            self.Q_table = np.load(self.q_table_path)
            print(f"Q-table loaded from {self.q_table_path}")
        except FileNotFoundError:
            print(f"No Q-table found at {self.q_table_path}. Starting fresh.")

    def get_state(self, focus_score):
        if focus_score > 90:
            return 0
        elif focus_score > 70:
            return 1
        elif focus_score > 50:
            return 2
        elif focus_score > 30:
            return 3
        else:
            return 0


    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)  # Explore
        return np.argmax(self.Q_table[state])  # Exploit


    def update(self, state, action, reward, new_state):
        best_next = np.argmax(self.Q_table[new_state])
        self.Q_table[state, action] = (1 - self.alpha) * self.Q_table[state, action] + \
                                      self.alpha * (reward + self.gamma * self.Q_table[new_state, best_next])
