from openai import OpenAI
import os


class GeminiService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ OpenAI API key missing — fallback mode enabled")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
            print("✅ OpenAI client initialized")

    def generate_followup_questions(self, symptoms: str) -> str:
        if not self.client:
            return self._fallback_followup(symptoms)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a gentle health assistant. "
                            "Ask 2–3 short follow-up questions. "
                            "Do NOT diagnose. Do NOT give treatment advice."
                        )
                    },
                    {"role": "user", "content": symptoms}
                ],
                temperature=0.4
            )
            return response.choices[0].message.content

        except Exception as e:
            print("🔥 LLM ERROR:", e)
            return self._fallback_followup(symptoms)

    def generate_explanation(self, condition: str) -> str:
        if not self.client:
            return self._fallback_explanation(condition)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Explain medical conditions simply and safely. "
                            "Do NOT diagnose. Encourage professional consultation."
                        )
                    },
                    {"role": "user", "content": condition}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content

        except Exception as e:
            print("🔥 LLM ERROR:", e)
            return self._fallback_explanation(condition)

    # ---------------- FALLBACKS ----------------

    def _fallback_followup(self, symptoms: str) -> str:
        return (
            "I need a little more information to understand this better:\n"
            "• When did these symptoms begin?\n"
            "• Are they constant or do they come and go?\n"
            "• Have you noticed any recent changes or triggers?"
        )

    def _fallback_explanation(self, condition: str) -> str:
        return (
            f"'{condition}' is a term often used to describe a group of related symptoms. "
            "Only a qualified healthcare professional can provide an accurate diagnosis."
        )
