#! /usr/bin/python

# Finds a random solution for g-4-w instances of the Social Golfer Problem given g and trying to maximise w

from random import shuffle, choice
from itertools import combinations
from sys import argv

TABLES = 10 if len(argv) == 1 else int(argv[1])
NO_OF_PLAYERS = 4 * TABLES
FAILURES_LIMIT = 1_000_000

def random_tables(players):
    # Returns a list of TABLES random tables from possible_tables such that no player is included in more than one table
    # or None if fails to find a valid set within FAILURES_LIMIT tries
    tables = []
    options = possible_tables.copy()
    failures = 0
    if len(options) == 0:
        return None
    while len(tables) < TABLES:
        if len(options) == 0:
            tables = []
            options = possible_tables.copy()
            failures += 1
        if failures >= FAILURES_LIMIT:
            return None
        pick = choice(tuple(options))
        tables.append(pick)
        players = set(pick)
        options = set(x for x in options if len(players & set(x)) == 0)
    return tables

def play_round(tables):
    # Removes all tables from possible_tables that contain a pair included in any of the tables in tables
    for table in tables:
        pairs = set(combinations(table, 2))
        global possible_tables
        possible_tables = set(x for x in possible_tables if len(pairs & set(combinations(x,2))) == 0)

if __name__ == '__main__':
    players = list(range(NO_OF_PLAYERS))
    possible_tables = set(combinations(players, 4))
    rounds = 0
    while True:
        tables = random_tables(players)
        if tables:
            rounds += 1
            play_round(tables)
            for i, table in enumerate(tables):
                table = list(table)
                shuffle(table)
                tables[i] = tuple(table)
            print("Round %d\a" % rounds)
            print(tables)
        else:
            print('---')
            break
