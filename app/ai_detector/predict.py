import torch
import joblib
import numpy as np
from app.ai_detector.model import AIContentClassifier
from app.ai_detector.extract_features import extract_combined_features

MODEL_PATH = "app/ai_detector/ai_model.pth"
SCALER_PATH = "app/ai_detector/scaler.pkl"

model = None
scaler = None

def load_model_and_scaler():
    global model, scaler
    if model is None or scaler is None:
        scaler = joblib.load(SCALER_PATH)
        input_size = len(extract_combined_features("sample text"))
        model = AIContentClassifier(input_size=input_size)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
        model.eval()


def predict_ai_liklihood(text):
    load_model_and_scaler()

    features = extract_combined_features(text)
    if features is None or len(features) == 0:
        return 0.0, "No features found"

    scaled = scalar.transform([features])
    tensor_input = torch.tensor(scaled, dtype=torch.float32)

    with torch.no_grad():
        output = model(tensor_input).item()

    label = "AI-generated" if output >= 0.5 else "Human-written"
    cofidence = round(output, 3) if output >= 0.5 else round(1 - output, 3)

    return output, f"{label} (confidence: {cofidence})"