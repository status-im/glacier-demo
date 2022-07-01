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
from typing import Callable, List, Generator, Dict
import random
from collections import Counter
from rusty_results import Option


class Vote:
    __slots__ = []

    def flip(self):
        raise NotImplementedError


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


def sample(nodes: List[SnowballState]) -> List[Vote]:
    def _sample(k: int, node_id: int):
        return [nodes[i].opinion for i in random.sample(list(range(len(nodes))), k+1) if i != node_id][:k]
    return _sample


def simulate(nodes: List[SnowballState], config: SnowballConfig, max_ttf: int) -> Generator[Dict[Vote, int], None, None]:
    ttf = 0
    sample_query = sample(nodes)
    while not all(node.decision.is_some for node in nodes) and ttf < max_ttf:
        yield Counter(node.opinion for node in nodes)
        for node_id, node_state in enumerate(nodes):
            update_state(node_id, node_state, config, sample_query)


