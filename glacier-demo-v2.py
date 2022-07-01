from random import sample

# snowball consensus demo - no byzantine

# define parameters

# n: number of participants
n = 1000

# k (sample size): between 1 and n | bigger the k the faster the conversion
k = 10

# alpha (quorum size): between 1 and k
alpha = 2

# beta (decision threshold): >= 1
beta = 1


# preference := pizza
# n size list w/ each term n having it's own preference
node_list = [True for i in range(n)]

# success counter for each node
node_counter = [0 for i in range(n)]

# node decision
node_decision = [None for i in range(n)]

while not all(node_decision): # returns false if any None exist - truthy, any is falsy
    for node_index in range(n):
        sample_response = sample(node_list, k)
        previous_preference = node_list[node_index]
        # count how many truth
        sample_response_count = sample_response.count(previous_preference)

        # change node decision to align with majority opinion from sampled size
        # compare previous node opinion with majority opinion to increment counter if opinion is unchanged
        if sample_response_count >= alpha:
            node_counter[node_index] += 1
        else:
            node_counter[node_index] = 1
            node_list[node_index] = not previous_preference
    else:
        node_counter[node_index] = 0
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