"""Misc functions used in main program for various processes."""

from pathlib import Path

def red(text):
    """Print input text in red."""
    print("\033[31m" + text + "\033[0m")

def green(text):
    """Print input text in green."""
    print("\033[32m" + text + "\033[0m")

def yellow(text):
    """Print input text in yellow."""
    print("\033[33m" + text + "\033[0m")

def bold(text):
    """Print input text in bold."""
    print("\033[1m" + text + "\033[0m")

def user_input(prompt=str) -> bool:
    """User input returned as true / false."""
    user_ans = input(prompt + " (y / n) ")
    user_ans = user_ans.lower().strip()

    # Allowed input.
    yes_ans = ["y", "yes", "ye"]
    if user_ans in yes_ans:
        return True
    return False
