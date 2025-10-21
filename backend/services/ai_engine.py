import joblib
import numpy as np
from pathlib import Path
from config import MODELS_DIR

class AIEngine:
    """Embedded TinyML & PyOD anomaly detection"""

    def __init__(self, model_path: Path = None):
        self.model_path = model_path or MODELS_DIR / "iforest_model.pkl"
        self.vectorizer_path = MODELS_DIR / "tfidf_vectorizer.pkl"

        # Load pre-trained models
        try:
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
            print(f"✅ AI models loaded from {self.model_path}")
        except FileNotFoundError:
            raise RuntimeError(f"❌ Model files not found in {MODELS_DIR}")

    def analyze(self, messages: list) -> dict:
        """
        Perform anomaly detection on log messages
        Returns: {"anomalies": [...], "scores": [...]}
        """
        if not messages:
            return {"anomalies": [], "scores": []}

        # Vectorize messages
        X = self.vectorizer.transform(messages)

        # Get anomaly scores
        scores = self.model.decision_function(X.toarray())
        predictions = self.model.predict(X.toarray())

        # Format results
        anomalies = []
        for idx, (score, pred) in enumerate(zip(scores, predictions)):
            if pred == 1:  # Anomaly detected
                anomalies.append({
                    "index": idx,
                    "message": messages[idx],
                    "score": float(score),
                    "severity": "high" if score > 0.5 else "medium"
                })

        return {
            "anomalies": anomalies,
            "scores": scores.tolist(),
            "total_analyzed": len(messages),
            "anomaly_count": len(anomalies)
        }
    
    