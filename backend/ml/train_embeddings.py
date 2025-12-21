import os
import joblib
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

DATASET_PATH = "data/mediva_symptoms.csv"
MODEL_DIR = "backend/ml/models"

os.makedirs(MODEL_DIR, exist_ok=True)

def main():
    print("🔄 Loading dataset...")
    df = pd.read_csv(DATASET_PATH)

    assert {"symptoms", "condition", "domain"}.issubset(df.columns)

    texts = df["symptoms"].astype(str).tolist()

    print("🧠 Loading embedding model...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    print("⚡ Generating embeddings...")
    embeddings = embedder.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    print("💾 Saving models...")
    joblib.dump(embedder, f"{MODEL_DIR}/embedding_model.joblib")
    joblib.dump(embeddings, f"{MODEL_DIR}/symptom_embeddings.joblib")
    joblib.dump(df.reset_index(drop=True), f"{MODEL_DIR}/metadata.joblib")

    print("✅ Training complete")
    print(f"• Samples: {len(df)}")
    print(f"• Conditions: {df['condition'].nunique()}")

if __name__ == "__main__":
    main()
