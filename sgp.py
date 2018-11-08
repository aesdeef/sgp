#! /usr/bin/python

import networkx as nx
from random import shuffle, choice, randrange, sample, random
from itertools import combinations, permutations, chain
from collections import Counter
from math import floor, ceil
from sys import argv
from functools import lru_cache

TABLES = 10 if len(argv) == 1 else int(argv[1])
ROUNDS = 4 if len(argv) <= 2 else int(argv[2])
TRESHOLD = 200 if len(argv) <= 3 else int(argv[3])
NO_OF_PLAYERS = 4 * TABLES
spreadsheet_friendly_output = True

def random_tables(possible_tables):
    def _random_tables(possible_tables, tables):
        if len(tables) == TABLES:
            return tables
        if not possible_tables:
            return False
        for table in possible_tables:
            players = set(table)
            new_possible_tables = (x for x in possible_tables if len(players & set(x)) == 0)
            r = _random_tables(new_possible_tables, tables+[table])
            if r:
                return r
        return False
    return _random_tables(possible_tables, [])

def schedule(possible_tables, G):
    def _schedule(possible_tables, rounds, G):
        print(len(rounds), flush=True)
        if len(rounds) == ROUNDS:
            return rounds
        if not possible_tables and len(rounds) % 4 == 0:
            possible_tables = list(map(list, chain.from_iterable(combinations(clq, 4) for clq in nx.find_cliques(G) if len(clq)>=4)))
            for table in possible_tables:
                shuffle(table)
        for _ in range(10 if len(rounds) < TABLES-1 else 1):
            shuffle(possible_tables)
            round_ = random_tables(possible_tables)
            if not round_:
                continue
            new_G = G.copy()
            new_possible_tables = possible_tables.copy()
            pairs = set(chain.from_iterable(combinations(sorted(table), 2) for table in round_))
            for pair in pairs:
                try:
                    assert(G.has_edge(*pair))
                except AssertionError:
                    print(rounds, round_, flush=True)
                    raise AssertionError
            new_G.remove_edges_from(pairs)
            new_possible_tables = list(x for x in new_possible_tables if len(pairs & set(combinations(sorted(x), 2))) == 0)
            r = _schedule(list(new_possible_tables), rounds+(round_,), new_G)
            if r:
                return r
        return False
    return _schedule(possible_tables, tuple(), G)

def set_winds(rounds, players):
    def list_winds(rounds, player):
        winds = []
        for round_ in rounds:
            for table in round_:
                if player in table:
                    winds.append(table.index(player))
                    break
        return winds
    def eval_winds(winds):
        min_rounds = floor(ROUNDS/4)
        max_rounds = ceil(ROUNDS/4)
        score = 0
        counted = Counter(winds)
        for i in range(4):
            if counted[i] < min_rounds:
                score += pow(3, min_rounds - counted[i])
            elif counted[i] > max_rounds:
                score += pow(3, counted[i] - max_rounds)
        return score
    winds = {i: list_winds(rounds, i) for i in players}
    score = {i: eval_winds(winds[i]) for i in players}
    sum_of_scores = sum(score.values())
    while sum_of_scores:
        table_score = {}
        for r, round_ in enumerate(rounds):
            for t, table in enumerate(round_):
                table_score[(r, t)] = sum(score[player] for player in table)
        for r, t in sorted(table_score, key=table_score.get):
            best_new_table = None
            best_improvement = -1
            best_new_scores = None
            for new_table in permutations(rounds[r][t]):
                new_scores = {}
                for player in new_table:
                    new_scores[player] = eval_winds(winds[player][:r]+[new_table.index(player)]+winds[player][r+1:])
                improvement = table_score[(r, t)] - sum(new_scores.values())
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_new_table = new_table
                    best_new_scores = new_scores
            if best_improvement > 0:
                break
        if best_improvement == 0:
            r = randrange(len(rounds))
            t = randrange(len(rounds[0]))
            shuffle(rounds[r][t])
        else:        
            rounds[r][t] = list(best_new_table)
        winds = {i: list_winds(rounds, i) for i in players}
        score = {i: eval_winds(winds[i]) for i in players}
        sum_of_scores = sum(score.values())
    return rounds

def improve(rounds, sum_of_scores):
    rounds = untuple_rounds(rounds)
    improvement = {}
    for r in range(len(rounds)):
        for a, b in combinations(range(TABLES), 2):
            rounds[r][a], rounds[r][b] = rounds[r][b], rounds[r][a]
            new_tables = {i: list_tables(rounds, i) for i in players}
            new_score = {i: eval_tables(new_tables[i]) for i in players}
            new_sum = sum(new_score.values())
            change = sum_of_scores - new_sum
            rounds[r][a], rounds[r][b] = rounds[r][b], rounds[r][a]
            if change > 0:
                improvement[(r, a, b)] = change
    if len(improvement) == 0:
        return None
    return max(improvement, key=improvement.get)

