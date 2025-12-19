from flask import Blueprint, request, jsonify
from backend.ml.inference import MLInferenceService
from backend.llm.gemini_service import GeminiService

predict_bp = Blueprint("predict", __name__)

ml_service = MLInferenceService()
llm_service = GeminiService()


@predict_bp.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json()

    if not data or "symptoms" not in data:
        return jsonify({"error": "Missing 'symptoms' field"}), 400

    symptoms = data["symptoms"].strip()

    if not symptoms:
        return jsonify({"error": "Symptoms cannot be empty"}), 400

    result = ml_service.predict(symptoms)

    response = {
        "ml_result": result,
        "llm": None
    }

    try:
        if not result["is_confident"]:
            response["llm"] = {
                "type": "follow_up_questions",
                "content": llm_service.generate_followup_questions(symptoms)
            }
        else:
            response["llm"] = {
                "type": "explanation",
                "content": llm_service.generate_explanation(result["prediction"])
            }

    except Exception:
        response["llm"] = {
            "type": "unavailable",
            "content": "AI explanation service is currently unavailable."
        }

    return jsonify(response), 200
