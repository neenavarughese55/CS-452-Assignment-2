# CS-452-Assignment-2

Crossword Puzzle Solver - CS 452 Assignment 2
Overview
This is a crossword puzzle solver implemented using Constraint Satisfaction Problems (CSP) with backtracking search. The program reads crossword puzzle layouts and dictionary files, then solves the puzzles using various search heuristics and constraint checking techniques.


Requirements
Python 3.6 or higher

Standard libraries only: argparse, sys, time


Usage:
Basic Command
python3 solve.py -d <dictionary_file> -p <puzzle_file> [options]

Examples of how to run
# Basic Usage
python3 solve.py -d a02-data/dictionary-small.txt -p a02-data/xword00.txt

# With Heuristics and Verbosity
python3 solve.py -d a02-data/dictionary-small.txt -p a02-data/xword00.txt -vs mrv -vo lcv -v 1

# With Limited Forward Checking
python3 solve.py -d a02-data/dictionary-medium.txt -p a02-data/xword01.txt -lfc -v 2

Testing Different Puzzles

# Small puzzle with small dictionary
python3 solve.py -d a02-data/dictionary-small.txt -p a02-data/xword00.txt -v 1

# Medium puzzle with medium dictionary  
python3 solve.py -d a02-data/dictionary-medium.txt -p a02-data/xword01.txt -v 1

# Complex puzzle (should fail with small dictionary)
python3 solve.py -d a02-data/dictionary-small.txt -p a02-data/xword02.txt -v 1

## Known Issue:
The forward checking does not seem to working