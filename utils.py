import os
import json

SAVE_FILE = "save_data.json"
DEFAULT_DATA = {"high_score": 0, "tutorial_done": False}


def load_data():
    if not os.path.exists(SAVE_FILE):
        return DEFAULT_DATA.copy()
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return DEFAULT_DATA.copy()


def save_data(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_high_score():
    return load_data().get("high_score", 0)


def save_high_score(score):
    data = load_data()
    data["high_score"] = score
    save_data(data)


def is_first_time():
    return not load_data().get("tutorial_done", False)


def mark_tutorial_done():
    data = load_data()
    data["tutorial_done"] = True
    save_data(data)
