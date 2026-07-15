import json
from pathlib import Path
import numpy as np
from PIL import Image
from tensorflow import keras

def display_label(label):
    replacements = {
        "diabetic_retinopathy": "Diabetic Retinopathy",
        "Tooth_discoloration_augmented": "Tooth Discoloration",
        "NORMAL": "Normal",
        "PNEUMONIA": "Pneumonia",
        "Unknown_Normal": "Unknown / Normal-like",
    }
    return replacements.get(label, label.replace("_", " ").title())

class MedicalPredictor:
    def __init__(self, model_path, class_path, info_path):
        self.model_path = Path(model_path)
        self.class_path = Path(class_path)
        self.info_path = Path(info_path)

        self.class_names = json.loads(self.class_path.read_text(encoding="utf-8"))
        self.info = json.loads(self.info_path.read_text(encoding="utf-8"))

        size = self.info.get("input_size", [224, 224, 3])
        self.input_size = (int(size[0]), int(size[1]))
        self.activation = str(self.info.get("output_activation", "softmax")).lower()
        self.threshold = float(self.info.get("threshold", 0.5))
        self.confidence_threshold = float(self.info.get("confidence_threshold", 0.0))

        self.model = keras.models.load_model(self.model_path, compile=False)

    def prepare(self, image_path):
        image = Image.open(image_path).convert("RGB")
        image = image.resize(self.input_size)
        arr = np.asarray(image, dtype=np.float32)
        return np.expand_dims(arr, axis=0)

    def predict(self, image_path):
        raw = self.model.predict(self.prepare(image_path), verbose=0)

        if self.activation == "sigmoid":
            positive = float(np.asarray(raw).reshape(-1)[0])
            positive = min(max(positive, 0.0), 1.0)
            probabilities = np.array([1.0 - positive, positive], dtype=float)
        else:
            probabilities = np.asarray(raw)[0].astype(float)

        best_index = int(np.argmax(probabilities))
        confidence = float(probabilities[best_index])

        items = [
            {
                "label": label,
                "display_label": display_label(label),
                "probability": round(float(prob) * 100, 2),
            }
            for label, prob in zip(self.class_names, probabilities)
        ]
        items.sort(key=lambda item: item["probability"], reverse=True)

        return {
            "prediction": self.class_names[best_index],
            "display_prediction": display_label(self.class_names[best_index]),
            "confidence": round(confidence * 100, 2),
            "uncertain": bool(self.confidence_threshold and confidence < self.confidence_threshold),
            "all_predictions": items,
            "top_predictions": items[:5],
            "model_name": self.info.get("model_name", self.model_path.stem),
            "architecture": self.info.get("architecture", "Unknown"),
        }
