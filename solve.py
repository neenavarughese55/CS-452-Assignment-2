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
    # Parse puzzle grid from file
    with open(filename, 'r') as data:
        # Read dimensions
        first_line = data.readline().strip()
        rows, cols = map(int, first_line.split())

        # Read grid
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

def build_csp(grid, dictionary, verbosity=0):
    variables = []
    var_dict = {}
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # Find across words
    for i in range(rows):
        j = 0
        while j < cols:
            if grid[i][j].isdigit(): # Start of a word
                start_j = j
                number = grid[i][j]
                length = 0

                # Calculate word length
                is_start_of_across = (j == 0 or grid[i][j-1] == '#')
                while j < cols and grid[i][j] != '#':
                    length += 1
                    j += 1
                
                if is_start_of_across and length > 1: # Single letter words don't count
                    var_name = f"X{number}a"
                    var = Variable(var_name, 'across', (i, start_j), length)
                    variables.append(var)
                    var_dict[var_name] = var
                j += 1
            else:
                j +=1

    # Find down words
    for j in range(cols):
        i = 0
        while i < rows:
            if grid[i][j].isdigit():
                start_i = i
                number = grid[i][j]
                length = 0
                is_start_of_down = (i == 0 or grid[i-1][j] == '#')
                while i < rows and grid[i][j] != '#':
                    length += 1
                    i += 1
                
                if is_start_of_down and length > 1:
                    var_name = f"X{number}d"
                    var = Variable(var_name, 'down', (start_i, j), length)
                    variables.append(var)
                    var_dict[var_name] = var
                i += 1
            else:
                i += 1

    # Initialise domains
    words_by_length = {}
    for word in dictionary:
        length = len(word)
        if length not in words_by_length:
            words_by_length[length] = []
        words_by_length[length].append(word)

    for var in variables:
        if var.length in words_by_length:
            var.domains = sorted(words_by_length[var.length])