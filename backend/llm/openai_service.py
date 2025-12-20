import os
from openai import OpenAI

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")

    def generate_followup_questions(self, symptoms: str) -> str:
        prompt = f"""
You are a medical triage assistant.

User symptoms:
"{symptoms}"

Ask 2–3 short, respectful follow-up questions.
Do NOT diagnose.
Do NOT give treatment advice.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        return response.choices[0].message.content

    def generate_explanation(self, condition: str) -> str:
        prompt = f"""
Explain what "{condition}" generally means
in simple, non-alarming language.

Rules:
- Do NOT diagnose
- Do NOT give medical advice
- Encourage consulting a healthcare professional
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )

        return response.choices[0].message.content
