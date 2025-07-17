import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from app.ai_detector.extract_features import extract_combined_features
from app.ai_detector.model import AIContentClassifier
import joblib
import torch
import torch.nn as nn
import torch.optim as optim


def load_data(csv_path):
    df = pd.read_csv(csv_path)
    texts = df['text'].astype(str).tolist()
    labels = df['label'].astype(int).tolist()

    X, Y = [], []

    for text, label in zip(texts, labels):
        features = extract_combined_features(text)
        if features is None or len(features) == 0:
            print("Empty features for:", text[:100], "...")
        else:
            X.append(features)
            Y.append(label)

    return np.array(X), np.array(Y)


def train_and_save(csv_path, model_path, scaler_path):
    X, Y = load_data(csv_path)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_val, y_train, y_val = train_test_split(X_scaled, Y, test_size=0.2)

    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    Y_train_tensor = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)
    X_val_tensor = torch.tensor(X_val, dtype=torch.float32)
    Y_val_tensor = torch.tensor(y_val, dtype=torch.float32).view(-1, 1)

    model = AIContentClassifier(input_dim=X.shape[1])
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    for epoch in range(30):
        model.train()
        optimizer.zero_grad()
        output = model(X_train_tensor)
        loss = criterion(output, Y_train_tensor)
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val_tensor)
            val_loss = criterion(val_outputs, Y_val_tensor)
            val_pred = (val_outputs > 0.5).int()
            acc = (val_pred.view(-1) == Y_val_tensor.view(-1).int()).sum().item() / len(Y_val_tensor)

        print(f"Epoch {epoch+1} - Loss: {loss.item():.4f}, Val Loss: {val_loss.item():.4f}, Val Acc: {acc:.2f}")

    torch.save(model.state_dict(), model_path)
    joblib.dump(scaler, scaler_path)

    print(f"Model saved to {model_path}")
    print(f"Scaler saved to {scaler_path}")

if __name__ == "__main__":
    csv_path = "app/ai_detector/Dataset - Sheet1 (1).csv"
    model_path = "app/ai_detector/ai_model.pt"
    scaler_path = "app/ai_detector/scaler.pkl"
    train_and_save(csv_path, model_path, scaler_path)


