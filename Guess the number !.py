import random
import tkinter as tk


class NumberGuessingGame:
    WIDTH = 500
    HEIGHT = 560

    def __init__(self, root):
        self.root = root
        self.root.title("Guess the Number")
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.root.resizable(False, False)

        self.dark = False
        self.secret = 0
        self.attempts = 0
        self.guesses = set()
        self.message = "Your turn!"
        self.message_color = "muted"
        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT,
                                highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.entry = tk.Entry(root, font=("Segoe UI", 20), justify="center",
                              relief="flat", bd=0)
        self.new_game()
        self.draw()
        self.root.bind("<Return>", lambda _event: self.check_guess())

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

    def rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]
        return self.canvas.create_polygon(
            points, smooth=True, splinesteps=24, **kwargs
        )

    def button(self, x1, y1, x2, y2, text, callback, tag, *, secondary=False):
        colors = self.palette()
        fill = colors["input"] if secondary else colors["accent"]
        text_color = colors["text"] if secondary else "#ffffff"
        shape = self.rounded_rectangle(
            x1, y1, x2, y2, 14, fill=fill, outline="", tags=tag
        )
        self.canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2, text=text,
            fill=text_color, font=("Segoe UI", 11, "bold"), tags=tag,
        )
        self.canvas.tag_bind(tag, "<Button-1>", lambda _event: callback())
        self.canvas.tag_bind(
            tag, "<Enter>",
            lambda _event: self.canvas.itemconfigure(
                shape, fill=colors["accent_hover"] if not secondary else colors["border"]
            ),
        )
        self.canvas.tag_bind(
            tag, "<Leave>", lambda _event: self.canvas.itemconfigure(shape, fill=fill)
        )
        self.canvas.tag_bind(tag, "<Enter>", lambda _event: self.canvas.config(cursor="hand2"), add="+")
        self.canvas.tag_bind(tag, "<Leave>", lambda _event: self.canvas.config(cursor=""), add="+")

    def draw(self):
        colors = self.palette()
        self.canvas.configure(bg=colors["background"])
        self.canvas.delete("all")
        self.rounded_rectangle(32, 28, 468, 532, 26, fill=colors["card"],
                               outline=colors["border"], width=1)
        self.canvas.create_text(250, 83, text="GUESS THE NUMBER",
                                fill=colors["muted"], font=("Segoe UI", 10, "bold"))
        self.canvas.create_text(250, 125, text="Guess the number",
                                fill=colors["text"], font=("Segoe UI", 23, "bold"))
        self.canvas.create_text(250, 165, text="Pick a number from 1 to 10",
                                fill=colors["muted"], font=("Segoe UI", 11))
        self.rounded_rectangle(106, 201, 394, 265, 13, fill=colors["input"],
                               outline=colors["border"], width=1)
        self.entry.configure(bg=colors["input"], fg=colors["text"],
                             insertbackground=colors["text"], highlightthickness=0)
        self.canvas.create_window(250, 233, window=self.entry, width=260, height=48)
        self.button(106, 286, 394, 336, "Guess", self.check_guess, "guess")
        self.canvas.create_text(250, 377, text=self.message,
                                fill=colors[self.message_color],
                                font=("Segoe UI", 12, "bold"))
        self.canvas.create_text(250, 413, text=f"Attempts: {self.attempts}",
                                fill=colors["muted"], font=("Segoe UI", 10))
        self.button(106, 448, 242, 492, "New game", self.new_game, "new-game",
                    secondary=True)
        self.button(258, 448, 394, 492,
                    "Light theme" if self.dark else "Dark theme",
                    self.toggle_theme, "theme", secondary=True)

    def check_guess(self):
        if self.message.startswith("You win"):
            return
        raw_guess = self.entry.get().strip()
        try:
            guess = int(raw_guess)
        except ValueError:
            self.message = "Enter a whole number."
            self.message_color = "error"
            self.draw()
            self.entry.focus_set()
            return

        if not 1 <= guess <= 10:
            self.message = "Choose a number from 1 to 10."
            self.message_color = "error"
        elif guess in self.guesses:
            self.message = "You already tried that number."
            self.message_color = "error"
        else:
            self.guesses.add(guess)
            self.attempts += 1
            if guess < self.secret:
                self.message = "Try a higher number!"
                self.message_color = "accent"
            elif guess > self.secret:
                self.message = "Try a lower number!"
                self.message_color = "accent"
            else:
                self.message = f"You win! Found in {self.attempts} guess(es)."
                self.message_color = "success"

        self.entry.delete(0, tk.END)
        self.draw()
        self.entry.focus_set()

    def new_game(self):
        self.secret = random.randint(1, 10)
        self.attempts = 0
        self.guesses = set()
        self.message = "Your turn!"
        self.message_color = "muted"
        if hasattr(self, "canvas"):
            self.entry.delete(0, tk.END)
            self.draw()
            self.entry.focus_set()

    def toggle_theme(self):
        self.dark = not self.dark
        self.draw()
        self.entry.focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    NumberGuessingGame(root)
    root.mainloop()
