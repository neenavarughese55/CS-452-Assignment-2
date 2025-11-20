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
        for _ in range(rows):
            value = data.readline().strip().split()
            if len(value) != cols:
                raise ValueError(f"Expected {cols} values per row, got {len(value)}")
            grid.append(value)

    if verbosity >= 1:
        print(f"* Reading puzzle from [{filename}]")
    if verbosity >= 2:
        print("** Puzzle")
        for row in grid:
            print(' '.join(row))
    return grid, rows, cols

def build_csp(grid, dictionary, verbosity=0):
    variables = []
    var_dict = {}
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # Helper: any non-# cell is fillable
    def is_fillable(r, c):
        return grid[r][c] != '#'

    # Find across words
    for i in range(rows):
        j = 0
        while j < cols:
            if is_fillable(i, j):
                # Check if it is the start of an across word
                if j == 0 or not is_fillable(i, j-1):
                    # measure length
                    length = 0
                    jj = j
                    while jj < cols and is_fillable(i, jj):
                        length += 1
                        jj += 1
                    
                    # Only create variable if length > 1
                    if length > 1:
                        val = grid[i][j]
                        label = val if val.isdigit() else f"{i}_{j}"
                        name = f"X{label}a"
                        var = Variable(name, 'across', (i, j), length)
                        variables.append(var)
                        var_dict[name] = var
                    
                    j = jj  # Move to position after this word
                else:
                    j += 1  # Not start of word, move to next cell
            else:
                j += 1  # Not fillable, move to next cell

    # Find down words 
    for j in range(cols):
        i = 0
        while i < rows:
            if is_fillable(i, j):
                # Check if it is the start of a down word
                if i == 0 or not is_fillable(i-1, j):
                    # measure length
                    length = 0
                    ii = i
                    while ii < rows and is_fillable(ii, j):
                        length += 1
                        ii += 1
                    
                    # Only create variable if length > 1
                    if length > 1:
                        val = grid[i][j]
                        label = val if val.isdigit() else f"{i}_{j}"
                        name = f"X{label}d"
                        var = Variable(name, 'down', (i, j), length)
                        variables.append(var)
                        var_dict[name] = var
                    
                    i = ii  # Move to position after this word
                else:
                    i += 1  # Not start of word, move to next cell
            else:
                i += 1  # Not fillable, move to next cell

    # Initialise domains by length
    words_by_length = {}
    for word in dictionary:
        words_by_length.setdefault(len(word), []).append(word)

    for var in variables:
        var.domain = sorted(words_by_length.get(var.length, []))

    position_to_vars = {}

    # Get all positions occupied by variables
    for var in variables:
        r, c = var.start_pos
        for pos in range(var.length):
            if var.direction == 'across':
                current_pos = (r, c + pos)
            else:
                current_pos = (r + pos, c)
            position_to_vars.setdefault(current_pos, []).append((var, pos))
    
    # Build constraints and adjacency lists
    constraints = []
    adjacency = {var.name: [] for var in variables}
    for pos, var_list in position_to_vars.items():
        if len(var_list) > 1:
            for i in range(len(var_list)):
                for j in range(i + 1, len(var_list)):
                    var1, pos1 = var_list[i]
                    var2, pos2 = var_list[j]
                    constraint = Constraint(var1, var2, pos1, pos2)
                    constraints.append(constraint)
                    adjacency[var1.name].append(constraint)
                    adjacency[var2.name].append(constraint)

    if verbosity >= 1:
        print(f"* CSP has {len(variables)} variables")
        print(f"* CSP has {len(constraints)} constraints")

    return {'variables': variables, 'constraints': constraints, 'var_dict': var_dict, 'adjacency': adjacency}

def select_unassigned_variable(assignment, csp, method):
    # Select next variable using specified heuristic
    unassigned = [var for var in csp['variables'] if var.name not in assignment]
    if not unassigned:
        return None

    # Static ordering by puzzle number, across before down
    if method == 'static':
        def sort_key(var):
            body = var.name[1:-1]
            try:
                num = int(body)
                return (num, 0 if var.name[-1]=='a' else 1)
            except:
                return (999999, var.name)
        return sorted(unassigned, key=sort_key)[0]
    
    # Minimum remaining values heuristic
    if method == 'mrv':
        return min(unassigned, key=lambda var: len(var.domain))
    
    # Degree heuristic, variable involved in most constraints
    if method == 'deg':
        def count_constraints(var):
            return len(csp['adjacency'].get(var.name, []))
        return max(unassigned, key=count_constraints)
    
    if method == 'mrv+deg':
        mrv_sorted = sorted(unassigned, key=lambda var: len(var.domain))
        min_domain_size = len(mrv_sorted[0].domain)
        tied_vars = [var for var in mrv_sorted if len(var.domain) == min_domain_size]
        
        if len(tied_vars) == 1:
            return tied_vars[0]
        else:
            return select_unassigned_variable(assignment, csp, 'deg')
        
    return unassigned[0]
        
