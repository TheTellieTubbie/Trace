import os
import json

HISTORY_PATH = os.path.join("data", "history.json")

def load_history():
    if not os.path.isfile(HISTORY_PATH):
        return {}
    with open(HISTORY_PATH, "r") as f:
        return json.load(f)

def save_history(history):
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

def update_history(filename, chunks):
    history = load_history()
    existing = history.get(filename, [])
    updated = existing + [
        {"hash": c["hash"], "embedding": c["embedding"]}
        for c in chunks
    ]
    history[filename] = updated
    save_history(history)