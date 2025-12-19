import os
import requests
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()


class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        # Current stable Gemini model
        self.endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-1.5-flash:generateContent"
        )

    def _call_gemini(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("Gemini API key not configured")

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                f"{self.endpoint}?key={self.api_key}",
                headers=headers,
                json=payload,     # IMPORTANT: use json= not data=
                timeout=15
            )

            response.raise_for_status()
            data = response.json()

            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            # TEMP debugging — safe because no secrets are printed
            if "response" in locals():
                print("DEBUG: Gemini response body:", response.text)
            raise

    def generate_followup_questions(self, symptoms: str) -> str:
        prompt = f"""
You are a women-focused health assistant.

The ML model is uncertain about the condition.

User symptoms:
"{symptoms}"

Ask 2–3 short, empathetic follow-up questions
to better understand the symptoms.

Rules:
- Do NOT diagnose
- Do NOT give medical advice
- Be supportive and inclusive
"""
        return self._call_gemini(prompt)

    def generate_explanation(self, condition: str) -> str:
        prompt = f"""
Explain what "{condition}" generally refers to
in simple, calm, non-alarming language.

Rules:
- Do NOT diagnose
- Do NOT give medical advice
- Encourage consulting a healthcare professional
- Use an empathetic tone
"""
        return self._call_gemini(prompt)
