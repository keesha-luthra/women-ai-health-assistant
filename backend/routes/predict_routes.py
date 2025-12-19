from flask import Blueprint, request, jsonify
from backend.ml.inference import MLInferenceService

predict_bp = Blueprint("predict", __name__)

# Initialize ML service once
ml_service = MLInferenceService()


@predict_bp.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json()

    if not data or "symptoms" not in data:
        return jsonify({
            "error": "Missing 'symptoms' field in request body"
        }), 400

    symptoms_text = data["symptoms"].strip()

    if not symptoms_text:
        return jsonify({
            "error": "Symptoms text cannot be empty"
        }), 400

    try:
        result = ml_service.predict(symptoms_text)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500
