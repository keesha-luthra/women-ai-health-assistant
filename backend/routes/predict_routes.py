import os
import uuid
from flask import Blueprint, request, jsonify, current_app

from backend.ml.inference import MLInferenceService
from backend.ml.image_inference import ImageInferenceService
from backend.services.decision_service import DecisionService
from backend.llm.openai_service import OpenAIService

CONFIDENCE_THRESHOLD = 0.60

predict_bp = Blueprint("predict", __name__)

# Initialize services ONCE
ml_service = MLInferenceService()
image_service = ImageInferenceService()
llm_service = OpenAIService()


@predict_bp.route("/api/predict", methods=["POST"])
def predict():
    # ---------------- INPUT ----------------
    symptoms = request.form.get("symptoms", "").strip()
    mode = request.form.get("mode", "general").lower()

    if not symptoms:
        return jsonify({"error": "Symptoms are required"}), 400

    # ---------------- IMAGE ----------------
    image = request.files.get("image")
    image_path = None

    if image:
        filename = f"{uuid.uuid4().hex}_{image.filename}"
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)

    # ---------------- ML INFERENCE (DO NOT TOUCH OUTPUT) ----------------
    ml_result = ml_service.predict(symptoms)

    # Hard guarantee: confidence is always 0–1
    confidence = float(ml_result.get("confidence", 0.0))
    is_low_confidence = confidence < CONFIDENCE_THRESHOLD

    # ---------------- IMAGE ANALYSIS (OPTIONAL, NON-DESTRUCTIVE) ----------------
    image_analysis = None
    decision_note = None

    if image_path:
        image_analysis = image_service.analyze_image(image_path)
        # IMPORTANT: combine must NOT mutate ml_result
        decision_note = DecisionService.combine(
            ml_result=ml_result,
            image_analysis=image_analysis
        )

    # ---------------- MODE METADATA (UI-ONLY) ----------------
    women_context = (mode == "women")

    # ---------------- LLM FOLLOW-UP (UX ONLY) ----------------
    llm_payload = None

    if is_low_confidence:
        try:
            llm_payload = {
                "type": "followup",
                "content": llm_service.generate_followup_questions(symptoms)
            }
        except Exception:
            llm_payload = {
                "type": "unavailable",
                "content": "AI follow-up questions are currently unavailable."
            }

    # ---------------- RESPONSE (STRICT CONTRACT) ----------------
    response = {
        "mode": mode,
        "ml_result": {
            "prediction": ml_result["prediction"],
            "confidence": confidence,
            "similarity_score": ml_result.get("similarity_score"),
            "support_count": ml_result.get("support_count"),
            "is_confident": ml_result.get("is_confident"),
            "used_image": ml_result.get("used_image", False),
        },
        "image_analysis": image_analysis,
        "decision_note": decision_note,
        "llm": llm_payload
    }

    if women_context:
        response["disclaimer"] = (
            "This tool is for informational purposes only and is not a medical diagnosis. "
            "Women’s health symptoms can vary widely. Please consult a healthcare professional."
        )

    # ---------------- CLEANUP ----------------
    if image_path and os.path.exists(image_path):
        os.remove(image_path)

    return jsonify(response), 200
