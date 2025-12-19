class WomenHealthService:
    """
    Handles women-specific health context logic.
    This does NOT modify ML predictions.
    """

    WOMEN_KEYWORDS = [
        "period", "periods", "menstrual", "cycle",
        "pcos", "hormonal", "acne", "irregular periods",
        "missed periods", "cramps", "ovulation"
    ]

    WOMEN_RELATED_CONDITIONS = [
        "pcos",
        "hormonal acne"
    ]

    @staticmethod
    def is_women_health_context(symptoms_text: str) -> bool:
        text = symptoms_text.lower()
        return any(keyword in text for keyword in WomenHealthService.WOMEN_KEYWORDS)

    @staticmethod
    def is_condition_women_related(condition: str) -> bool:
        return condition.lower() in WomenHealthService.WOMEN_RELATED_CONDITIONS
