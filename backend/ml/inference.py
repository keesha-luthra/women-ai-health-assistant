import os
import numpy as np
import joblib
from backend.services.image_feature_service import ImageFeatureService


class MLInferenceService:
    """
    Handles ML inference for the application.

    Supports:
    - Text-only inference (default)
    - Text + image inference (optional, supporting signal)

    The final prediction is always made by a classical ML model.
    """

    def __init__(self):
        # Load model artifacts relative to this file
        base_dir = os.path.dirname(__file__)

        self.vectorizer = joblib.load(
            os.path.join(base_dir, "tfidf_vectorizer.pkl")
        )
        self.model = joblib.load(
            os.path.join(base_dir, "logistic_model.pkl")
        )
        self.labels = joblib.load(
            os.path.join(base_dir, "labels.pkl")
        )

        # Image feature extractor (pretrained CNN, frozen)
        self.image_service = ImageFeatureService()

    def predict(self, symptoms_text: str, image_path: str = None):
        """
        Perform inference using text features and optional image features.

        Args:
            symptoms_text (str): User-provided symptom description
            image_path (str, optional): Path to uploaded image

        Returns:
            dict: Prediction result with confidence and metadata
        """

        # ---------------- TEXT FEATURES ----------------
        text_features = self.vectorizer.transform(
            [symptoms_text]
        ).toarray()

        # ---------------- IMAGE FEATURES (OPTIONAL) ----------------
        if image_path:
            image_features = self.image_service.extract_features(image_path)
            image_features = image_features.reshape(1, -1)

            # Combine text + image features
            combined_features = np.hstack(
                [text_features, image_features]
            )
        else:
            combined_features = text_features

        # ---------------- MODEL PREDICTION ----------------
        probabilities = self.model.predict_proba(combined_features)[0]
        max_index = probabilities.argmax()

        prediction = self.labels[max_index]
        confidence = float(probabilities[max_index])

        return {
            "prediction": prediction,
            "confidence": round(confidence, 3),
            "is_confident": confidence >= 0.6,
            "probabilities": {
                label: round(float(prob), 3)
                for label, prob in zip(self.labels, probabilities)
            },
            "used_image": bool(image_path)
        }
