import numpy as np

from clgridworld.grid_world_builder import GridWorldBuilder, InitialStateParams
from example.agent_trainer import AgentTrainer
from example.agents.agent import Agent


class SarsaEpsilonGreedyAgent(Agent):

    def __init__(self, action_space, discount_factor=0.95, learning_rate=0.01, epsilon=0.1, seed=0):

        self.num_actions = action_space.n

        np.random.seed(seed)

        self.Q = {}
        self.action_space = action_space

        self.gamma = discount_factor
        self.alpha = learning_rate
        self.epsilon = epsilon

        self.prev_sample = None

    def get_action(self, curr_state):

        if np.random.rand(1) < self.epsilon:
            # exploration
            return self.action_space.sample()
        else:
            # exploitation
            return self.get_best_action(curr_state)

    def get_best_action(self, curr_state):

        if curr_state not in self.Q:
            self.Q[curr_state] = np.zeros([self.num_actions])
        return np.argmax(self.Q[curr_state])

    def update(self, prev_state, action, curr_state, reward):

        if self.prev_sample is not None:
            prev_sample = self.prev_sample
            self._update(prev_sample[0], prev_sample[1], prev_sample[2], prev_sample[3], action)

        self.prev_sample = (prev_state, action, curr_state, reward)

    def _update(self, prev_state, prev_action, curr_state, prev_reward, curr_action):

        if curr_state not in self.Q:
            self.Q[curr_state] = np.zeros([self.num_actions])

        self.Q[prev_state][prev_action] += self.alpha * (prev_reward + self.gamma * self.Q[curr_state][curr_action]
                                                         - self.Q[prev_state][prev_action])

    def inc_episode(self):
        if self.prev_sample is not None:
            prev_sample = self.prev_sample
            self._update(prev_sample[0], prev_sample[1], prev_sample[2], prev_sample[3],
                         self.get_best_action(prev_sample[2]))


if __name__ == '__main__':

    seed = 0

    # target task spec as defined in Source Task Sequencing,,, Narvekar et al 2017
    params = InitialStateParams(shape=(10, 10), player=(1, 4), key=(7, 5), lock=(1, 1), pit_start=(4, 2),
                                pit_end=(4, 7))
    env = GridWorldBuilder.create(params)

    agent = SarsaEpsilonGreedyAgent(env.action_space, discount_factor=1, seed=seed)

    AgentTrainer(env, agent).train(seed, num_episodes=5000, max_steps_per_episode=10000, episode_log_interval=100)

