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

    # Find constraints
    constraints = []
    position_to_vars = {}

    # Get all positions occupied by var1 and var2
    for var in variables:
        row, col = var.start.pos
        for pos in range(var.length):
            if var.direction == 'across':
                current_pos = (row, col + pos)
            else:
                current_pos = (row + pos, col)

            if current_pos not in position_to_vars:
                position_to_vars[current_pos] = []
            position_to_vars[current_pos].append((var, pos))

    for pos, var_list in position_to_vars.items():
        if len(var_list) > 1:
            for i in range(len(var_list)):
                for j in range(i + 1, len(var_list)):
                    var1, pos1 = var_list[i]
                    var2, pos2 = var_list[j]
                    constraints.append(Constraint(var1, var2, pos1, pos2))

    if verbosity >= 1:
        print(f"* CSP has {len(variables)} variables")
        print(f"* CSP has {len(constraints)} constraints")

    return {'variables': variables, 'constraints': constraints, 'var_dict': var_dict}

def select_unassigned_variable(assignment, csp, method):
    # Select next variable using specified heuristic
    unassigned = [var for var in csp['variables'] if var.name not in assignment]

    # Static ordering by puzzle number, across before down
    if method == 'static':
        def sort_key(var):
            num = int(var.name[1:-1])
            direction = 0 if var.name[-1] == 'a' else 1
            return (num, direction)
        return sorted(unassigned, key=sort_key)[0]
    
    # Minimum remaining values heuristic
    elif method == 'mrv':
        return min(unassigned, key=lambda var: len(var.domain))
    
    # Degree heuristic, variable involved in most constraints
    elif method == 'deg':
        def count_constraints(var):
            count = 0
            for constraint in csp['constraints']:
                if constraint.var1.name == var.name or constraint.var2.name == var.name:
                    count += 1
            return count
        return max(unassigned, key=count_constraints)
    
    elif method == 'mrv+deg':
        mrv_sorted = sorted(unassigned, key=lambda var: len(var.domain))
        min_domain_size = len(mrv_sorted[0].domain)
        tied_vars = [var for var in mrv_sorted if len(var.domain) == min_domain_size]
        
        if len(tied_vars) == 1:
            return tied_vars[0]
        else:
            return select_unassigned_variable(assignment, csp, 'deg')
        
def order_domain_values(var, assignment, csp, method):
    # order domain values using specified heuristic
    if method == 'static':
        return sorted(var.domain) # Alphabetical order
    elif method == 'lcv':
        value_scores = []
        for value in var.domain:
            score = 0
            # For each constraint involving this variable
            for constraint in csp['constraints']:
                if constraint.var1.name == var.name:
                    other_var = constraint.var2
                    if other_var.name not in assignment:
                        # Count how many values remain for other variable
                        for other_value in other_var.domain:
                            if value[constraint.post1] == other_value[constraint.pos2]:
                                score += 1
                elif constraint.var2.name == var.name:
                    other_var = constraint.var1
                    if other_var.name not in assignment:
                        for other_value in other_var.domain:
                            if value[constraint.pos2] == other_value[constraint.pos1]:
                                score += 1

            value_scores.append((value, score))
        value_scores.append((value, score))
        return [value for value, _ in value_scores]
        
def is_consistent(var, value, assignment, csp, forward_check):
    # Check if assignment is consistent
    # Basic consistency check
    for constraint in csp['constraints']:
        if constraint.var1.name == var.name and constraint.var2.name in assignment:
            other_value = assignment[constraint.var2.name]
            if value[constraint.pos1] != other_value[constraint.pos2]:
                return False
            elif constraint.var2.name == var.name and constraint.var1.name in assignment:
                other_value = assignment[constraint.var1.name]
                if value[constraint.pos2] != other_value[constraint.pos1]:
                    return False
                
        if forward_check:
            for constraint in csp['constraints']:
                if constraint.var1.name == var.name and constraint.var2.name not in assignment:
                    # Check if any value in other domain statisfies constraint
                    other_var = constraint.var2
                    has_valid_value = False
                    for other_value in other_var.domain:
                        if value[constraint.pos1] == other_value[constraint.pos2]:
                            has_valid_value = True
                            break
                        if not has_valid_value:
                            return False
                        elif constraint.var2.name == var.name and constraint.var1.name not in assignment:
                            other_var = constraint.var1
                            has_valid_value = False
                            for other_value in other_var.domain:
                                if value[constraint.pos2] == other_value[constraint.pos1]:
                                    has_valid_value = True
                                    break
                            if not has_valid_value:
                                return False
        return True
    
