"""
============================================================
  3-Pawn Tic-Tac-Toe (Three Men's Morris / Tapatan)
============================================================
Rules:
1. Drop Phase:
   - Players take turns placing 3 pawns each (X and O) on any empty square.
   - If a player gets 3-in-a-row during this phase, they win immediately.

2. Movement Phase:
   - Players take turns moving one of their 3 pawns to an adjacent empty square.
   - Center (B2) connects to all 8 surrounding squares.
   - Corners and Edges connect to their immediate perimeter neighbors + Center.
   - First to align their 3 pawns in a straight line wins!
"""

# Board Coordinates:
#  A1(0) -- A2(1) -- A3(2)
#   |   \    |    /   |
#  B1(3) -- B2(4) -- B3(5)
#   |   /    |    \   |
#  C1(6) -- C2(7) -- C3(8)

COORD_NAMES = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
NAME_TO_IDX = {name.lower(): idx for idx, name in enumerate(COORD_NAMES)}

# Graph Adjacency based on confirmed rules:
ADJACENCY = {
    0: [1, 3, 4],                 # A1: A2, B1, Center
    1: [0, 2, 4],                 # A2: A1, A3, Center
    2: [1, 5, 4],                 # A3: A2, B3, Center
    3: [0, 6, 4],                 # B1: A1, C1, Center
    4: [0, 1, 2, 3, 5, 6, 7, 8],  # B2 (Center): all 8 neighbors
    5: [2, 8, 4],                 # B3: A3, C3, Center
    6: [3, 7, 4],                 # C1: B1, C2, Center
    7: [6, 8, 4],                 # C2: C1, C3, Center
    8: [5, 7, 4],                 # C3: B3, C2, Center
}

WINNING_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows (A, B, C)
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns (1, 2, 3)
    [0, 4, 8], [2, 4, 6]              # Diagonals
]


def print_board(board):
    """Prints the current board state with row and column headers."""
    def sym(i):
        return board[i] if board[i] is not None else " "

    print("\n      1   2   3")
    print(f"   A  {sym(0)} | {sym(1)} | {sym(2)}")
    print("     ---+---+---")
    print(f"   B  {sym(3)} | {sym(4)} | {sym(5)}")
    print("     ---+---+---")
    print(f"   C  {sym(6)} | {sym(7)} | {sym(8)}\n")


def check_win(board, player):
    """Returns True if the player has formed any 3-in-a-row."""
    return any(all(board[i] == player for i in line) for line in WINNING_LINES)


def get_legal_moves(board, player):
    """Returns a list of (from_node, to_node) for all legal moves."""
    pieces = [i for i, val in enumerate(board) if val == player]
    moves = []
    for p in pieces:
        for adj in ADJACENCY[p]:
            if board[adj] is None:
                moves.append((p, adj))
    return moves


# ---------------- AI DECISION ENGINE ---------------- #

def ai_drop_move(board):
    """Smart placement logic for the AI during Drop Phase."""
    empty = [i for i, val in enumerate(board) if val is None]

    # 1. Immediate Win
    for idx in empty:
        board[idx] = "O"
        if check_win(board, "O"):
            board[idx] = None
            return idx
        board[idx] = None

    # 2. Block Opponent's Immediate Win
    for idx in empty:
        board[idx] = "X"
        if check_win(board, "X"):
            board[idx] = None
            return idx
        board[idx] = None

    # 3. Take Center if open
    if 4 in empty:
        return 4

    # 4. Corner preference
    for corner in [0, 2, 6, 8]:
        if corner in empty:
            return corner

    return empty[0]


def ai_movement_move(board):
    """Smart movement logic for the AI during Movement Phase."""
    moves = get_legal_moves(board, "O")
    if not moves:
        return None

    # 1. Immediate Win
    for f, t in moves:
        board[f] = None
        board[t] = "O"
        if check_win(board, "O"):
            board[t] = None
            board[f] = "O"
            return (f, t)
        board[t] = None
        board[f] = "O"

    # 2. Position evaluation
    best_move = moves[0]
    best_score = -9999

    for f, t in moves:
        board[f] = None
        board[t] = "O"

        score = 0
        if t == 4:
            score += 10  # Moving into center is strong
        if f == 4:
            score -= 5   # Avoid abandoning center unless necessary

        # Check if this move gives X an immediate win on their next turn
        x_moves = get_legal_moves(board, "X")
        x_can_win = False
        for xf, xt in x_moves:
            board[xf] = None
            board[xt] = "X"
            if check_win(board, "X"):
                x_can_win = True
            board[xt] = None
            board[xf] = "X"

        if x_can_win:
            score -= 200

        if score > best_score:
            best_score = score
            best_move = (f, t)

        board[t] = None
        board[f] = "O"

    return best_move


