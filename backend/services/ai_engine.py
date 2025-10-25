import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import re
import tensorflow as tf
from pyod.models.combination import aom

from config import MODELS_DIR

class SecurityFeatureExtractor:
    def __init__(self):
        self.ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        self.port_pattern = re.compile(r':(\d{1,5})\b')
        self.error_pattern = re.compile(r'\b(error|fail|denied|unauthorized|forbidden|critical)\b', re.I)
        self.hex_pattern = re.compile(r'\b0x[0-9a-fA-F]+\b')
        self.suspicious_cmd = re.compile(r'\b(wget|curl|nc|bash|powershell|cmd|eval|exec)\b', re.I)

    def extract(self, message: str) -> dict:
        if not isinstance(message, str):
            message = ""
        return {
            'has_ip': int(bool(self.ip_pattern.search(message))),
            'ip_count': len(self.ip_pattern.findall(message)),
            'has_port': int(bool(self.port_pattern.search(message))),
            'has_error': int(bool(self.error_pattern.search(message))),
            'has_hex': int(bool(self.hex_pattern.search(message))),
            'has_suspicious_cmd': int(bool(self.suspicious_cmd.search(message))),
            'message_length': len(message),
            'special_char_ratio': sum(1 for c in message if not c.isalnum()) / max(len(message), 1),
            'digit_ratio': sum(1 for c in message if c.isdigit()) / max(len(message), 1),
            'uppercase_ratio': sum(1 for c in message if c.isupper()) / max(len(message), 1),
        }

class AIEngine:
    """Embedded TinyML & PyOD anomaly detection"""

    def __init__(self, model_dir: Path = None):
        self.model_dir = model_dir or MODELS_DIR
        self.extractor = SecurityFeatureExtractor()
        
        # Load models
        try:
            self.iforest = joblib.load(self.model_dir / "iforest_model.pkl")
            self.lof = joblib.load(self.model_dir / "lof_model.pkl")
            self.vectorizer = joblib.load(self.model_dir / "tfidf_vectorizer (1).pkl")
            self.scaler = joblib.load(self.model_dir / "security_features_scaler.pkl")
            
            # Load TFLite model
            self.interpreter = tf.lite.Interpreter(model_path=str(self.model_dir / "autoencoder.tflite"))
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            print(f"✅ AI models loaded from {self.model_dir}")
        except Exception as e:
            raise RuntimeError(f"❌ Model files not found or failed to load from {self.model_dir}: {e}")

    def analyze(self, messages: list) -> dict:
        """
        Perform anomaly detection on log messages
        Returns: {"anomalies": [...], "scores": [...]}
        """
        if not messages:
            return {"anomalies": [], "scores": [], "total_analyzed": 0, "anomaly_count": 0}

        # 1. Feature Engineering
        X_tfidf = self.vectorizer.transform(messages).toarray()
        
        security_features = [list(self.extractor.extract(msg).values()) for msg in messages]
        X_security = np.array(security_features)
        X_security_scaled = self.scaler.transform(X_security)
        
        X_combined = np.hstack([X_tfidf, X_security_scaled]).astype(np.float32)

        # 2. Ensemble Prediction (IForest + LOF)
        iforest_scores = self.iforest.decision_function(X_combined)
        lof_scores = self.lof.decision_function(X_combined)
        scores_matrix = np.column_stack([iforest_scores, lof_scores])
        ensemble_scores = aom(scores_matrix, n_buckets=2)
        
        # 3. Autoencoder Prediction (TFLite)
        self.interpreter.set_tensor(self.input_details[0]['index'], X_combined)
        self.interpreter.invoke()
        reconstructed = self.interpreter.get_tensor(self.output_details[0]['index'])
        mse_scores = np.mean(np.square(X_combined - reconstructed), axis=1)

        # 4. Combine and format results
        # Using a simple average of normalized scores for a final score
        final_scores = (ensemble_scores / np.max(ensemble_scores) + mse_scores / np.max(mse_scores)) / 2
        
        # Using a percentile-based threshold for anomalies
        threshold = np.percentile(final_scores, 90) 
        predictions = (final_scores > threshold).astype(int)

        anomalies = []
        for idx, (score, pred) in enumerate(zip(final_scores, predictions)):
            if pred == 1:
                anomalies.append({
                    "index": idx,
                    "message": messages[idx],
                    "score": float(score),
                    "severity": "high" if score > (threshold * 1.2) else "medium"
                })

        return {
            "anomalies": anomalies,
            "scores": final_scores.tolist(),
            "total_analyzed": len(messages),
            "anomaly_count": len(anomalies)
        }