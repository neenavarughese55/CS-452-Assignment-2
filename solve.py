# Crossword Puzzle Solver
# Neena Varughese

import argparse
import sys
import time

class Variable:
    def __init__(self, name, direction, start_pos, length):
        self.name = name
        self.direction = direction # 'across' or 'down'
        self.start_pos = start_pos # (row, col) of starting square
        self.length = length # To find out the word length
        self.domain = [] # list of possible words

class Constraint:
    def __init__(self, var1, var2, pos1, pos2):
        self.var1 = var1 # first variable
        self.var2 = var2 # second variable
        self.pos1 = pos1 # position in var1 where they intersect
        self.pos2 = pos2 # position in var2 where they intersect

def load_dictionary(filename, verbosity=0):
    # Load dictionary words from file
    words = []
    with open(filename, 'r') as data:
        for line in data:
            word = line.strip().upper()
            if word: # Skip empty lines
                words.append(word)

    if verbosity >= 1:
        print(f"* Reading dictionary from [{filename}]")
    if verbosity >= 2:
        print(f"** Dictionary has {len(words)} words")
    return words

def parse_puzzle(filename, verbosity=0):
    with open(filename, 'r') as data:
        first_line = data.readline().strip()
        rows, cols = map(int, first_line.split())
        grid = []
        for i in range(rows):
            line = data.readline().strip()
            cells = line.split()
            grid.append(cells)

    if verbosity >=1:
        print(f"* Reading puzzle from [{filename}]")
    if verbosity >=2:
        print("** Puzzle")
        for row in grid:
            print(''.join(row))
    return grid, rows, cols