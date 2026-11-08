# Guessing Games

Two small Python games with graphical interfaces built using Tkinter:

- **Guess the Number**: guess a number from 1 to 10. Includes light and dark
  themes, rounded interface elements, input validation, and Enter-key support.
- **Hangman**: guess a word using the built-in list or load your own dictionary.
  Plain-text (`.txt`) word lists and Hunspell (`.dic`) dictionaries are supported.

## Using a word dictionary

To load a dictionary automatically, place a UTF-8 file named `words.txt`
in the same folder as `Guess the word !.py`. Words can be separated by spaces or
listed one per line. You can also click **Load dictionary…** in the game to
choose a `.txt` or `.dic` file. The game uses a small built-in list if no
dictionary file is found. The older `dictionnaire.txt` filename is also
supported. Accented words keep their spelling; accents are ignored when
matching guessed letters.

## Run the games

Python 3 with Tkinter is required. Run either script from a terminal:

```text
python "Guess the number !.py"
python "Guess the word !.py"
```

Tkinter is included with most Python installations. No third-party packages or
Internet connection are required.
