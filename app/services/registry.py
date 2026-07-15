import json
from pathlib import Path
from .predictor import MedicalPredictor, display_label

class PredictorRegistry:
    def __init__(self, app_root):
        self.root = Path(app_root)
        config_path = self.root / "config" / "model_registry.json"
        self.config = json.loads(config_path.read_text(encoding="utf-8"))
        self.cache = {}

    def has(self, key):
        return key in self.config

    def public_departments(self):
        result = []
        for key, item in self.config.items():
            info = json.loads((self.root / "config" / item["info"]).read_text(encoding="utf-8"))
            classes = json.loads((self.root / "config" / item["classes"]).read_text(encoding="utf-8"))
            result.append({
                "key": key,
                **item,
                "model_name": info.get("model_name", key),
                "architecture": info.get("architecture", "Unknown"),
                "input_size": info.get("input_size", [224, 224, 3]),
                "output_activation": info.get("output_activation", "softmax"),
                "classes": [display_label(x) for x in classes],
                "test_metrics": info.get("test_metrics", {}),
            })
        return result

    def predictor(self, key):
        if not self.has(key):
            raise KeyError(key)
        if key not in self.cache:
            cfg = self.config[key]
            self.cache[key] = MedicalPredictor(
                self.root / "models" / cfg["model"],
                self.root / "config" / cfg["classes"],
                self.root / "config" / cfg["info"],
            )
        return self.cache[key]

    def predict(self, key, image_path):
        return self.predictor(key).predict(image_path)
