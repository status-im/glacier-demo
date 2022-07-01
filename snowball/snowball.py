# From webpage example:
#
# Parameters
# n: number of participants
# k (sample size): between 1 and n
# α (quorum size): between 1 and k
# β (decision threshold): >= 1
#
# Algorithm
#
# preference := pizza
# consecutiveSuccesses := 0
# while not decided:
#   ask k random people their preference
#   if >= α give the same response:
#     preference := response with >= α
#     if preference == old preference:
#       consecutiveSuccesses++
#     else:
#       consecutiveSuccesses = 1
#   else:
#     consecutiveSuccesses = 0
#   if consecutiveSuccesses > β:
#     decide(preference)

# Preferences

from dataclasses import dataclass
from typing import Callable, List, Generator, Protocol, Tuple
import random
from collections import Counter

from numpy import sqrt
from rusty_results import Option, Empty, Some
from copy import copy


class Vote(Protocol):
    __slots__ = []

    def flip(self) -> "Vote":
        pass

    @classmethod
    def __eq__(cls, other):
        return isinstance(other, (cls, ))


class VoteYes(Vote):
    __slots__ = []

    def flip(self):
        return VOTE_NO


class VoteNo(Vote):
    __slots__ = []

    def flip(self):
        return VOTE_YES


VOTE_YES = VoteYes()
VOTE_NO = VoteNo()


@dataclass(slots=True)
class SnowballConfig:
    quorum_size: int
    sample_size: int
    decision_threshold: int


@dataclass(slots=True)
class SnowballState:
    preference: Vote
    consecutive_success: int
    decision: Option[Vote]


def update_state(
        node_id: int,
        state: SnowballState,
        config: SnowballConfig,
        sample_function: Callable[[int, int], List[Vote]]):
    sample_response = sample_function(config.sample_size, node_id)
    previous_preference = state.preference
    preference_count = sample_response.count(previous_preference)
    not_preference_count = len(sample_response) - preference_count

    if preference_count >= config.quorum_size:
        state.consecutive_success += 1
    elif not_preference_count >= config.quorum_size:
        state.consecutive_success = 1
        state.preference = state.preference.flip()
    else:
        state.consecutive_success = 0

    if state.consecutive_success > config.decision_threshold:
        state.decision = Some(state.preference)


def sample(nodes: List[SnowballState]) -> Callable[[int, int], List[Vote]]:
    def _sample(k: int, node_id: int):
        return [
           nodes[i].preference for i in random.sample(list(range(len(nodes))), k + 1) if i != node_id
        ][:k]
    return _sample


def simulate(nodes: List[SnowballState], config: SnowballConfig, max_ttf: int) -> Generator[List[SnowballState], None, None]:
    ttf = 0
    sample_query = sample(nodes)
    while not all(node.decision.is_some for node in nodes) and ttf < max_ttf:
        yield [copy(node) for node in nodes]
        non_decided = (
            (node_id, node_state) for node_id, node_state in enumerate(nodes) if node_state.decision.is_empty
        )
        for node_id, node_state in non_decided:
            update_state(node_id, node_state, config, sample_query)


def generate_random_nodes(size: int, weights: Tuple[float, float]) -> List[SnowballState]:
    return [
        SnowballState(preference=preference, consecutive_success=0, decision=Empty())
        for preference in random.choices([VOTE_YES, VOTE_NO], weights=weights, k=size)
    ]


def plot_history(history: List[List[SnowballState]]):
    import seaborn as sbn
    import matplotlib.pyplot as plt
    preferences = (Counter(x.preference for x in step) for step in history)
    yes, no = zip(*((x[VOTE_YES], x[VOTE_NO]) for x in preferences))
    sbn.lineplot(data={"yes": yes, "no": no})
    plt.show()


def plot_animated_heatmap(history: List[List[SnowballState]]):
    import matplotlib.pyplot as plt
    from matplotlib import animation
    import numpy as np
    import seaborn as sbn
    fig = plt.figure()
    heat_max = max(node.consecutive_success for node in history[-1])
    print(heat_max)
    half_heat_max = heat_max//2

    def node_state_to_hue_value(node):
        return 1 if node.preference == VOTE_YES else -1

    def init():
        data = np.array(
            [node_state_to_hue_value(node) for node in history[0]]
        )
        squared_shape = int(sqrt(len(data)))
        data = np.reshape(data, (squared_shape, squared_shape))

        sbn.heatmap(data, vmax=1,  vmin=-1, fmt="d", cmap="coolwarm", cbar=True)

    def animate(i):
        plt.clf()
        data = np.array(
            [node_state_to_hue_value(node) for node in history[i]]
        )
        data = np.reshape(data, (-1, int(sqrt(len(data)))))
        sbn.heatmap(data, vmax=1, vmin=-1, fmt="d", cmap="coolwarm", cbar=True)
        plt.text(0, 0, f"Round = {i}")

    _ = animation.FuncAnimation(
        fig, init_func=init, func=animate, frames=len(history), repeat=False, interval=1000
    )

    plt.show()


if __name__ == "__main__":
    n = 30
    k = 20
    alpha = 16
    beta = 30

    config = SnowballConfig(alpha, k, beta)

    nodes = generate_random_nodes(n*n, (0.51, 0.49))
    history_states = list(simulate(nodes, config, 100))
    # plot_history(history_states)
    plot_animated_heatmap(history_states)
