class DecisionService:
    @staticmethod
    def combine(text_result, image_result):
        if not image_result:
            return "Text-based prediction only."

        if image_result["signal"] == "visual_patterns_detected":
            return (
                "The image shows visual patterns that may support "
                "the text-based analysis."
            )

        return "The image does not add strong visual support."
