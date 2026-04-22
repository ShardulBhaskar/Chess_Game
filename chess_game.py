import tkinter as tk
from tkinter import font as tkfont, messagebox
import chess
import chess.engine
import os
import random

# =====================================================
# SETTINGS
# =====================================================
SQ = 72
BOARD_SIZE = SQ * 8
MOVELIST_W = 220
TOPBAR_H = 52
BTNBAR_H = 54
WINDOW_W = BOARD_SIZE + MOVELIST_W
WINDOW_H = BOARD_SIZE + TOPBAR_H + BTNBAR_H

LIGHT = "#EEEED2"
DARK = "#769656"
SELECT_COL = "#f6f669"
LASTMOVE_L = "#cdd26a"
LASTMOVE_D = "#aaa23a"
CHECK_COL = "#ff5555"

TOPBAR_BG = "#1e1e24"
TOPBAR_FG = "#e8d5a3"

MOVELIST_BG = "#1a1a22"
MOVELIST_HDR = "#252530"

BTNBAR_BG = "#15151d"

PIECES = {
    "P": "♙", "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔",
    "p": "♟", "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚",
}

DIFFICULTY_LEVELS = {
    "Beginner": {"depth": 3, "time": 0.05},
    "Easy": {"depth": 10, "time": 0.10},
    "Intermediate": {"depth": 15, "time": 0.20},
    "Advanced": {"depth": 25, "time": 0.30},
    "Expert": {"depth": 50, "time": 0.50},
}

STOCKFISH_PATHS = [
    "stockfish",
    r"C:\Users\thesh\OneDrive\Desktop\Chess_Game\Stockfish\stockfish\stockfish-windows-x86-64.exe",
]

# =====================================================
# DIFFICULTY
# =====================================================
class DifficultyDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title("Chess vs AI")
        self.geometry("420x520")
        self.configure(bg="#111")
        self.grab_set()

        tk.Label(self, text="♟ Chess vs AI",
                 fg="#e0c97f", bg="#111",
                 font=("Georgia", 22, "bold")).pack(pady=20)

        self.level = tk.StringVar(value="Intermediate")

        for lv in DIFFICULTY_LEVELS:
            tk.Radiobutton(
                self,
                text=lv,
                variable=self.level,
                value=lv,
                bg="#111",
                fg="white",
                selectcolor="#222",
                font=("Consolas", 11)
            ).pack(anchor="w", padx=100)

        tk.Label(self, text="Play As",
                 fg="#e0c97f", bg="#111",
                 font=("Consolas", 12, "bold")).pack(pady=10)

        self.color = tk.StringVar(value="Random")

        row = tk.Frame(self, bg="#111")
        row.pack()

        for c in ("White", "Black", "Random"):
            tk.Radiobutton(
                row,
                text=c,
                variable=self.color,
                value=c,
                bg="#111",
                fg="white",
                selectcolor="#222"
            ).pack(side="left", padx=10)

        tk.Button(
            self,
            text="START GAME",
            command=self.start,
            bg="#e0c97f",
            font=("Consolas", 13, "bold"),
            padx=15,
            pady=8,
            bd=0
        ).pack(pady=25)

    def start(self):
        self.result = {
            "difficulty": self.level.get(),
            "color": self.color.get()
        }
        self.destroy()

