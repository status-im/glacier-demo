from random import sample
from random import choices
import matplotlib.pyplot as plt
import seaborn as sbn
from collections import Counter

# snowball consensus demo - no byzantine

### define parameters

# n: number of participants
n = 400

# k (sample size): between 1 and n | bigger the k the faster the conversion
k = 20

# alpha (quorum size): between 1 and k
alpha = 14

# beta (decision threshold): >= 1
beta = 20


# preference := pizza
# n size list w/ each term n having it's own preference
node_preference = [choices([True, False], weights=[60, 40])[0] for i in range(n)]

# success counter for each node
node_counter = [0 for i in range(n)]

# node decision
node_decision = [None for i in range(n)]
x_axis = []

while not all(x is not None for x in node_decision): # returns false if any None exist - truthy, any is falsy
    for node_index in (i for i, d in enumerate(node_decision) if d is None):
        sample_response = sample(node_preference, k)
        print(sample_response)
        previous_preference = node_preference[node_index]
        # count how many truth
        sample_response_count = sample_response.count(previous_preference)
        print(sample_response_count)
        not_preference_count = len(sample_response)-sample_response_count
        # change node decision to align with majority opinion from sampled size
        # compare previous node opinion with majority opinion to increment counter if opinion is unchanged
        if sample_response_count >= alpha:
            node_counter[node_index] += 1
        elif not_preference_count >= alpha:
            node_counter[node_index] = 1
            node_preference[node_index] = not previous_preference
        else:
            node_counter[node_index] = 0
        if node_counter[node_index] > beta:
            node_decision[node_index] = node_preference[node_index]
    x_axis.append(node_preference.copy()) # read up on append command
print(node_decision)

#plot two lines, one w/ yes and one w/ no

x_axis = list(zip(*[Counter(x) for x in x_axis]))
sbn.lineplot(data = x_axis)
plt.show()
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