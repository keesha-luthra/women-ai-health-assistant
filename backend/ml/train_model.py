import os
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


DATA_PATH = "data/symptoms_dataset.csv"


def train():
    # ---- Load dataset ----
    df = pd.read_csv(DATA_PATH)

    X = df["symptoms"].astype(str)
    y = df["condition"].astype(str)

    # ---- Vectorizer ----
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1
    )

    X_vec = vectorizer.fit_transform(X)

    # ---- Classifier ----
    model = LogisticRegression(
        max_iter=1000,
        solver="lbfgs",
        multi_class="auto"
    )

    model.fit(X_vec, y)

    # ---- Save artifacts RELATIVE to this file ----
    base_dir = os.path.dirname(__file__)

    joblib.dump(vectorizer, os.path.join(base_dir, "tfidf_vectorizer.pkl"))
    joblib.dump(model, os.path.join(base_dir, "logistic_model.pkl"))
    joblib.dump(model.classes_, os.path.join(base_dir, "labels.pkl"))

    print("✅ Training complete.")
    print("📦 Artifacts saved to backend/ml/")


if __name__ == "__main__":
    train()
