# Crossword Puzzle Solver
# Neena Varughese

import argparse
import sys
import time

class Variable:
    def __init__(self, name, direction, start_pos, length):
        self.name = name
        self.direction = direction
        self.start_pos = start_pos
        self.length = length
        self.domain = []