def backtrack(assignment, csp, args, stats, depth):
    # Recursive backtracking function
    stats['recursive_calls'] += 1

    # If assignment is complete, return it
    if len(assignment) == len(csp['variable']):
        if args.verbosity >= 2:
            print(" " * depth + "Assignment is complete!")
        return assignment
    
    # Select unassigned variable
    var = select_unassigned_variable(assignment, csp, args.variable_selection)

    if args.verbosity >= 2:
        indent = " " * depth
        print(f"{indent}Backtrack Call: ")
        print(f"{indent}Trying values for {var.name}")

    # Try values in order
    for value in order_domain_values(var, assignment, csp, args.value_order):
        if is_consistent(var, value, assignment, csp, args.limited_forward_check):
            # Add to assignment
            assignment[var.name] = value

            if args.verbosity >= 2:
                indent = " " * depth
                print(f"{indent}Assignment {{ {var.name} = {value} }} is consistent")

                # Recursive call
                result = backtrack(assignment, csp, args, stats, depth + 1)
                if result is not None:
                    return result
                
                # Backtrack
                del assignment[var.name]
            else:
                if args.verbosity >= 2:
                    indent = " " * depth
                    print(f"{indent}Assignment {{ {var.name} = {value} }} is inconsistent")

    if args.verbosity >= 2:
        indent = " " * depth
        print(f"{indent}Failed call; backtracking...")
    return None # Failure

def backtracking_search(csp, args, stats):
    # Backtracking search algorithm
    assignment = {}
    if args.verbosity >= 1:
        print("* Attempting to solve crossword puzzle...")
    if args.verbosity >= 2:
        print("** Running backtracking search...")
    return backtrack(assignment, csp, args, stats, 0)

def display_solution(assignment, original_grid):
    grid = [row[:] for row in original_grid]
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    for var_name, word in assignment.items():
        var_num = var_name[1:-1]
        direction = var_name[-1]
        start_row, start_col = -1, -1

        for i in range(rows):
            for j in range(cols):
                if grid[i][j] == var_num:
                    start_row, start_col = i, j
                    break
            if start_row != -1:
                break

        if start_row != -1:
            for k in range(len(word)):
                if direction == 'a':
                    if j + k < cols:
                        grid[i][j + k] = word[k]
                else:
                    if i + k < rows:
                        grid[i + k][j] = word[k]

    for row in grid:
        display_row = []
        for cell in row:
            if cell == '#':
                display_row.append(' ')
            else:
                display_row.append(cell)
        print(''.join(display_row))

def main():
    parser = argparse.ArgumentParser(description='Crossword Puzzle Solver')
    parser.add_argument('-d', dest='dictionary_file', required=True)
    parser.add_argument('-p', dest='puzzle_file', required=True)
    parser.add_argument('-v', dest='verbosity', type=int, default=0)
    parser.add_argument('-vs', '--variable-selection', choices=['static', 'mrv', 'deg', 'mrv+deg'], default='static')
    parser.add_argument('-vo', '--value-order', choices=['static', 'lcv'], default='static')
    parser.add_argument('-lfc', '--limited-forward-check', action='store_true')

    args = parser.parse_args()
    start_time = time.time()
    stats = {'recursive_calls': 0, 'start_time': start_time}

    # Solve the puzzle
    try:
        dictionary = load_dictionary(args.dictionary_file, args.verbosity)
        grid, rows, cols = parse_puzzle(args.puzzle_file, args.verbosity)
        csp = build_csp(grid, dictionary, args.verbosity)
        solution = backtracking_search(csp, args, stats)
        stats['elapsed_time'] = int((time.time() - start_time) * 1000)

        # Output results
        if solution is not None:
            print("SUCCESS! ", end="")
        else:
            print("FAILED ", end="")
        print(f"Solving took {stats['elapsed_time']}ms ({stats['recursive_calls']} recursive calls)")

        if solution:
            display_solution(solution, grid)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
