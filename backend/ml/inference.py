import pickle
import os
import numpy as np

MODEL_PATH = "models/symptom_classifier.pkl"
LOW_CONFIDENCE_THRESHOLD = 0.5


class MLInferenceService:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Trained ML model not found. Please train the model first."
            )

        with open(MODEL_PATH, "rb") as f:
            self.pipeline = pickle.load(f)

        # Class labels learned by Logistic Regression
        self.labels = self.pipeline.classes_

    def predict(self, text: str):
        """
        Predict condition probabilities from symptom text.

        Returns:
            dict: {
                prediction: str,
                confidence: float,
                is_confident: bool,
                probabilities: {label: probability}
            }
        """

        # Predict probabilities
        probabilities = self.pipeline.predict_proba([text])[0]

        # Find top prediction
        top_index = np.argmax(probabilities)
        top_label = self.labels[top_index]
        top_confidence = probabilities[top_index]

        # Confidence check
        is_confident = bool(top_confidence >= LOW_CONFIDENCE_THRESHOLD)

        return {
            "prediction": top_label,
            "confidence": round(float(top_confidence), 3),
            "is_confident": is_confident,
            "probabilities": {
                label: round(float(prob), 3)
                for label, prob in zip(self.labels, probabilities)
            }
        }
