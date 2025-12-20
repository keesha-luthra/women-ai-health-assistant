import os
import uuid
from flask import Blueprint, request, jsonify, current_app

from backend.ml.inference import MLInferenceService
from backend.ml.image_inference import ImageInferenceService
from backend.services.decision_service import DecisionService
from backend.services.women_health_service import WomenHealthService
from backend.llm.openai_service import OpenAIService

# ---------------- CONFIG ----------------

CONFIDENCE_THRESHOLD = 60  # percent (0–100)

HIGH_RISK_CONDITIONS = {
    "melanoma",
    "cancer",
    "tumor",
    "breast cancer",
    "ovarian cancer"
}

# ---------------- INIT ----------------

predict_bp = Blueprint("predict", __name__)

ml_service = MLInferenceService()
image_service = ImageInferenceService()
llm_service = OpenAIService()

# ---------------- ROUTE ----------------

@predict_bp.route("/api/predict", methods=["POST"])
def predict():
    # ---------------- INPUT ----------------
    symptoms = request.form.get("symptoms", "").strip()
    if not symptoms:
        return jsonify({"error": "Symptoms are required"}), 400

    image = request.files.get("image")
    image_path = None

    if image:
        filename = f"{uuid.uuid4().hex}_{image.filename}"
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)

    # ---------------- ML INFERENCE ----------------
    ml_result = ml_service.predict(symptoms)

    confidence = float(ml_result.get("confidence", 0))  # expected 0–100
    prediction = ml_result.get("prediction", "").lower()

    # ---------------- CONFIDENCE GATING ----------------
    is_confident = confidence >= CONFIDENCE_THRESHOLD
    is_high_risk = prediction in HIGH_RISK_CONDITIONS
    safe_mode = (not is_confident) or (is_high_risk and not image_path)

    ml_result["is_confident"] = is_confident
    ml_result["safe_mode"] = safe_mode

    if safe_mode:
        ml_result["prediction"] = "Insufficient information"
        ml_result["confidence_note"] = (
            "More details are needed before suggesting any condition."
        )

    # ---------------- IMAGE ANALYSIS ----------------
    image_analysis = None
    decision_note = None

    if image_path and not safe_mode:
        image_analysis = image_service.analyze_image(image_path)
        decision_note = DecisionService.combine(ml_result, image_analysis)

    # ---------------- WOMEN HEALTH CONTEXT ----------------
    women_context = WomenHealthService.is_women_health_context(symptoms)
    women_condition = WomenHealthService.is_condition_women_related(
        ml_result["prediction"]
    )

    ml_result["women_health_context"] = {
        "enabled": women_context,
        "condition_related": women_condition
    }

    # ---------------- LLM LOGIC ----------------
    llm_payload = None

    if safe_mode:
        # 🔒 SAFE MODE (NO EXTERNAL AI REQUIRED)
        llm_payload = {
            "type": "safe_mode",
            "content": (
                "To better understand what you’re experiencing, a few follow-up "
                "questions would help. For example:\n\n"
                "• How long have you noticed these symptoms?\n"
                "• Have they been getting worse or changing?\n"
                "• Are there any other symptoms you’ve observed?"
            )
        }

    elif not is_confident:
        # 🤖 LOW CONFIDENCE → LLM FOLLOW-UPS
        try:
            followups = llm_service.generate_followup_questions(symptoms)
            llm_payload = {
                "type": "followup",
                "content": followups
            }
        except Exception:
            llm_payload = {
                "type": "unavailable",
                "content": "AI follow-up questions are currently unavailable."
            }

    # ---------------- RESPONSE ----------------
    response = {
        "ml_result": ml_result,
        "image_analysis": image_analysis,
        "decision_note": decision_note,
        "llm": llm_payload
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
