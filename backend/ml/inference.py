import os
import joblib
from sklearn.feature_extraction.text import HashingVectorizer
import numpy as np

class MLInferenceService:
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        model_path = os.path.join(base_dir, "svm_model.pkl")

        self.model = joblib.load(model_path)

        # Must match training config
        self.vectorizer = HashingVectorizer(
            n_features=2**12,
            alternate_sign=False,
            norm="l2"
        )

    def predict(self, symptoms: str, image_path=None):
        X = self.vectorizer.transform([symptoms])

        prediction = self.model.predict(X)[0]

        # Multi-class decision scores
        decision_scores = self.model.decision_function(X)[0]

        # Confidence = margin between top two classes
        sorted_scores = np.sort(decision_scores)
        confidence = float(sorted_scores[-1] - sorted_scores[-2])

        confidence = max(0.0, min(confidence, 1.0))
        confidence_pct = round(confidence * 100, 1)

        is_confident = confidence >= 0.5  # tunable threshold

        return {
            "prediction": prediction,
            "confidence": confidence_pct,
            "is_confident": is_confident,
            "used_image": bool(image_path)
        }
