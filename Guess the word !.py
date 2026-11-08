import random
import re
import tkinter as tk
import unicodedata
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


BUILT_IN_WORDS = [
    "python", "computer", "programming", "hangman", "algorithm", "intelligence",
    "crocodile", "international", "nebula", "chocolate", "library", "developer",
    "adventure", "elephant", "mystery", "butterfly", "mountain", "sunshine",
]
MAX_MISTAKES = 8
WORD_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE)


def normalize_letter(value):
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def read_dictionary(path):
    words = set()
    is_hunspell = path.suffix.lower() == ".dic"
    with path.open("r", encoding="utf-8-sig", errors="replace") as dictionary:
        for line_number, line in enumerate(dictionary):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if is_hunspell and line_number == 0 and line.isdigit():
                continue
            if is_hunspell:
                line = line.split("\t", 1)[0].split("/", 1)[0]
                candidates = [line]
            else:
                candidates = WORD_PATTERN.findall(line)
            for candidate in candidates:
                candidate = candidate.strip("'-’")
                if len(candidate) >= 2 and candidate.isalpha():
                    words.add(candidate)
    if not words:
        raise ValueError("No valid words were found in this dictionary.")
    return sorted(words, key=str.casefold)


class HangmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman")
        self.root.geometry("760x700")
        self.root.minsize(650, 620)
        self.dark = False

        self.style = ttk.Style(root)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.dictionary_path = Path(__file__).with_name("words.txt")
        legacy_dictionary = Path(__file__).with_name("dictionnaire.txt")
        if not self.dictionary_path.is_file() and legacy_dictionary.is_file():
            self.dictionary_path = legacy_dictionary
        if self.dictionary_path.is_file():
            try:
                self.words = read_dictionary(self.dictionary_path)
                self.dictionary_name = self.dictionary_path.name
            except (OSError, ValueError) as error:
                messagebox.showwarning(
                    "Dictionary",
                    f"Could not load {self.dictionary_path.name}:\n{error}\n\n"
                    "The built-in word list will be used.",
                )
                self.use_builtin_words()
        else:
            self.use_builtin_words()

        self.apply_theme()
        self.build_interface()
        self.new_game()

    def palette(self):
        if self.dark:
            return {
                "background": "#101827", "card": "#1b2638", "text": "#f4f7fb",
                "muted": "#a7b3c5", "accent": "#8b7bff", "accent_hover": "#7564ee",
                "input": "#111b2b", "border": "#344258", "success": "#46d6a0",
                "error": "#ff7185",
            }
        return {
            "background": "#f1f5fb", "card": "#ffffff", "text": "#182338",
            "muted": "#66738a", "accent": "#6757e8", "accent_hover": "#5141d2",
            "input": "#f4f6fb", "border": "#e0e6f0", "success": "#168a65",
            "error": "#d7475c",
        }

    def apply_theme(self):
        colors = self.palette()
        self.root.configure(bg=colors["background"])
        self.style.configure("TFrame", background=colors["background"])
        self.style.configure("Card.TFrame", background=colors["card"])
        self.style.configure("Title.TLabel", background=colors["background"],
                             foreground=colors["text"], font=("Segoe UI", 23, "bold"))
        self.style.configure("Subtitle.TLabel", background=colors["background"],
                             foreground=colors["muted"], font=("Segoe UI", 10))
        self.style.configure("Card.TLabel", background=colors["card"],
                             foreground=colors["text"], font=("Segoe UI", 11))
        self.style.configure("Word.TLabel", background=colors["card"],
                             foreground=colors["accent"], font=("Segoe UI", 24, "bold"))
        self.style.configure("Status.TLabel", background=colors["card"],
                             foreground=colors["muted"], font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8),
                             background=colors["input"], foreground=colors["text"])
        self.style.map("TButton", background=[
            ("active", colors["border"]), ("pressed", colors["border"])
        ])
        self.style.configure("Accent.TButton", background=colors["accent"],
                             foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", background=[
            ("active", colors["accent_hover"]), ("pressed", colors["accent_hover"])
        ])
        if hasattr(self, "drawing"):
            self.drawing.configure(bg=colors["card"])
        if hasattr(self, "letter_entry"):
            self.letter_entry.configure(
                style="Game.TEntry"
            )
        self.style.configure(
            "Game.TEntry", fieldbackground=colors["input"],
            foreground=colors["text"], insertcolor=colors["text"],
            bordercolor=colors["border"],
        )

    def use_builtin_words(self):
        self.words = BUILT_IN_WORDS[:]
        self.dictionary_name = "built-in list"

    def build_interface(self):
        outer = ttk.Frame(self.root, padding=(28, 22))
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Hangman", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="Guess the word before the drawing is complete.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 18))

        card = ttk.Frame(outer, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)
        self.drawing = tk.Canvas(card, height=235, bg="#ffffff",
                                 highlightthickness=0, bd=0)
        self.drawing.pack(fill="x")
        self.drawing.bind("<Configure>", lambda _event: self.draw_hangman())

        self.word_label = ttk.Label(card, style="Word.TLabel", anchor="center")
        self.word_label.pack(fill="x", pady=(6, 12))
        self.status_label = ttk.Label(card, style="Status.TLabel", anchor="center")
        self.status_label.pack(fill="x")
        self.wrong_label = ttk.Label(card, style="Card.TLabel", anchor="center")
        self.wrong_label.pack(fill="x", pady=(6, 18))

        controls = ttk.Frame(card, style="Card.TFrame")
        controls.pack()
        self.letter_entry = ttk.Entry(controls, width=8, justify="center",
                                      font=("Segoe UI", 15))
        self.letter_entry.grid(row=0, column=0, padx=(0, 8))
        self.letter_entry.bind("<Return>", lambda _event: self.guess())
        ttk.Button(controls, text="Guess", style="Accent.TButton",
                   command=self.guess).grid(row=0, column=1, padx=4)
        ttk.Button(controls, text="New game",
                   command=self.new_game).grid(row=0, column=2, padx=4)

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(14, 0))
        self.dictionary_label = ttk.Label(footer, style="Subtitle.TLabel")
        self.dictionary_label.pack(side="left")
        self.theme_button = ttk.Button(footer, command=self.toggle_theme)
        self.theme_button.pack(side="right", padx=(8, 0))
        ttk.Button(footer, text="Load dictionary…",
                   command=self.choose_dictionary).pack(side="right")
        self.update_theme_button()

    def update_theme_button(self):
        self.theme_button.configure(
            text="Light theme" if self.dark else "Dark theme"
        )

    def toggle_theme(self):
        self.dark = not self.dark
        self.apply_theme()
        self.update_theme_button()
        self.refresh()

    def new_game(self):
        self.secret = random.choice(self.words)
        self.found = set()
        self.missed = set()
        self.game_over = False
        self.feedback = "Enter a letter, then submit."
        if hasattr(self, "letter_entry"):
            self.letter_entry.delete(0, tk.END)
            self.refresh()
            self.letter_entry.focus_set()

    def guess(self):
        if self.game_over:
            return
        raw = self.letter_entry.get().strip()
        self.letter_entry.delete(0, tk.END)
        normalized = normalize_letter(raw)
        if len(normalized) != 1 or not normalized.isalpha():
            self.feedback = "Enter a single valid letter."
            self.refresh()
            return
        if normalized in self.found or normalized in self.missed:
            self.feedback = "You already guessed that letter."
            self.refresh()
            return

        secret_letters = {normalize_letter(char) for char in self.secret}
        if normalized in secret_letters:
            self.found.add(normalized)
            self.feedback = "Good guess!"
        else:
            self.missed.add(normalized)
            self.feedback = "Not this time."

        if secret_letters.issubset(self.found):
            self.game_over = True
            self.feedback = f"You found it: {self.secret}!"
        elif len(self.missed) >= MAX_MISTAKES:
            self.game_over = True
            self.feedback = f"Game over. The word was: {self.secret}."
        self.refresh()
        if not self.game_over:
            self.letter_entry.focus_set()

    def refresh(self):
        displayed = [
            char if not char.isalpha() or normalize_letter(char) in self.found else "_"
            for char in self.secret
        ]
        self.word_label.configure(text="  ".join(displayed))
        self.status_label.configure(
            text=f"{self.feedback}   ·   Mistakes: {len(self.missed)}/{MAX_MISTAKES}"
        )
        self.wrong_label.configure(
            text="Missed letters: " + (", ".join(sorted(self.missed)) or "none")
        )
        self.dictionary_label.configure(
            text=f"{len(self.words):,} words · {self.dictionary_name}".replace(",", " ")
        )
        self.draw_hangman()

    def draw_hangman(self):
        if not hasattr(self, "drawing"):
            return
        canvas = self.drawing
        canvas.delete("all")
        width = max(canvas.winfo_width(), 400)
        colors = self.palette()
        color = colors["muted"]
        canvas.create_line(width * 0.30, 210, width * 0.68, 210,
                           fill=colors["border"], width=5, capstyle=tk.ROUND)
        if len(self.missed) >= 1:
            canvas.create_line(width * 0.42, 208, width * 0.42, 28,
                               fill=color, width=5, capstyle=tk.ROUND)
        if len(self.missed) >= 2:
            canvas.create_line(width * 0.42, 30, width * 0.61, 30,
                               fill=color, width=5, capstyle=tk.ROUND)
        if len(self.missed) >= 3:
            canvas.create_line(width * 0.61, 30, width * 0.61, 54,
                               fill=color, width=4, capstyle=tk.ROUND)
        if len(self.missed) >= 4:
            canvas.create_oval(width * 0.575, 51, width * 0.645, 121,
                               outline=colors["accent"], width=4)
        if len(self.missed) >= 5:
            canvas.create_line(width * 0.61, 121, width * 0.61, 166,
                               fill=color, width=4, capstyle=tk.ROUND)
        if len(self.missed) >= 6:
            canvas.create_line(width * 0.61, 132, width * 0.56, 156,
                               fill=color, width=4, capstyle=tk.ROUND)
        if len(self.missed) >= 7:
            canvas.create_line(width * 0.61, 132, width * 0.66, 156,
                               fill=color, width=4, capstyle=tk.ROUND)
        if len(self.missed) >= 8:
            canvas.create_line(width * 0.61, 166, width * 0.57, 191,
                               fill=color, width=4, capstyle=tk.ROUND)
            canvas.create_line(width * 0.61, 166, width * 0.65, 191,
                               fill=color, width=4, capstyle=tk.ROUND)

    def choose_dictionary(self):
        filename = filedialog.askopenfilename(
            title="Choose a word dictionary",
            filetypes=[
                ("Text and Hunspell dictionaries", "*.txt *.dic"),
                ("All files", "*.*"),
            ],
        )
        if not filename:
            return
        try:
            words = read_dictionary(Path(filename))
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror("Invalid dictionary", str(error))
            return
        self.words = words
        self.dictionary_name = Path(filename).name
        self.new_game()


if __name__ == "__main__":
    root = tk.Tk()
    HangmanGame(root)
    root.mainloop()