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