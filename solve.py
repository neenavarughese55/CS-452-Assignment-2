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
        self.length = length 
        self.domain = [] # list of possible words