def order_domain_values(var, assignment, csp, method):
    # order domain values using specified heuristic
    if method == 'static':
        return sorted(var.domain) # Alphabetical order
    
    elif method == 'lcv':
        value_scores = []
        neighbours = []
        # For each constraint involving this variable
        for constraint in csp['adjacency'].get(var.name, []):
            if constraint.var1.name == var.name:
                neighbour = constraint.var2
                pos_self = constraint.pos1
                pos_neighbour = constraint.pos2
            else:
                neighbour = constraint.var1
                pos_self = constraint.pos2
                pos_neighbour = constraint.pos1

            if neighbour.name not in assignment:
                neighbours.append((neighbour, pos_self, pos_neighbour))

        # Count how many values remain for other variable
        for val in var.domain:
            total = 0
            for neighbour, pos_self, pos_neighbour in neighbours:
                count = 0
                for nv in neighbour.domain:
                    if val[pos_self] == nv[pos_neighbour]:
                        count += 1
                total += count
            value_scores.append((val, total))

        # Sort by score descending (higher score = less constraining)
        value_scores.sort(key=lambda x: x[1], reverse=True)
        return [value for value, _ in value_scores]
    
    return sorted(var.domain) # Default to static
        
def is_consistent(var, value, assignment, csp, forward_check):
    # Check consistency with already assigned neighbours
    for constraint in csp['adjacency'].get(var.name, []):
        if constraint.var1.name == var.name:
            other_var = constraint.var2
            pos_self = constraint.pos1
            pos_other = constraint.pos2
        else:
            other_var = constraint.var1
            pos_self = constraint.pos2
            pos_other = constraint.pos1

        if other_var.name in assignment:
            other_value = assignment[other_var.name]
            if value[pos_self] != other_value[pos_other]:
                return False
                
        # Limited forward checking
    if forward_check:
        for constraint in csp['adjacency'].get(var.name, []):
            if constraint.var1.name == var.name:
                other_var = constraint.var2
                pos_self = constraint.pos1
                pos_other = constraint.pos2
            else:
                other_var = constraint.var1
                pos_self = constraint.pos2
                pos_other = constraint.pos1
                
            if other_var.name not in assignment:
                    has_valid = False
                    for ov in other_var.domain:
                        if value[pos_self] == ov[pos_other]:
                            has_valid = True
                            break
                    if not has_valid:
                        return False
    return True
    
def backtrack(assignment, csp, args, stats, depth):
    # Recursive backtracking function
    stats['recursive_calls'] += 1

    # If assignment is complete, return it
    if len(assignment) == len(csp['variables']):
        if args.verbosity >= 2:
            print("  " * depth + "Assignment is complete!")
        return assignment
    
    # Select unassigned variable
    var = select_unassigned_variable(assignment, csp, args.variable_selection)
    if var is None:
        return None

    if args.verbosity >= 2:
        print("  " * depth + f"Trying variable {var.name} (domain size {len(var.domain)})")

    # Try values in order
    for value in order_domain_values(var, assignment, csp, args.value_order):
        if is_consistent(var, value, assignment, csp, args.limited_forward_check):
            # Add to assignment
            assignment[var.name] = value

            if args.verbosity >= 2:
                print("  " * depth + f"Assign {var.name} = {value}")

            # Recursive call
            result = backtrack(assignment, csp, args, stats, depth + 1)
            if result is not None:
                return result
                
            # Backtrack
            if args.verbosity >= 2:
                print("  " * depth + f"Backtracking on {var.name}")
            del assignment[var.name]
        else:
            if args.verbosity >= 2:
                print("  " * depth + f"Value {value} inconsistent for {var.name}")

    return None # Failure

def backtracking_search(csp, args, stats):
    # Backtracking search algorithm
    if args.verbosity >= 1:
        print("* Attempting to solve crossword puzzle...")
    if args.verbosity >= 2:
        print("** Running backtracking search...")
    return backtrack({}, csp, args, stats, 0)

def display_solution(assignment, original_grid, csp):
    rows = len(original_grid)
    cols = len(original_grid[0])
    out = [[' ' for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if original_grid[r][c]== '#':
                out[r][c] = ' '

    # Fills in the solution for each variable
    for var_name, word in assignment.items():
        # Finds which variable this is
        var = next((v for v in csp['variables'] if v.name == var_name), None)
        if var:
            r, c = var.start_pos

            # Place each letter of the word in the grid
            for k, ch in enumerate(word):
                if var.direction == 'across':
                        out[r][c + k] = ch
                else: # Down
                    if r + k < rows:
                        out[r + k][c] = ch

    # Display the final grid
    for r in range(rows):
        print(''.join(out[r]))

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
            print("FAILED; ", end="")
        print(f"Solving took {stats['elapsed_time']}ms ({stats['recursive_calls']} recursive calls)")

        if solution:
            display_solution(solution, grid, csp)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
