import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.baseline import get_user_baseline

def is_semantically_similar(embedding1, embedding2, threshold=0.9):
    sim = cosine_similarity([embedding1], [embedding2])[0][0]
    return sim >= threshold, sim

def is_in_clipboard(chunk_text, clipboard_log):
    for entry in clipboard_log:
        if chunk_text.strip() == entry.get("text", "").strip():
            return True
    return False

def detect_style_anomaly(embedding, user_baseline, threshold=0.85):
    if not user_baseline:
        return False, 0.0
    sim = cosine_similarity([embedding], [user_baseline])[0][0]
    return sim < threshold, sim

def analyze_chunk(chunk_data, embedding, clipboard_log, previous_chunks, username):
    hash_val = chunk_data["hash"]
    chunk_text = chunk_data["text"]

    reasons = []
    status = "New"

    for past in previous_chunks:
        if hash_val == past["hash"]:
            reasons.append("Exact match with previously submitted content (hash match).")
            return "Resued", "; ".join(reasons)

        similar, sim_score = is_semantically_similar(embedding, past["embedding"])
        if similar:
            reasons.append(f"High semantic similarity to prior content (similarity={sim_score:.2}).")
            return "Resued", "; ".join(reasons)

    if is_in_clipboard(chunk_text, clipboard_log):
        reasons.append("Chunk text previously appeared in clipboard history.")

    user_baseline = get_user_baseline(username)
    if user_baseline is not None:
        anomaly, sim_score = detect_style_anomaly(embedding, user_baseline)
        if anomaly:
            reasons.append(f"Style deviates from typical user writing (style similarity={sim_score:.2}).")

        if reasons:
            status = "Suspicious!"
        return status, "; ".join(reasons) if reasons else "No matching signals detected."



