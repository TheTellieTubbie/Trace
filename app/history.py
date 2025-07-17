import os
import json

HISTORY_PATH = os.path.join("data", "history.json")

def load_history():
    if not os.path.isfile(HISTORY_PATH):
        return {}
    try:
        with open(HISTORY_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Failed to load history from {HISTORY_PATH}")
        return {}

def save_history(history):
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

def update_history(username, chunks):
    history = load_history()
    existing = history.get(username, [])
    updated = existing + [
        {
            "hash": c["hash"],
            "embedding": c["embedding"],
            "text": c.get("text", ""),
            "status": c.get("status", "New")
         }
        for c in chunks
    ]
    history[username] = updated
    save_history(history)