import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os

df = pd.read_csv("app/ai_detector/Dataset - Sheet1 (1).csv")

if "text" not in df.columns or "label" not in df.columns:
    raise ValueError("Dataset must have 'text' and 'label' columns")

model = SentenceTransformer('all-MiniLM-L6-v2')

print("Generating embeddings...")
embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)

np.save("embeddings.npy", embeddings)
df["label"].to_csv("label.csv", index=False)

print("Done! Saved embeddings.npy and 'label.csv'")