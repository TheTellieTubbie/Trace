import threading
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename
from .extractor import extract_chunks
from .fingerprints import get_sha256, get_embeddings
from .history import load_history, update_history
from app.monitor.clipboard_monitor import monitor_clipboard, load_log

main = Blueprint('main', __name__)

def is_semantically_similar(new_emb, existing_emb, threshold=0.9):
    return cosine_similarity([new_emb], [existing_emb])[0][0] >= threshold

monitor_thread = None

@main.route("/", methods=["GET", "POST"])
def index():
    extracted_data = {}
    history = load_history()

    previous_chunks = []
    for chunks in history.values():
        previous_chunks.extend(chunks)


    new_chunks_for_history = []

    if request.method == "POST":
        uploaded_files = request.files.getlist("files")
        saved_paths = []

        for file in uploaded_files:
            if file.filename != "":
                filename = secure_filename(file.filename)
                save_path = os.path.join("uploads", filename)
                file.save(save_path)
                saved_paths.append(filename)

                chunks = extract_chunks(save_path)
                chunk_data = []

                for chunk in chunks:
                    hash_val = get_sha256(chunk)
                    embedding = get_embeddings(chunk)

                    embedding_array = embedding.tolist()
                    prev_match = next(
                        (c for c in previous_chunks if
                         c["hash"] == hash_val or
                         is_semantically_similar(embedding_array, c["embedding"])),
                        None
                    )
                    if prev_match:
                        status = "Reused"
                    else:
                        status = "New"
                        new_chunks_for_history.append({
                            "hash": hash_val,
                            "text": chunk,
                            "embedding": embedding.tolist(),
                        })

                    chunk_data.append({
                        "text": chunk,
                        "hash": hash_val,
                        "embedding": embedding.tolist(),
                        "status": status
                    })

                extracted_data[filename] = chunk_data

        update_history(filename, new_chunks_for_history)

        return render_template("index.html", uploaded=True, files=saved_paths, extracted=extracted_data)

    return render_template("index.html", uploaded=False)

@main.route("/clipboard", methods=["GET", "POST"])
def clipboard():
    global montior_thread

    if request.method == "POST":
        if not montior_thread or not montior_thread.is_alive():
            montior_thread = threading.Thread(target=monitor_clipboard, daemon=True)
            montior_thread.start()

    log_data = load_log()
    return render_template("clipboard.html", log=log_data)