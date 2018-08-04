
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = [r + c for r in rows for c in cols]
history = {}

def assign_value(values, box, value):
    if values[box] == value:
        return values

    prev = values2grid(values)
    values[box] = value
    if len(value) == 1:
        history[values2grid(values)] = (prev, (box, value))
    return values

def cross(A, B):
    """Cross product of elements in A and elements in B """
    return [ x +y for x in A for y in B]


def values2grid(values):
    """Convert the dictionary board representation to as string

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    a string representing a sudoku grid.

        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    """
    res = []
    for r in rows:
        for c in cols:
            v = values[r + c]
            res.append(v if len(v) == 1 else '.')
    return ''.join(res)


def grid2values(grid):
    """Convert grid into a dict of {square: char} with '123456789' for empties.

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.

        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
            then the value will be '123456789'.
    """
    sudoku_grid = {}
    for val, key in zip(grid, boxes):
        if val == '.':
            sudoku_grid[key] = '123456789'
        else:
            sudoku_grid[key] = val
    return sudoku_grid

def gridExample(grid):
    sudoku_grid = {}
    for val, key in zip(grid, boxes):
        sudoku_grid[key] = val
    return sudoku_grid

def display(values):
    """Display the values as a 2-D grid.

    Parameters
    ----------
        values(dict): The sudoku in dictionary form
    """
    width = 1+ max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print()


def reconstruct(values, history):
    """Returns the solution as a sequence of value assignments 

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    history(dict)
        a dictionary of the form {key: (key, (box, value))} encoding a linked
        list where each element points to the parent and identifies the value
        assignment that connects from the parent to the current state

    Returns
    -------
    list
    """
    path = []
    prev = values2grid(values)
    while prev in history:
        prev, step = history[prev]
        path.append(step)
    return path[::-1]



row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
unitlist = row_units + column_units + square_units



# // DIAGONAL UNITS ------------------------------------------------
def calculateDiagonalUnits(inverse):
    increment = 0
    diagonal_units = []
    columns = cols
    if inverse:
        columns = cols[::-1]

    for rw in rows:
        dunit = (rows[increment] + columns[increment])
        diagonal_units.insert(increment, dunit)
        increment = increment + 1
    return diagonal_units
# -----------------------------------------------------------------//

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def naked_twins(values):
    # TODO: Implement this function!
    # Save all boxes Ids with 2 possible numbers
    twinBoxes = [boxName for boxName in values.keys() if len(values[boxName]) == 2]
    # Iterate through them
    for boxName in twinBoxes:
        # Save values in possible options
        possibleOptions = values[boxName]
        # Iterate through all the Block peers associated to each box with 2 options
        for peer in peers[boxName]:
            if (values[peer] == possibleOptions):
                # print("Found nakedTwin")
                # print("possibleOption is: " + boxName + " with value: " + possibleOptions + " and his nakedTwin is: " + peer + ": " + values[peer])

                # Get the peers they share
                sharedPeers = [nakedOne for nakedOne in peers[boxName] if nakedOne in peers[peer]]
                # print("Shared peers are: " + str(sharedPeers))
                for sharedPeerBox in sharedPeers:
                    # print("The values of sharedPeer: " + sharedPeerBox + " is: " + values[sharedPeerBox])
                    for possibleOption in possibleOptions:
                        values[sharedPeerBox] = values[sharedPeerBox].replace(possibleOption, '')
                        # print("The values of sharedPeer: " + sharedPeerBox + " is: " + values[sharedPeerBox])
    return values


def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit, '')
    return values


def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)

        # Implement Naked-Twins --------------
        values = naked_twins(values)
        # ------------------------------------
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    values = reduce_puzzle(values)
    if values is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values  ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt
            # raise NotImplementedError


def solve(grid):
    #print(unitlist)
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":

    print("Lets solve a Sudoku")
    print("Please indicate if you want to solve a Diagonal Sudoku by writing YES (only if you are sure). If not, please write NO: ")
    print("     A Diagonal Sudoku has its large diagonals with no repeating numbers")
    print("     IMPORTANT: Most Sudokus are not diagonal. Trying to solve it as so will result in an error")
    diagonalSudoku = input("Is it Diagonal?: ")

    if diagonalSudoku == "YES":
        diagonal_units = [calculateDiagonalUnits(False), calculateDiagonalUnits(True)]
        unitlist = unitlist + diagonal_units
        print("Thank you very much. We will try and solve a Diagonal Sudoku!")
    else:
        print("Thank you very much.")

    print(" ")
    print("To solve a Sudoku, please follow the next instructions")
    print("You must write the values of the unsolved Sudoku from left to right and up to down without blank spaces")
    print("     If one of the squares has a number, write it down, if it is blank, write a dot . ( . )")
    print(" ")
    print("For example, if you see this Sudoku: ")
    print(" ")
    display(gridExample('2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'))
    print(" ")
    print("You must input this: ")
    print("2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3")
    print("If you understood the instructions, lets proceed.")
    sudokuAResolver = input("Please write your Sudoku in the format explained in the previous instructions: ")
    print(" ")
    print("############################################################")


    diag_sudoku_grid = sudokuAResolver

    print("UNSOLVED SUDOKU: ")
    display(gridExample(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    print(" ")
    print("SOLVED SUDOKU: ")
    display(result)
    print("############################################################")

    try:
        import PySudoku

        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

