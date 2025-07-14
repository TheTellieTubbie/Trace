import time
import pyperclip
import os
import json
from app.extractor import extract_chunks
from app.fingerprints import get_sha256, get_embeddings
from app.history import load_history
from sklearn.metrics.pairwise import cosine_similarity

LOG_PATH = os.path.join("data", "clipboard_log.json")

def is_similar(embedding1, embedding2, threshold=0.9):
    return cosine_similarity([embedding1], [embedding2])[0][0] >= threshold

def load_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            return json.load(f)
    return []

def save_log():
    with open(LOG_PATH, "w") as f:
        json.dump(load_log(), f, indent=2)

def monitor_clipboard():
    print("Clipboard monitor")
    seen = set()
    history = load_history()
    all_previous = []
    for chunks in history.values():
        all_previous.extend(chunks)


    log = load_log()
