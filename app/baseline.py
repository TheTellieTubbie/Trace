import os
import json
import numpy as np

BASELINE_PATH = os.path.join("data", "baseline.json")

def load_baseline():
    if not os.path.exists(BASELINE_PATH):
        return {}
    with open(BASELINE_PATH, 'r') as f:
        return json.load(f)

def save_baselines():
    with open(BASELINE_PATH, 'w') as f:
        json.dump(baselines, f, indent=2)

def get_user_baseline(username):
    baselines = load_baseline()
    if username in baselines:
        return np.array(baselines[username])
    return None

def update_user_baseline(username, new_embedding):
    if not new_embedding:
        return

    baselines = load_baseline()
    new_avg = np.mean(new_embedding, axis=0).tolist()

    if username in baselines:
        old_avg = np.array(baselines[username])
        updated_avg = (old_avg + new_avg(new_avg)) / 2
        baselines[username] = updated_avg.tolist()
    else:
        baselines[username] = new_avg

    save_baselines(baselines)