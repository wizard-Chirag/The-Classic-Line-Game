"""
============================================================
  Frontend GUI for 3-Pawn Tic-Tac-Toe
============================================================
Uses Python's built-in Tkinter.
Communicates with `main.py` for game rules, adjacency, and AI.
Run with: python gui.py
"""

import tkinter as tk
from tkinter import messagebox
import main  # Imports game logic, AI, and constants from main.py


class ThreePawnsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("𝑻𝒉𝒆 𝑪𝒍𝒂𝒔𝒔𝒊𝒄 𝑳𝒊𝒏𝒆 𝑮𝒂𝒎𝒆")
        self.root.geometry("480x720")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        # Game State
        self.board = [None] * 9
        self.current_player = "X"
        self.x_placed = 0
        self.o_placed = 0
        self.selected_node = None
        self.winning_line = None
        self.game_over = False
        self.ai_timer_id = None
        self.is_vs_ai = tk.BooleanVar(value=True)

        # Board Coordinates mapped to Canvas pixels (x, y)
        self.node_coords = {
            0: (90, 90),    # A1
            1: (240, 90),   # A2
            2: (390, 90),   # A3
            3: (90, 240),   # B1
            4: (240, 240),  # B2 (Center)
            5: (390, 240),  # B3
            6: (90, 390),   # C1
            7: (240, 390),  # C2
            8: (390, 390),  # C3
        }

        self.create_widgets()
        self.reset_game()

    def create_widgets(self):
        # Header / Title
        header_frame = tk.Frame(self.root, bg="#0f172a")
        header_frame.pack(pady=10)

        title_lbl = tk.Label(
            header_frame, text="𝑻𝒉𝒆 𝑪𝒍𝒂𝒔𝒔𝒊𝒄 𝑳𝒊𝒏𝒆 𝑮𝒂𝒎𝒆",
            font=("Segoe UI", 18, "bold"), fg="#38bdf8", bg="#0f172a"
        )
        title_lbl.pack()

        # Mode Selection & Reset Button
        ctrl_frame = tk.Frame(self.root, bg="#0f172a")
        ctrl_frame.pack(pady=5)

        ai_check = tk.Checkbutton(
            ctrl_frame, text="Play vs AI (Computer is O)",
            variable=self.is_vs_ai, command=self.reset_game,
            font=("Segoe UI", 10), fg="#f8fafc", bg="#1e293b",
            selectcolor="#0f172a", activebackground="#1e293b",
            activeforeground="#38bdf8", padx=8, pady=3, relief="flat"
        )
        ai_check.pack(side=tk.LEFT, padx=10)

        reset_btn = tk.Button(
            ctrl_frame, text="🔄 Reset", command=self.reset_game,
            font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#334155",
            activebackground="#475569", activeforeground="#ffffff",
            padx=10, pady=2, relief="flat", cursor="hand2"
        )
        reset_btn.pack(side=tk.LEFT)

        # Status Banner (Phase & Turn)
        status_frame = tk.Frame(self.root, bg="#1e293b", padx=15, pady=8, relief="ridge", bd=1)
        status_frame.pack(fill=tk.X, padx=30, pady=10)

        self.phase_lbl = tk.Label(
            status_frame, text="Phase 1: Drop Phase",
            font=("Segoe UI", 10, "italic"), fg="#94a3b8", bg="#1e293b"
        )
        self.phase_lbl.pack()

        self.turn_lbl = tk.Label(
            status_frame, text="Turn: Player X",
            font=("Segoe UI", 13, "bold"), fg="#38bdf8", bg="#1e293b",
            wraplength=420, justify="center"
        )
        self.turn_lbl.pack()

        self.counter_lbl = tk.Label(
            status_frame, text="Pawns Placed: X (0/3) | O (0/3)",
            font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b"
        )
        self.counter_lbl.pack()

        # Board Canvas
        self.canvas = tk.Canvas(
            self.root, width=480, height=450,
            bg="#0f172a", highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def is_movement_phase(self):
        return self.x_placed == 3 and self.o_placed == 3

    def reset_game(self):
        if self.ai_timer_id is not None:
            self.root.after_cancel(self.ai_timer_id)
            self.ai_timer_id = None
        self.board = [None] * 9
        self.current_player = "X"
        self.x_placed = 0
        self.o_placed = 0
        self.selected_node = None
        self.winning_line = None
        self.game_over = False
        self.redraw_board()

    def redraw_board(self):
        self.canvas.delete("all")
        line_color = "#475569"

        # 1. Draw connection lines
        # Outer Perimeter
        self.canvas.create_rectangle(90, 90, 390, 390, outline=line_color, width=4)
        # Center Cross (+ shape)
        self.canvas.create_line(240, 90, 240, 390, fill=line_color, width=4)
        self.canvas.create_line(90, 240, 390, 240, fill=line_color, width=4)
        # Diagonals (X shape)
        self.canvas.create_line(90, 90, 390, 390, fill=line_color, width=4)
        self.canvas.create_line(390, 90, 90, 390, fill=line_color, width=4)

        # 2. Draw Nodes (circles & pieces)
        radius = 28
        for idx, (cx, cy) in self.node_coords.items():
            circle_color = "#1e293b"
            border_color = "#334155"
            border_width = 3
            is_target = False

            # Highlight selected pawn (Yellow)
            if self.selected_node == idx:
                border_color = "#eab308"
                border_width = 5

            # Highlight valid adjacent empty targets (Green)
            if self.selected_node is not None:
                if idx in main.ADJACENCY[self.selected_node] and self.board[idx] is None:
                    border_color = "#22c55e"
                    circle_color = "#14532d"
                    border_width = 4
                    is_target = True

            # Highlight winning line (Gold)
            if self.winning_line is not None and idx in self.winning_line:
                border_color = "#f59e0b"
                border_width = 5

            # Draw circle
            self.canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                fill=circle_color, outline=border_color, width=border_width
            )

            # Draw pawn mark (X or O)
            val = self.board[idx]
            if val == "X":
                self.canvas.create_text(
                    cx, cy, text="X", font=("Segoe UI", 22, "bold"), fill="#38bdf8"
                )
            elif val == "O":
                self.canvas.create_text(
                    cx, cy, text="O", font=("Segoe UI", 22, "bold"), fill="#f43f5e"
                )
            else:
                # Small coordinate label (e.g. A1, B2)
                lbl_color = "#86efac" if is_target else "#64748b"
                self.canvas.create_text(
                    cx, cy, text=main.COORD_NAMES[idx],
                    font=("Segoe UI", 9), fill=lbl_color
                )

        # 3. Update Status Texts
        if not self.game_over:
            if not self.is_movement_phase():
                self.phase_lbl.config(text=f"Phase 1: Drop Phase ({self.x_placed + self.o_placed}/6 placed)")
            else:
                self.phase_lbl.config(text="Phase 2: Movement Phase (Slide Pawns)")

            color = "#38bdf8" if self.current_player == "X" else "#f43f5e"
            self.turn_lbl.config(text=f"Turn: Player {self.current_player}", fg=color)
            self.counter_lbl.config(text=f"Pawns Placed: X ({self.x_placed}/3) | O ({self.o_placed}/3)")

    def get_clicked_node(self, x, y):
        """Finds which node was clicked within its radius."""
        for idx, (cx, cy) in self.node_coords.items():
            if (x - cx) ** 2 + (y - cy) ** 2 <= 32 ** 2:
                return idx
        return None

    def on_canvas_click(self, event):
        if self.game_over:
            return

        # Disable input if it's AI's turn
        if self.is_vs_ai.get() and self.current_player == "O":
            return

        idx = self.get_clicked_node(event.x, event.y)
        if idx is None:
            return

        self.handle_player_action(idx)

    def handle_player_action(self, idx):
        if not self.is_movement_phase():
            # --- DROP PHASE ---
            if self.board[idx] is not None:
                return  # Occupied

            self.board[idx] = self.current_player
            if self.current_player == "X":
                self.x_placed += 1
            else:
                self.o_placed += 1

            if main.check_win(self.board, self.current_player):
                self.end_game(f"🎉 Player {self.current_player} wins on the drop phase!", winning_player=self.current_player)
                return

            self.next_turn()
        else:
            # --- MOVEMENT PHASE ---
            if self.selected_node is None:
                # Select own piece
                if self.board[idx] == self.current_player:
                    self.selected_node = idx
                    self.redraw_board()
            else:
                # If clicking the currently selected piece, deselect it
                if self.selected_node == idx:
                    self.selected_node = None
                    self.redraw_board()
                    return

                # If clicking another of own piece, change selection
                if self.board[idx] == self.current_player:
                    self.selected_node = idx
                    self.redraw_board()
                    return

                # Move pawn to adjacent empty node
                if self.board[idx] is None and idx in main.ADJACENCY[self.selected_node]:
                    self.board[self.selected_node] = None
                    self.board[idx] = self.current_player
                    self.selected_node = None

                    if main.check_win(self.board, self.current_player):
                        self.end_game(f"🏆 Player {self.current_player} wins with 3-in-a-row!", winning_player=self.current_player)
                        return

                    self.next_turn()
                else:
                    # Deselect on invalid click
                    self.selected_node = None
                    self.redraw_board()

    def next_turn(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        self.selected_node = None
        self.redraw_board()

        # Check for stalemate / no legal moves in movement phase
        if self.is_movement_phase():
            legal_moves = main.get_legal_moves(self.board, self.current_player)
            if not legal_moves:
                winner = "O" if self.current_player == "X" else "X"
                self.end_game(f"❌ No legal moves left for Player {self.current_player}! Player {winner} wins!")
                return

        # Trigger AI move
        if self.is_vs_ai.get() and self.current_player == "O" and not self.game_over:
            self.ai_timer_id = self.root.after(400, self.run_ai_turn)

    def run_ai_turn(self):
        self.ai_timer_id = None
        if self.game_over or self.current_player != "O" or not self.is_vs_ai.get():
            return

        if not self.is_movement_phase():
            idx = main.ai_drop_move(self.board)
            self.board[idx] = "O"
            self.o_placed += 1

            if main.check_win(self.board, "O"):
                self.end_game("🤖 Computer (O) wins on the drop phase!", winning_player="O")
                return
        else:
            move = main.ai_movement_move(self.board)
            if not move:
                self.end_game("Player X wins! AI has no legal moves.")
                return

            f, t = move
            self.board[f] = None
            self.board[t] = "O"

            if main.check_win(self.board, "O"):
                self.end_game("🤖 Computer (O) wins with 3-in-a-row!", winning_player="O")
                return

        self.next_turn()

    def end_game(self, message, winning_player=None):
        self.game_over = True
        self.selected_node = None
        if self.ai_timer_id is not None:
            self.root.after_cancel(self.ai_timer_id)
            self.ai_timer_id = None

        if winning_player:
            for line in main.WINNING_LINES:
                if all(self.board[pos] == winning_player for pos in line):
                    self.winning_line = line
                    break

        self.redraw_board()
        self.phase_lbl.config(text="Game Over!")
        self.turn_lbl.config(text=message, fg="#22c55e")
        self.counter_lbl.config(text="Click '🔄 Reset' to play again.")
        messagebox.showinfo("Game Over", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = ThreePawnsGUI(root)
    root.mainloop()