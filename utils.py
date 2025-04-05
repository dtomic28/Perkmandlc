import os


def load_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))


def is_first_time():
    if not os.path.exists("tutorial_flag.txt"):
        with open("tutorial_flag.txt", "w") as f:
            f.write("False")
        return True
    with open("tutorial_flag.txt", "r") as f:
        return f.read().strip() == "False"


def mark_tutorial_done():
    with open("tutorial_flag.txt", "w") as f:
        f.write("True")