# ---------------- MAIN GAME LOOP ---------------- #

def main():
    print("=" * 50)
    print("      3-PAWN TIC-TAC-TOE (Three Men's Morris)     ")
    print("=" * 50)
    print("Game Modes:")
    print("  1. Player vs AI (You are X, AI is O)")
    print("  2. Two Players Local (Pass & Play)")

    mode = input("\nSelect mode (1 or 2, default=1): ").strip()
    is_vs_ai = (mode != "2")

    board = [None] * 9
    current_player = "X"
    x_placed = 0
    o_placed = 0

    # ---------------- PHASE 1: DROP PHASE ---------------- #
    print("\n" + "=" * 50)
    print(">>> PHASE 1: DROP PHASE (Place 3 pawns each)")
    print("=" * 50)

    while x_placed < 3 or o_placed < 3:
        print_board(board)
        print(f"Current Turn: {current_player} | Pawns Placed: X={x_placed}/3, O={o_placed}/3")

        if is_vs_ai and current_player == "O":
            idx = ai_drop_move(board)
            print(f"🤖 AI places 'O' at: {COORD_NAMES[idx]}")
        else:
            while True:
                user_input = input(f"Enter coordinate to place {current_player} (e.g. B2): ").strip().lower()
                if user_input in NAME_TO_IDX:
                    idx = NAME_TO_IDX[user_input]
                    if board[idx] is None:
                        break
                    print("❌ That square is already occupied! Choose an empty one.")
                else:
                    print("❌ Invalid coordinate! Valid choices: A1, A2, A3, B1, B2, B3, C1, C2, C3.")

        board[idx] = current_player
        if current_player == "X":
            x_placed += 1
        else:
            o_placed += 1

        # Check for immediate win in placement phase
        if check_win(board, current_player):
            print_board(board)
            print(f"🎉 {current_player} WINS on the placement round! Congratulations!")
            return

        current_player = "O" if current_player == "X" else "X"

    # ---------------- PHASE 2: MOVEMENT PHASE ---------------- #
    print("\n" + "=" * 50)
    print(">>> PHASE 2: MOVEMENT PHASE (Slide pawns along lines)")
    print("=" * 50)
    print("Format: Enter 'Source Destination' (e.g. 'B2 C2' or 'B2 > C2')")

    while True:
        print_board(board)
        print(f"Current Turn: {current_player}")

        if is_vs_ai and current_player == "O":
            move = ai_movement_move(board)
            if not move:
                print("❌ AI has no legal moves! Player X wins!")
                return
            f, t = move
            print(f"🤖 AI moves: {COORD_NAMES[f]} -> {COORD_NAMES[t]}")
        else:
            legal_moves = get_legal_moves(board, current_player)
            if not legal_moves:
                winner = "O" if current_player == "X" else "X"
                print(f"❌ No legal moves left for {current_player}! {winner} wins!")
                return

            while True:
                user_input = input(f"Enter move for {current_player} (e.g. 'B2 C2'): ").strip().lower()
                tokens = user_input.replace(">", " ").replace("-", " ").split()

                if len(tokens) == 2 and tokens[0] in NAME_TO_IDX and tokens[1] in NAME_TO_IDX:
                    f = NAME_TO_IDX[tokens[0]]
                    t = NAME_TO_IDX[tokens[1]]
                    if (f, t) in legal_moves:
                        break
                    print("❌ Illegal move! You can only move your pawn to an adjacent EMPTY square.")
                else:
                    print("❌ Invalid format! Please enter like 'B2 C2' or 'A1 B1'.")

        # Execute move
        board[f] = None
        board[t] = current_player

        # Check win condition
        if check_win(board, current_player):
            print_board(board)
            print(f"🏆 {current_player} WINS with 3-in-a-row! BOOYAH!")
            return

        current_player = "O" if current_player == "X" else "X"


if __name__ == "__main__":
    main()