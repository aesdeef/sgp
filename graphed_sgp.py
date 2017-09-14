#! /usr/bin/python

# Finds a perfect solution of the Social Golfer Problem given g and p
# Might be slow and require a lot of memory for bigger problems

import networkx as nx
from networkx.algorithms.approximation.clique import max_clique
from sys import argv
from itertools import combinations, chain

TABLES = 10 if len(argv) == 1 else int(argv[1])
PLAYERS_AT_TABLE = 4 if len(argv) <= 2 else int(argv[2])
NO_OF_PLAYERS = PLAYERS_AT_TABLE * TABLES

def all_k_cliques(graph, k):
    return map(tuple, chain.from_iterable(combinations(clq, k) for clq in nx.find_cliques(graph) if len(clq)>=k))
def all_pairs(tables):
    return map(tuple, chain.from_iterable(combinations(table, 2) for table in tables))

G = nx.complete_graph(NO_OF_PLAYERS)
print("graph G generated")
# print(G.nodes())
# print(G.edges())
H = nx.Graph()
H.add_nodes_from(all_k_cliques(G, PLAYERS_AT_TABLE))
for node, node2 in combinations(H.nodes(), 2):
    if len(set(node) & set(node2)) == 0:
        H.add_edge(node, node2)
print("graph H generated")
# print(H.nodes())
# print(H.edges())
I = nx.Graph()
I.add_nodes_from(all_k_cliques(H, TABLES))
print("graph I - added nodes")
for node, node2 in combinations(I.nodes(), 2):
    no_repeats = True
    pairs = set(all_pairs(node))
    for pair in all_pairs(node2):
        if pair in pairs:
            no_repeats = False
            break
    if no_repeats:
        I.add_edge(node, node2)
# print(I.nodes())
# print(I.edges())
print("graph I - added edges")
k_max = int((NO_OF_PLAYERS - 1) / (PLAYERS_AT_TABLE - 1))
found = False
while not found:
    for solution in all_k_cliques(I, k_max):
        found = True
        print(solution)
        print(k_max)
        break
    k_max -= 1
# print(max_clique(I))
