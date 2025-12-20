class ImageInferenceService:
    """
    Image analysis service.
    TensorFlow is loaded lazily to avoid crashing the app on unsupported systems.
    """

    def __init__(self):
        self.available = True
        self.model = None

        try:
            import tensorflow as tf
            self.tf = tf
            self.model = tf.keras.applications.MobileNetV2(
                weights="imagenet",
                include_top=False,
                pooling="avg"
            )
        except Exception as e:
            # TensorFlow not available on this system
            self.available = False
            self.error = str(e)

    def analyze_image(self, image_path: str):
        if not self.available:
            return {
                "signal": "image_analysis_unavailable",
                "confidence": "none",
                "reason": "Image analysis not supported on this system."
            }

        try:
            import numpy as np
            from PIL import Image

            img = Image.open(image_path).convert("RGB").resize((224, 224))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            features = self.model.predict(img_array)
            feature_strength = float((features ** 2).sum() ** 0.5)

            if feature_strength > 20:
                return {
                    "signal": "visual_patterns_detected",
                    "confidence": "medium"
                }

            return {
                "signal": "no_strong_visual_patterns",
                "confidence": "low"
            }

        except Exception:
            return {
                "signal": "image_processing_failed",
                "confidence": "none"
            }
