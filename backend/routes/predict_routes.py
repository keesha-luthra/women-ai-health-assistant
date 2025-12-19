from flask import Blueprint, request, jsonify
from backend.ml.inference import MLInferenceService
from backend.llm.gemini_service import GeminiService
from backend.services.women_health_service import WomenHealthService

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

    # ML inference
    result = ml_service.predict(symptoms)

    # Women-specific context detection
    women_context = WomenHealthService.is_women_health_context(symptoms)
    women_condition = WomenHealthService.is_condition_women_related(
        result["prediction"]
    )

    result["women_health_context"] = {
        "enabled": women_context,
        "condition_related": women_condition
    }

    response = {
        "ml_result": result,
        "llm": None
    }

    # LLM logic (optional, non-blocking)
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

    # Ethical disclaimer for women-specific context
    if women_context:
        response["disclaimer"] = (
            "This tool is for informational purposes only and is not a medical diagnosis. "
            "Women’s health symptoms can vary widely, so consider consulting a qualified "
            "healthcare professional for personalized advice."
        )

    return jsonify(response), 200
