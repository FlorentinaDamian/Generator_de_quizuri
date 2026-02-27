"""
TensorFlow Models
─────────────────
Model 1 – Level Classifier  : Beginner / Intermediate / Advanced
Model 2 – Chance Predictor  : 0–100 % success probability

Both models are trained on-the-fly with synthetic data if no saved weights exist.
Replace synthetic data + retrain with your real dataset for production use.
"""

import numpy as np
import os
from typing import Dict, List

MODEL_DIR = "saved_models"
os.makedirs(MODEL_DIR, exist_ok=True)

LEVEL_LABELS = ["Beginner", "Intermediate", "Advanced"]


# ─── Feature engineering ──────────────────────────────────────────────────────

def _answers_to_features(answers: List[Dict]) -> np.ndarray:
    """
    Convert a list of answer objects to a fixed-size feature vector.

    Features:
        [0] score_ratio          – correct / total
        [1] total_questions
        [2] avg_answer_index     – avg position of selected option (0-3)
        [3] first_answer_correct – 1 if first question answered correctly
        [4] last_answer_correct  – 1 if last question answered correctly
    """
    total = len(answers)
    if total == 0:
        return np.zeros((1, 5), dtype=np.float32)

    correct_count = sum(1 for a in answers if a.get("selected") == a.get("correct"))
    score_ratio = correct_count / total
    avg_idx = np.mean([a.get("selected_index", 0) for a in answers])
    first_ok = 1.0 if answers[0].get("selected") == answers[0].get("correct") else 0.0
    last_ok  = 1.0 if answers[-1].get("selected") == answers[-1].get("correct") else 0.0

    return np.array([[score_ratio, total, avg_idx, first_ok, last_ok]], dtype=np.float32)


# ─── Model builders ───────────────────────────────────────────────────────────

def _build_level_model():
    import tensorflow as tf
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(5,)),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(3, activation="softmax"),   # 3 levels
    ], name="level_classifier")
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


def _build_chances_model():
    import tensorflow as tf
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(5,)),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid"),   # probability 0-1
    ], name="chance_predictor")
    model.compile(optimizer="adam", loss="mse")
    return model


# ─── Synthetic training data (replace with real data) ─────────────────────────

def _synthetic_data(n=500):
    np.random.seed(42)
    scores = np.random.uniform(0, 1, n)
    totals = np.random.randint(3, 20, n).astype(float)
    avg_idx = np.random.uniform(0, 3, n)
    first_ok = (np.random.rand(n) > 0.4).astype(float)
    last_ok  = (np.random.rand(n) > 0.4).astype(float)

    X = np.stack([scores, totals, avg_idx, first_ok, last_ok], axis=1).astype(np.float32)

    # Level: 0=Beginner (<0.4), 1=Intermediate (0.4-0.7), 2=Advanced (>0.7)
    y_level = np.where(scores < 0.4, 0, np.where(scores < 0.7, 1, 2)).astype(np.int32)

    # Chances: correlated with score + noise
    y_chances = np.clip(scores + np.random.normal(0, 0.1, n), 0, 1).astype(np.float32)

    return X, y_level, y_chances


# ─── Load or train models ─────────────────────────────────────────────────────

_level_model = None
_chances_model = None


def _get_models():
    global _level_model, _chances_model
    if _level_model and _chances_model:
        return _level_model, _chances_model

    level_path   = os.path.join(MODEL_DIR, "level_model.keras")
    chances_path = os.path.join(MODEL_DIR, "chances_model.keras")

    if os.path.exists(level_path) and os.path.exists(chances_path):
        import tensorflow as tf
        _level_model   = tf.keras.models.load_model(level_path)
        _chances_model = tf.keras.models.load_model(chances_path)
    else:
        print("[ML] Training models on synthetic data …")
        X, y_level, y_chances = _synthetic_data()

        _level_model = _build_level_model()
        _level_model.fit(X, y_level, epochs=20, verbose=0)
        _level_model.save(level_path)

        _chances_model = _build_chances_model()
        _chances_model.fit(X, y_chances, epochs=20, verbose=0)
        _chances_model.save(chances_path)
        print("[ML] Models trained and saved.")

    return _level_model, _chances_model


# ─── Public API ───────────────────────────────────────────────────────────────

def predict_level_and_chances(answers: List[Dict]) -> Dict:
    """
    Run both models and return:
        { "level": str, "chances_percent": float }
    """
    features = _answers_to_features(answers)
    level_model, chances_model = _get_models()

    level_probs = level_model.predict(features, verbose=0)[0]
    level_idx   = int(np.argmax(level_probs))
    level       = LEVEL_LABELS[level_idx]

    chances_raw     = float(chances_model.predict(features, verbose=0)[0][0])
    chances_percent = round(chances_raw * 100, 1)

    return {"level": level, "chances_percent": chances_percent}
