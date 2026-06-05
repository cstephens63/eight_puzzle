from collections import deque
import random


class Node:
    '''
   Represents a state in the search tree.

    state: tuple representing board configuration
    parent: pointer to parent node (used to reconstruct solution path)
    move: move that generated the state
    depth: depth of node in search tree
    '''
    def __init__(self, state, parent =None, move =None, depth =0):
        self.state = state
        self.parent = parent
        self.move = move
        self.depth = depth






# Generates starting state and checks if the state is solvable #
def random_board_generator():
    '''
    Generate starting state and checks if the state is solvable.

    A configuration of the 8-puzzle is solvable if the number of inversions
    is even.

    This function repeatedly shuffles the board until a solvable configuration
    is produced, then returns it as an immutable tuple.
    '''

    # Starts with a list of the goal state (0 represents the blank)
    board = [1, 2, 3, 4, 0, 5, 6, 7, 8]
    solvable = False

    # Continue generating until a solvable board is found
    while not solvable:
        no_zero = []                
        inversion_count = 0        
        random.shuffle(board)       
        
        # Count number of inversions in the shuffled board
        for i in board:             
            no_zero.append(i)

        # Create a copy of the board excluding 0
        no_zero.remove(0)           

        # Counts pairs (i,j) where i appears before j but i > j
        for a in range(len(no_zero)):
            for b in range(a + 1, len(no_zero)):        
                if no_zero[a] > no_zero[b]:
                    inversion_count += 1

        # Check if inversions are even
        if inversion_count % 2 == 0:                    
            solvable = True
            return tuple(board)  # Return as tuple for hashability in sets                 

def print_state(board):
    '''
    Prints the 8-puzzle board in a 3x3 grid format.

    The board is stored internally as a flat tuple of length 9.

    The blank tile (0) is diplayed as "_" for clarity.
    '''

    #iterate over the board in groups of 3 to form rows
    for i in range(0,9,3):
        chunk = board[i:i+3]

        row = []

        # Replace 0 with "_" fo display purposes
        for j in chunk:
            if j == 0:
                row.append("_")
            else:
                row.append(j)
        print(*row)        



def moves(board):
    '''
    Generates all valid successor states from the given board configuration.

    The blank tile can move up, down, left, or right,
    provided the move stays within board boundaries.

    Returns:
        A list of tuples (new_board, direction), 
        where new_board is the resulting configuration 
        and direction indicates the move taken.
    '''
    neighbors = []

    # Locate a blank tile and compute its row and column
    blank = board.index(0)
    row = blank // 3
    col = blank % 3

    # If blank is not in the rightmost column, it can move right
    if col < 2:
        right = blank + 1
        new_list= list(board)
        new_list[blank], new_list[right] = new_list[right], new_list[blank]
        new_board = tuple(new_list)
        neighbors.append((new_board, "Right"))

    # If blank is not in the leftmost column, it can move left
    if col > 0:
        left = blank - 1
        new_list = list(board)
        new_list[blank], new_list[left] = new_list[left], new_list[blank]
        new_board = tuple(new_list)
        neighbors.append((new_board, "Left"))

    # If blank is not in the top column, it can move up
    if row > 0:
        up = blank - 3
        new_list = list(board)
        new_list[blank], new_list[up] = new_list[up], new_list[blank]
        new_board = tuple(new_list)
        neighbors.append((new_board, "Up"))

    # If blank is not in the bottom column, it can move down.
    if row < 2:
        down = blank + 3
        new_list = list(board)
        new_list[blank], new_list[down] = new_list[down], new_list[blank]
        new_board = tuple(new_list)
        neighbors.append((new_board, "Down"))

    return neighbors

# write search algorithms

