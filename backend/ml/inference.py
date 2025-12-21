import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

MODEL_DIR = "backend/ml/models"


class MLInferenceService:
    def __init__(self):
        self.embedding_model = joblib.load(
            f"{MODEL_DIR}/embedding_model.joblib"
        )
        self.embeddings = joblib.load(
            f"{MODEL_DIR}/symptom_embeddings.joblib"
        )
        self.metadata = joblib.load(
            f"{MODEL_DIR}/metadata.joblib"
        )

        # Normalize stored embeddings (important)
        self.embeddings = self.embeddings / np.linalg.norm(
            self.embeddings, axis=1, keepdims=True
        )

    def predict(self, symptoms: str):
        query_embedding = self.embedding_model.encode(
            [symptoms], convert_to_numpy=True
        )
        query_embedding = query_embedding / np.linalg.norm(
            query_embedding, axis=1, keepdims=True
        )

        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        top_k = 5
        top_indices = similarities.argsort()[-top_k:][::-1]

        top_conditions = self.metadata.iloc[top_indices]["condition"].tolist()
        best_score = float(similarities[top_indices[0]])

        # Majority vote
        prediction = max(set(top_conditions), key=top_conditions.count)
        support_count = top_conditions.count(prediction)

        # Confidence calculation
        sim_conf = np.clip((best_score - 0.45) / 0.35, 0, 1)
        support_conf = support_count / top_k
        confidence = round((0.7 * sim_conf + 0.3 * support_conf), 3)

        return {
            "prediction": str(prediction),
            "confidence": float(confidence),
            "similarity_score": float(best_score),
            "support_count": int(support_count),
            "is_confident": bool(confidence >= 0.65),
            "used_image": False
        }