# =====================================================
# MAIN
# =====================================================
class ChessGUI:
    def __init__(self, root, diff="Intermediate", clr="Random"):
        self.root = root
        self.difficulty = diff
        self.depth = DIFFICULTY_LEVELS[diff]["depth"]
        self.ai_time = DIFFICULTY_LEVELS[diff]["time"]

        if clr == "White":
            self.user_color = chess.WHITE
        elif clr == "Black":
            self.user_color = chess.BLACK
        else:
            self.user_color = random.choice([chess.WHITE, chess.BLACK])

        self.flipped = (self.user_color == chess.BLACK)

        self.board = chess.Board()
        self.selected = None
        self.legal_moves = []
        self.last_move = None
        self.game_over = False

        self.redo_stack = []

        self.build_fonts()
        self.build_ui()
        self.load_engine()
        self.draw_all()

        if self.user_color == chess.BLACK:
            self.root.after(400, self.ai_move)

    def build_fonts(self):
        self.piece_font = tkfont.Font(family="Arial Unicode MS", size=40, weight="bold")
        self.small = tkfont.Font(family="Consolas", size=10)

    def build_ui(self):
        self.top = tk.Canvas(self.root, width=WINDOW_W, height=TOPBAR_H,
                             bg=TOPBAR_BG, highlightthickness=0)
        self.top.pack()

        mid = tk.Frame(self.root)
        mid.pack()

        self.canvas = tk.Canvas(mid, width=BOARD_SIZE, height=BOARD_SIZE)
        self.canvas.pack(side="left")
        self.canvas.bind("<Button-1>", self.click)

        self.moves = tk.Text(mid, width=22, height=32,
                             bg=MOVELIST_BG, fg="white",
                             font=("Consolas", 11))
        self.moves.pack(side="left", fill="y")

        bar = tk.Frame(self.root, bg=BTNBAR_BG)
        bar.pack(fill="x")

        self.btn(bar, "Undo", self.undo).pack(side="left", padx=3, pady=5)
        self.btn(bar, "Redo", self.redo).pack(side="left", padx=3)
        self.btn(bar, "Draw", self.offer_draw).pack(side="left", padx=3)
        self.btn(bar, "New", self.new_game_selector).pack(side="left", padx=3)
        self.btn(bar, "Resign", self.resign).pack(side="right", padx=3)

    def btn(self, parent, txt, cmd):
        return tk.Button(parent, text=txt, command=cmd,
                         bg="#333", fg="white", bd=0,
                         padx=10, pady=8)

    def load_engine(self):
        self.engine = None
        for p in STOCKFISH_PATHS:
            try:
                if p == "stockfish" or os.path.exists(p):
                    self.engine = chess.engine.SimpleEngine.popen_uci(p)
                    return
            except:
                pass

    def sq_to_xy(self, sq):
        file = chess.square_file(sq)
        rank = chess.square_rank(sq)

        col = 7 - file if self.flipped else file
        row = rank if self.flipped else 7 - rank

        return col * SQ, row * SQ

    def xy_to_sq(self, x, y):
        col = x // SQ
        row = y // SQ

        file = 7 - col if self.flipped else col
        rank = row if self.flipped else 7 - row

        return chess.square(file, rank)

    def draw_all(self):
        self.draw_top()
        self.draw_board()
        self.draw_moves()

    def draw_top(self):
        self.top.delete("all")
        self.top.create_text(15, 25, text="♟ Chess vs AI",
                             fill=TOPBAR_FG, anchor="w")

        txt = "Stockfish ON" if self.engine else "No Engine"
        col = "#55cc55" if self.engine else "#ff5555"

        self.top.create_text(WINDOW_W - 10, 25, text=txt,
                             fill=col, anchor="e")

    def draw_board(self):
        self.canvas.delete("all")

        check_sq = None
        if self.board.is_check():
            check_sq = self.board.king(self.board.turn)

        for sq in chess.SQUARES:
            x, y = self.sq_to_xy(sq)
            f = chess.square_file(sq)
            r = chess.square_rank(sq)

            col = LIGHT if (f + r) % 2 else DARK

            if sq == self.selected:
                col = SELECT_COL
            elif self.last_move and sq in (
                    self.last_move.from_square,
                    self.last_move.to_square):
                col = LASTMOVE_L if (f + r) % 2 else LASTMOVE_D
            elif sq == check_sq:
                col = CHECK_COL

            self.canvas.create_rectangle(
                x, y, x + SQ, y + SQ,
                fill=col, outline=""
            )

            if sq in self.legal_moves:
                self.canvas.create_oval(
                    x+28, y+28, x+44, y+44,
                    fill="#333", outline=""
                )

            piece = self.board.piece_at(sq)
            if piece:
                fill = "#ffffff" if piece.color else "#111111"
                shadow = "#666666" if piece.color else "#999999"

                self.canvas.create_text(
                    x + SQ//2 + 1,
                    y + SQ//2 + 1,
                    text=PIECES[piece.symbol()],
                    font=self.piece_font,
                    fill=shadow
                )

                self.canvas.create_text(
                    x + SQ//2,
                    y + SQ//2,
                    text=PIECES[piece.symbol()],
                    font=self.piece_font,
                    fill=fill
                )

    def draw_moves(self):
        self.moves.delete("1.0", "end")
        temp = chess.Board()

        for i, mv in enumerate(self.board.move_stack):
            san = temp.san(mv)
            temp.push(mv)

            if i % 2 == 0:
                self.moves.insert("end", f"{i//2+1}. {san} ")
            else:
                self.moves.insert("end", f"{san}\n")

    def click(self, e):
        if self.game_over:
            return

        if self.board.turn != self.user_color:
            return

        sq = self.xy_to_sq(e.x, e.y)

        if self.selected is None:
            p = self.board.piece_at(sq)
            if p and p.color == self.user_color:
                self.selected = sq
                self.legal_moves = [
                    m.to_square for m in self.board.legal_moves
                    if m.from_square == sq
                ]
        else:
            move = chess.Move(self.selected, sq)

            p = self.board.piece_at(self.selected)
            if p and p.piece_type == chess.PAWN:
                rank = chess.square_rank(sq)
                if rank in [0, 7]:
                    move = chess.Move(self.selected, sq, promotion=chess.QUEEN)

            if move in self.board.legal_moves:
                self.board.push(move)
                self.last_move = move
                self.redo_stack.clear()

                self.selected = None
                self.legal_moves = []
                self.draw_all()

                if not self.board.is_game_over():
                    self.root.after(300, self.ai_move)
                return

            self.selected = None
            self.legal_moves = []

        self.draw_board()

    def ai_move(self):
        if self.board.turn == self.user_color:
            return

        if self.board.is_game_over():
            return

        try:
            if self.engine:
                res = self.engine.play(
                    self.board,
                    chess.engine.Limit(depth=self.depth, time=self.ai_time)
                )
                mv = res.move
            else:
                mv = random.choice(list(self.board.legal_moves))
        except:
            mv = random.choice(list(self.board.legal_moves))

        self.board.push(mv)
        self.last_move = mv
        self.draw_all()

    def undo(self):
        if len(self.board.move_stack) == 0:
            return

        self.redo_stack.clear()

        if len(self.board.move_stack):
            self.redo_stack.insert(0, self.board.pop())

        if len(self.board.move_stack):
            self.redo_stack.insert(0, self.board.pop())

        self.last_move = self.board.move_stack[-1] if self.board.move_stack else None
        self.draw_all()

    def redo(self):
        if not self.redo_stack:
            return

        if self.redo_stack:
            mv = self.redo_stack.pop(0)
            if mv in self.board.legal_moves:
                self.board.push(mv)

        if self.redo_stack:
            mv = self.redo_stack.pop(0)
            if mv in self.board.legal_moves:
                self.board.push(mv)

        self.last_move = self.board.move_stack[-1]
        self.draw_all()

    def resign(self):
        ans = messagebox.askyesno("Resign", "Are you sure?")
        if ans:
            self.new_game_selector()

    def offer_draw(self):
        ans = messagebox.askyesno("Draw", "Accept Draw?")
        if ans:
            self.new_game_selector()

    def new_game_selector(self):
        dlg = DifficultyDialog(self.root)
        self.root.wait_window(dlg)

        st = dlg.result or {
            "difficulty": "Intermediate",
            "color": "Random"
        }

        self.difficulty = st["difficulty"]
        self.depth = DIFFICULTY_LEVELS[self.difficulty]["depth"]
        self.ai_time = DIFFICULTY_LEVELS[self.difficulty]["time"]

        if st["color"] == "White":
            self.user_color = chess.WHITE
        elif st["color"] == "Black":
            self.user_color = chess.BLACK
        else:
            self.user_color = random.choice([chess.WHITE, chess.BLACK])

        self.flipped = (self.user_color == chess.BLACK)

        self.board = chess.Board()
        self.selected = None
        self.legal_moves = []
        self.last_move = None
        self.redo_stack.clear()

        self.draw_all()

        if self.user_color == chess.BLACK:
            self.root.after(400, self.ai_move)

    def close(self):
        try:
            if self.engine:
                self.engine.quit()
        except:
            pass
        self.root.destroy()

# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    dlg = DifficultyDialog(root)
    root.wait_window(dlg)

    st = dlg.result or {
        "difficulty": "Intermediate",
        "color": "Random"
    }

    root.deiconify()
    root.title("Chess vs AI")
    root.geometry(f"{WINDOW_W}x{WINDOW_H}")
    root.resizable(False, False)

    app = ChessGUI(root, st["difficulty"], st["color"])
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()