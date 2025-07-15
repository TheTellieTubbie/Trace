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
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                return []
    return []

def save_log(log):
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

def monitor_clipboard():
    print("Clipboard monitor")
    seen = set()
    history = load_history()
    all_previous = []
    for chunks in history.values():
        all_previous.extend(chunks)


    log = load_log()
    while True:
        try:
            content = pyperclip.paste()
            if content and content not in seen:
                seen.add(content)
                print(f"\n New clipboard content:\n {content[:100]}...")

                chunks = extract_chunks_from_text(content)
                for chunk in chunks:
                    hash_val = get_sha256(chunk)
                    embedding = get_embeddings(chunk).tolist()

                    match = next(
                        (c for c in all_previous if c["hash"] == hash_val or is_similar(embedding, c.get("embedding",[]))),
                        None
                    )
                    status = "Reused" if match else "New"

                    log.append({
                        "timestamp": time.time(),
                        "text": chunk,
                        "hash": hash_val,
                        "status": status,
                    })
                    print(f" Chunk status: {status}")

                save_log(log)
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def extract_chunks_from_text(text):
    return [para.strip() for para in text.split("\n") if para.strip()]

