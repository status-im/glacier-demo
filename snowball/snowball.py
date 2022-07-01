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
from typing import Callable, List, Generator, Dict, Protocol, Tuple
import random
from collections import Counter
from rusty_results import Option, Empty, Some


class Vote(Protocol):
    __slots__ = []

    def flip(self) -> "Vote":
        pass


class VoteYes(Vote):
    __slots__ = []

    def flip(self):
        return VOTE_NO


class VoteNo(Vote):
    __slots__ = []

    def flip(self):
        return VOTE_YES


VOTE_NO = VoteNo()
VOTE_YES = VoteYes()


@dataclass(slots=True)
class SnowballConfig:
    quorum_size: int
    sample_size: int
    decision_threshold: int


@dataclass(slots=True)
class SnowballState:
    opinion: Vote
    consecutive_success: int
    decision: Option[Vote]


def update_state(
        node_id: int,
        state: SnowballState,
        config: SnowballConfig,
        sample_function: Callable[[int, int], List[Vote]]):
    sample_response = sample_function(config.sample_size, node_id)
    previous_preference = state.opinion
    preference_count = sample_response.count(previous_preference)
    not_preference_count = len(sample_response) - preference_count

    if preference_count >= config.quorum_size:
        state.consecutive_success += 1
    elif not_preference_count >= config.quorum_size:
        state.consecutive_success = 1
        state.opinion = state.opinion.flip()
    else:
        state.consecutive_success = 0

    if state.consecutive_success > config.decision_threshold:
        state.decision = Some(state.opinion)


def sample(nodes: List[SnowballState]) -> Callable[[int, int], List[Vote]]:
    def _sample(k: int, node_id: int):
        return [
           nodes[i].opinion for i in random.sample(list(range(len(nodes))), k+1) if i != node_id
        ][:k]
    return _sample


def simulate(nodes: List[SnowballState], config: SnowballConfig, max_ttf: int) -> Generator[Dict[Vote, int], None, None]:
    ttf = 0
    sample_query = sample(nodes)
    while not all(node.decision.is_some for node in nodes) and ttf < max_ttf:
        yield Counter(node.opinion for node in nodes)
        non_decided = (
            (node_id, node_state) for node_id, node_state in enumerate(nodes) if node_state.decision.is_empty
        )
        for node_id, node_state in non_decided:
            update_state(node_id, node_state, config, sample_query)


def generate_random_nodes(size: int, weights: Tuple[float, float]) -> List[SnowballState]:
    return [
        SnowballState(opinion=opinion, consecutive_success=0, decision=Empty())
        for opinion in random.choices([VOTE_YES, VOTE_NO], weights=weights, k=size)
    ]


def plot_history(history: List[Dict[Vote, int]]):
    import seaborn as sbn
    import matplotlib.pyplot as plt
    yes, no = zip(*((x[VOTE_YES], x[VOTE_NO]) for x in history))
    sbn.lineplot(data={"yes": yes, "no": no})
    plt.show()


if __name__ == "__main__":
    n = 400
    k = 10
    alpha = 8
    beta = 20

    config = SnowballConfig(alpha, k, beta)

    nodes = generate_random_nodes(n, (0.55, 0.45))

    history_states = list(simulate(nodes, config, 100))

    plot_history(history_states)