def bfs(node, goal):
    '''
    Bredth-First Search.
    Explores nodes level-by-level using a queue
    Uses a reached set to prevent revisiting states.
    '''
    print_section("BEGIN SEARCH TREE (First 100 Expansions)")

    # If initial state is already goal, return immediately 
    if node.state == goal:
        print_state(node.state)
        return node.state
    
    q = deque()
    q.append(node)
    reached = set()
    reached.add(node.state) 
    expansion_count = 0
    while q:
        # Dequeue next node (ensures level-order traversal)
        current = q.popleft()
       
        expansion_count += 1
        if expansion_count <= 100:
            print_expansions(expansion_count, current)

        # Expand current node by generating successors
        for child_state, direction in moves(current.state):
            if child_state not in reached:
                child = Node(
                parent = current,
                state = child_state,
                move = direction,
                depth = current.depth +1
            )
                
                # Goal test on generation
                if child.state == goal:
                    print_section("SEARCH COMPLETE")
                    print(f"TOTAL EXPANSIONS: {expansion_count}")
                    print(f"SOLUTION DEPTH: {child.depth}")
                    print_section("SOLUTION PATH")
                    return child
                else:
                    reached.add(child_state)
                    q.append(child)



def dls(node, limit, goal, expansion_count):
    '''
    Depth-Limited Search used by IDFS.
    Performs DFS up to a given depth limit.
    Returns "cutoff" if depth limit prevents further expansion
    '''
    stack = []
    stack.append(node)
    cutoff_occurred = False
   

    while stack:
        # LIFO pop ensures depth-first behavior
        current = stack.pop()

        expansion_count += 1
        if expansion_count <= 100:
            print_expansions(expansion_count, current)
        if current.state == goal:
            return current, expansion_count
        
        # Do not expand beyond the depth limit
        if current.depth == limit:
            cutoff_occurred = True
            continue

        for child_state, direction in moves(current.state):

            # Prevent cycles along the current DFS branch
            ancestor = current
            is_cycle = False
            while ancestor is not None:
                if ancestor.state == child_state:
                    is_cycle = True
                    break
                
                ancestor = ancestor.parent

            if not is_cycle:
                child_node = Node(
                    state = child_state,
                    parent = current,
                    move = direction,
                    depth = current.depth + 1
                )
                stack.append(child_node)

    if cutoff_occurred:
        return "cutoff", expansion_count
    return None, expansion_count

def idfs(node, goal):
    '''
    Iterative Deepening DFS.
    Repeatedly calls DLS with increasing depth limits.
    Comibines optimality of BFS with memory efficiency of DFS
    '''
    print_section("BEGIN SEARCH TREE (First 100 Expansions)")

    depth = 0
    expansion_count = 0
    while True:
        # Call limited depth search with current limit
        result, expansion_count = dls(node, depth, goal, expansion_count)
        if result != "cutoff":
            print_section("SEARCH COMPLETE")
            print(f"TOTAL EXPANSIONS: {expansion_count}")
            print(f"SOLUTION DEPTH: {result.depth}")
            print_section("SOLUTION PATH")
            return result
        # Increase depth limit and repeat
        depth += 1



def print_expansions(expansion_count, node):
    '''
    Formating for displaying each expansion.

    Prints expansion number, depth, and state for each node.
    '''
    print(f"Expansion #: {expansion_count}")
    print(f"Depth: {node.depth}")
    print_state(node.state)
    print()


def print_path(goal):
    '''
    Reconstructs and prints the solution path from the initial state to the goal.

    The search algorithms (BFS/IDFS) store parent references in each Node.
    Starting from the goal node, this function follows parent pointers
    back to the root, collectsthe states, and then 
    reverses the order to display the path from start to goal.

    Each state is printed witha step number indicating its depth
    in the solution sequence
    '''
    path = []

    # Traverse backwards from the goal to the initial state using parent references
    current = goal
    while current is not None:
        path.append(current.state)
        current = current.parent

    # Reverse the path so it prints from start to goal
    path.reverse()

    # Print each state in order with step number
    for step_number, node_state in enumerate(path):
        print(f"Step {step_number}:")
        print_state(node_state)
        print()

def print_section(title):
    '''
    Formatting to note different sections in output
    '''
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50 + "\n")


        
GOAL = (1, 2, 3, 4, 0, 5, 6, 7, 8)

start_state = random_board_generator()

node = Node(start_state)

print_path(bfs(node, GOAL))
print_path(idfs(node, GOAL))

