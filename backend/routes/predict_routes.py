import os
import uuid
from flask import Blueprint, request, jsonify, current_app

from backend.ml.inference import MLInferenceService
from backend.ml.image_inference import ImageInferenceService
from backend.services.decision_service import DecisionService
from backend.llm.gemini_service import GeminiService
from backend.services.women_health_service import WomenHealthService

predict_bp = Blueprint("predict", __name__)

ml_service = MLInferenceService()
image_service = ImageInferenceService()
llm_service = GeminiService()


@predict_bp.route("/api/predict", methods=["POST"])
def predict():
    # ---------------- TEXT INPUT ----------------
    symptoms = request.form.get("symptoms", "").strip()
    if not symptoms:
        return jsonify({"error": "Symptoms are required"}), 400

    # ---------------- OPTIONAL IMAGE ----------------
    image = request.files.get("image")
    image_path = None

    if image:
        filename = f"{uuid.uuid4().hex}_{image.filename}"
        upload_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], filename
        )
        image.save(upload_path)
        image_path = upload_path

    # ---------------- TEXT ML INFERENCE ----------------
    ml_result = ml_service.predict(symptoms)

    # ---------------- IMAGE ANALYSIS (SEPARATE MODEL) ----------------
    image_analysis = None
    decision_note = None

    if image_path:
        image_analysis = image_service.analyze_image(image_path)
        decision_note = DecisionService.combine(
            ml_result, image_analysis
        )

    # ---------------- WOMEN HEALTH CONTEXT ----------------
    women_context = WomenHealthService.is_women_health_context(symptoms)
    women_condition = WomenHealthService.is_condition_women_related(
        ml_result["prediction"]
    )

    ml_result["women_health_context"] = {
        "enabled": women_context,
        "condition_related": women_condition
    }

    # ---------------- RESPONSE BASE ----------------
    response = {
        "ml_result": ml_result,
        "image_analysis": image_analysis,
        "decision_note": decision_note,
        "llm": None
    }

    # ---------------- OPTIONAL LLM ----------------
    try:
        if not ml_result["is_confident"]:
            response["llm"] = {
                "type": "follow_up_questions",
                "content": llm_service.generate_followup_questions(symptoms)
            }
        else:
            response["llm"] = {
                "type": "explanation",
                "content": llm_service.generate_explanation(
                    ml_result["prediction"]
                )
            }
    except Exception:
        response["llm"] = {
            "type": "unavailable",
            "content": "AI explanation service is currently unavailable."
        }

    # ---------------- DISCLAIMER ----------------
    if women_context:
        response["disclaimer"] = (
            "This tool is for informational purposes only and is not a medical diagnosis. "
            "Women’s health symptoms can vary widely. Please consult a healthcare professional."
        )

    # ---------------- CLEANUP ----------------
    if image_path and os.path.exists(image_path):
        os.remove(image_path)

    return jsonify(response), 200
