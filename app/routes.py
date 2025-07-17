import threading
import os
import joblib
import numpy as np
import json
import torch
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from .ai_detector.extract_features import extract_combined_features
from .models import User
from .forms import LoginForm
from .extractor import extract_chunks
from .fingerprints import get_sha256
from .history import load_history, update_history
from app.monitor.clipboard_monitor import monitor_clipboard, load_log
from app.ai_detector.model import AIContentClassifier

main = Blueprint('main', __name__)
monitor_thread = None

MODEL_PATH = "app/ai_detector/ai_model.pt"
SCALAR_PATH = "app/ai_detector/ai_scalar.pkl"
model = AIContentClassifier(input_dim=17)
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()
scaler = joblib.load(SCALAR_PATH)

AI_THRESHOLD = 0.5

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
                    try:
                        hash_val = get_sha256(chunk)
                        features = extract_combined_features(chunk)
                        if features is None:
                            continue

                        features_scaled = scaler.transform([features])
                        input_tensor = torch.tensor(features_scaled, dtype=torch.float32).unsqueeze(0)

                        with torch.no_grad():
                            prediction = model(input_tensor).item()


                        status = "Suspicious" if prediction > AI_THRESHOLD else "Unsuspicious"
                        reason = f"AI Prediction Score: {prediction:.2f}"

                        new_chunks_for_history.append({
                            "hash": hash_val,
                            "text": chunk,
                            "embedding": features.tolist(),
                            "status": status,
                        })

                        display_chunks.append({
                            "text": chunk,
                            "status": status,
                            "reason": reason,
                            "confidence": prediction,
                            "source": "AI Model",
                            "hash": hash_val,
                            "embedding": features[:5],
                        })

                    except Exception as e:
                        print(f"Exception chunk: {e}")
                        continue

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
        if entry.get("status") == "Suspicious" or entry.get("status") == "Reused"
    ]

    history = load_history()
    flagged_uploads = {}

    for user, chunks in history.items():
        for chunk in chunks:
            if chunk.get("status") in ["Suspicious!", "Reused", "Suspicious!"]:
                flagged_uploads.setdefault(user, []).append(chunk)

    return render_template(
        "teacher_dashboard.html",
        clipboard_flags=flagged_clipboard,
        upload_flags=flagged_uploads
    )