def improve_twice(rounds, sum_of_scores):
    rounds = untuple_rounds(rounds)
    improvement = {}
    rr = list(combinations(chain.from_iterable((range(len(rounds)) for i in range(2))), 2))
    shuffle(rr)
    ab1 = list(combinations(range(TABLES), 2))
    shuffle(ab1)
    ab2 = list(combinations(range(TABLES), 2))
    shuffle(ab2)
    for r1, r2 in rr:
        for a1, b1 in ab1:
            for a2, b2 in ab2:
                rounds[r1][a1], rounds[r1][b1] = rounds[r1][b1], rounds[r1][a1]
                rounds[r2][a2], rounds[r2][b2] = rounds[r2][b2], rounds[r2][a2]
                new_tables = {i: list_tables(rounds, i) for i in players}
                new_score = {i: eval_tables(new_tables[i]) for i in players}
                new_sum = sum(new_score.values())
                change = sum_of_scores - new_sum
                rounds[r2][a2], rounds[r2][b2] = rounds[r2][b2], rounds[r2][a2]
                rounds[r1][a1], rounds[r1][b1] = rounds[r1][b1], rounds[r1][a1]
                if change > 0:
                    return (r1, a1, b1, r2, a2, b2)
    return None

def list_tables(rounds, player):
    tables = []
    for round_ in rounds:
        for t, table in enumerate(round_):
            if player in table:
                tables.append(t)
                break
    return tuple(tables)

@lru_cache(maxsize=256000)
def eval_tables(tables):
    min_rounds = floor(ROUNDS/TABLES)
    max_rounds = ceil(ROUNDS/TABLES)
    score = 0
    counted = Counter(tables)
    for i in range(TABLES):
        if counted[i] < min_rounds:
            score += pow(3, min_rounds - counted[i])
        elif counted[i] > max_rounds:
            score += pow(3, counted[i] - max_rounds)
    return score

def reorder(rounds):
    def put_back(rounds, so_far, tables):
        if not tables:
            return so_far
        i = len(so_far)
        for t in tables:
            at_table_i = set(chain.from_iterable(r[i] for r in rounds))
            if not (set(t) & at_table_i):
                new_tables = tables.copy()
                new_tables.remove(t)
                step = put_back(rounds, so_far + [t], new_tables)
                if step:
                    return step
        return False
    saved_rounds = tuple_rounds(rounds)
    rr = list(range(len(saved_rounds)))
    shuffle(rr)
    for i in rr:
        new_rounds = untuple_rounds(saved_rounds)
        r = new_rounds[i]
        copy_r = r.copy()
        new_rounds = new_rounds[:i] + new_rounds[i+1:]
        shuffle(r)
        new_round = put_back(new_rounds, [], r)
        if new_round:
            if new_round != copy_r:
                return tuple_rounds(new_rounds + [new_round])
    return False


def set_tables(rounds, players, treshold=0):
    tables = {i: list_tables(rounds, i) for i in players}
    score = {i: eval_tables(tables[i]) for i in players}
    sum_of_scores = sum(score.values())
    min_rounds = floor(ROUNDS/TABLES)
    max_rounds = ceil(ROUNDS/TABLES)
    switch = 0
    pre_shuffle = set()
    best_score = 1000000
    best_rounds = None
    rounds = tuple_rounds(rounds)
    while sum_of_scores > treshold:
        if sum_of_scores < best_score:
            best_rounds = (score, tuple_rounds(rounds))
            if sum_of_scores == 0:
                break
        improvement = improve(rounds, sum_of_scores)
        if not improvement:
            new_rounds = reorder(rounds)
            if new_rounds:
                rounds = new_rounds
            else:
                rounds = untuple_rounds(rounds)
                for i in range(ROUNDS):
                    r = randrange(len(rounds))
                    a, b = sample(range(len(rounds[0])), 2)
                    rounds[r][a], rounds[r][b] = rounds[r][b], rounds[r][a]
                rounds = tuple_rounds(rounds)
        else:
            r, a, b = improvement
            rounds = untuple_rounds(rounds)
            rounds[r][a], rounds[r][b] = rounds[r][b], rounds[r][a]
            rounds = tuple_rounds(rounds)
        tables = {i: list_tables(rounds, i) for i in players}
        score = {i: eval_tables(tables[i]) for i in players}
        sum_of_scores = sum(score.values())
    return rounds

def tuple_rounds(rounds):
    return tuple(tuple(tuple(table) for table in round_) for round_ in rounds)

def untuple_rounds(rounds):
    return [[list(table) for table in round_] for round_ in rounds]

if __name__ == '__main__':
    print('preparations...', flush=True)
    players = list(range(1, NO_OF_PLAYERS+1))
    G = nx.complete_graph(players)
    possible_tables = list(map(list, combinations(players, 4)))
    for table in possible_tables:
        shuffle(table)
    print('creating a schedule...', flush=True)
    rounds = schedule(possible_tables, G)
    del(G)
    print('assigning starting winds...', flush=True)
    rounds = set_winds(rounds, players)
    print('assigning table numbers...', flush=True)
    rounds = set_tables(list(rounds), players, TRESHOLD)
    if not rounds:
        exit('Something went wrong.')
    while True:
        if spreadsheet_friendly_output:
            rows = [''] * NO_OF_PLAYERS
            for round_ in rounds:
                for i in range(TABLES):
                    rows[i*4+0] += f'E,{round_[i][0]},'
                    rows[i*4+1] += f'S,{round_[i][1]},'
                    rows[i*4+2] += f'W,{round_[i][2]},'
                    rows[i*4+3] += f'N,{round_[i][3]},'
            for row in rows:
                print(row)
        else:
            for i, round_ in enumerate(rounds, start=1):
                print(f'Round {i}', flush=True)
                for table in round_:
                    print(table, flush=True)
        if TRESHOLD > 0:
            new_treshold = int(input(f'current treshold = {TRESHOLD}, new treshold: '))
            if new_treshold < TRESHOLD:
                TRESHOLD = new_treshold
                rounds = set_tables(rounds, players, TRESHOLD)
            else:
                break
        else:
            break
