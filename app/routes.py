import threading
import os
import numpy as np
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from sklearn.metrics.pairwise import cosine_similarity

from .models import User
from .forms import LoginForm
from .extractor import extract_chunks
from .fingerprints import get_sha256, get_embeddings
from .history import load_history, update_history
from .detector import analyze_chunk
from app.baseline import get_user_baseline, update_user_baseline
from app.monitor.clipboard_monitor import monitor_clipboard, load_log

main = Blueprint('main', __name__)

monitor_thread = None

@main.route("/")
def home_redirect():
    return redirect(url_for('auth.login'))

@main.route("/clipboard", methods=["GET", "POST"])
def clipboard():
    global monitor_thread
    if request.method == "POST":
        if not monitor_thread or not monitor_thread.is_alive():
            monitor_thread = threading.Thread(target=monitor_clipboard, daemon=True)
            monitor_thread.start()
    log_data = load_log()
    return render_template("clipboard.html", log=log_data)

@main.route("/student", methods=["GET", "POST"])
@login_required
def student_dashboard():
    if current_user.role != "student":
            return "unauthorized", 403

    saved_files = []
    display_chunks = []
    history = load_history()
    previous_chunks = [c for chunks in history.values() for c in chunks]
    clipboard_log = load_log()
    new_chunks_for_history = []

    if request.method == "POST":
        uploaded_files = request.files.getlist("files")

        for file in uploaded_files:
            if file.filename != "":
                filename = secure_filename(file.filename)
                save_path = os.path.join("uploads", filename)
                file.save(save_path)
                saved_files.append(filename)
                chunks = extract_chunks(save_path)

                for chunk in chunks:
                    hash_val = get_sha256(chunk)
                    embedding = get_embeddings(chunk)

                    chunk_data = {
                        "hash": hash_val,
                        "text": chunk,
                        "embedding": embedding,
                    }

                    status, reason = analyze_chunk(chunk_data, embedding, clipboard_log, previous_chunks, current_user.username)

                    if status == "New":
                        new_chunks_for_history.append(chunk)

                    display_chunks.append({
                        "text": chunk,
                        "status": status,
                        "reason": reason,
                        "hash": hash_val,
                        "embedding": embedding[:5],
                    })

        if saved_files:
            update_history(current_user.username, new_chunks_for_history)

    return render_template("student_dashboard.html", uploaded=saved_files, extracted=display_chunks)

@main.route("/teacher", methods=["GET", "POST"])
@login_required
def teacher_dashboard():
    if current_user.role != "teacher":
        return "unauthorized", 403

    clipboard_log = load_log()

    flagged_clipboard = [
        entry for entry in clipboard_log
        if entry.get("status") == "Suspicious!" or entry.get("status") == "Reused"
    ]

    history = load_history()
    flagged_uploads = {}

    for user, chunks in history.items():
        for chunk in chunks:
            if chunk.get("status") in ["Suspicious!", "Reused"]:
                flagged_uploads.setdefault(user, []).append(chunk)

    return render_template(
        "teacher_dashboard.html",
        clipboard_flags=flagged_clipboard,
        upload_flags=flagged_uploads
    )

