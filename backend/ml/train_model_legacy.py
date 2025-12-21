import os
import joblib
import pandas as pd

from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.svm import LinearSVC


DATA_PATH = "data/symptoms_dataset.csv"


def train():
    df = pd.read_csv(DATA_PATH)

    X_text = df["symptoms"].astype(str)
    y = df["condition"].astype(str)

    vectorizer = HashingVectorizer(
        n_features=2**12,
        alternate_sign=False,
        norm="l2"
    )

    X = vectorizer.transform(X_text)

    model = LinearSVC()
    model.fit(X, y)

    base_dir = os.path.dirname(__file__)
    joblib.dump(model, os.path.join(base_dir, "svm_model.pkl"))

    print("✅ Training complete (HashingVectorizer + Linear SVM).")


if __name__ == "__main__":
    train()
