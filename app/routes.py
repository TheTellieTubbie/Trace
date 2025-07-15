import threading
import os
import numpy as np
from flask_login import current_user, login_required
from sklearn.metrics.pairwise import cosine_similarity
from flask import Blueprint, render_template, request
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from .extractor import extract_chunks
from .fingerprints import get_sha256, get_embeddings
from .forms import LoginForm
from .history import load_history, update_history
from app.monitor.clipboard_monitor import monitor_clipboard, load_log
from flask import redirect, url_for, flash
from flask_login import login_user
from .models import User


main = Blueprint('main', __name__)

def is_semantically_similar(new_emb, existing_emb, threshold=0.9):
    return cosine_similarity([new_emb], [existing_emb])[0][0] >= threshold

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
    history = load_history()
    previous_chunks = [c for chunks in history.values() for c in chunks]
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

                    similar = any(
                        c["hash"] == hash_val or
                        is_semantically_similar(embedding, c["embedding"])
                        for c in previous_chunks
                    )

                    if not similar:
                        new_chunks_for_history.append({
                            "hash": hash_val,
                            "text": chunk,
                            "embedding": embedding,
                            "uploaded_by": current_user.username,
                        })
        if saved_files:
            update_history(current_user.username, new_chunks_for_history)

    return render_template("student_dashboard.html", uploaded=saved_files)

@main.route("/teacher", methods=["GET", "POST"])
@login_required
def teacher_dashboard():
    if current_user.role != "teacher":
        return "unauthorized", 403
    return render_template("teacher_dashboard.html")

