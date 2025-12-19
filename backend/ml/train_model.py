import pandas as pd
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


DATA_PATH = "data/symptoms_dataset.csv"
MODEL_PATH = "models/symptom_classifier.pkl"


def train():
    df = pd.read_csv(DATA_PATH)

    X = df["symptoms"]
    y = df["condition"]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english")),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    pipeline.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    print("Model trained and saved successfully.")


if __name__ == "__main__":
    train()
