from flask import Blueprint, request, jsonify
from backend.llm.gemini_service import GeminiService

llm_bp = Blueprint("llm", __name__)
llm_service = GeminiService()


@llm_bp.route("/api/llm/followup", methods=["POST"])
def followup():
    data = request.get_json() or {}
    symptoms = data.get("symptoms", "").strip()

    if not symptoms:
        return jsonify({"error": "Symptoms are required"}), 400

    # 🔥 IMPORTANT: NO TRY/EXCEPT THAT RETURNS ERRORS
    # GeminiService already handles fallback internally
    content = llm_service.generate_followup_questions(symptoms)

    return jsonify({"content": content}), 200


@llm_bp.route("/api/llm/explain", methods=["POST"])
def explain():
    data = request.get_json() or {}
    condition = data.get("condition", "").strip()

    if not condition:
        return jsonify({"error": "Condition is required"}), 400

    content = llm_service.generate_explanation(condition)

    return jsonify({"content": content}), 200
