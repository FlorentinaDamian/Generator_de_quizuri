import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
np.random.seed(42)
n_samples = 1000
data = pd.DataFrame({
    "avg_score": np.random.randint(0, 100, n_samples),
    "avg_time": np.random.randint(10, 120, n_samples),
    "correct_rate": np.random.uniform(0, 1, n_samples),
    "difficulty_avg": np.random.randint(1, 4, n_samples)
})
def assign_level(row):
    if row["avg_score"] > 75 and row["correct_rate"] > 0.7:
        return "advanced"
    elif row["avg_score"] > 50:
        return "intermediate"
    else:
        return "beginner"
data["level"] = data.apply(assign_level, axis=1)
X = data.drop("level", axis=1)
y = data["level"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
model = RandomForestClassifier()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
joblib.dump(model, "student_level_model.pkl")
print("Model salvat cu succes!")