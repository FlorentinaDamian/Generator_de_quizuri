import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

# Setare seed pentru reproducibilitate
np.random.seed(42)

# 1️⃣ Generarea datelor simulate
n_samples = 1000
data = pd.DataFrame({
    "avg_score": np.random.randint(0, 100, n_samples),
    "avg_time": np.random.randint(10, 120, n_samples),
    "correct_rate": np.random.uniform(0, 1, n_samples),
    "difficulty_avg": np.random.randint(1, 4, n_samples)
})

# 2️⃣ Crearea etichetei "level"
def assign_level(row):
    if row["avg_score"] > 75 and row["correct_rate"] > 0.7:
        return "advanced"
    elif row["avg_score"] > 50:
        return "intermediate"
    else:
        return "beginner"

data["level"] = data.apply(assign_level, axis=1)

# 3️⃣ Transformarea etichetei în valori numerice
level_map = {"beginner": 0, "intermediate": 1, "advanced": 2}
y = data["level"].map(level_map).values

# 4️⃣ Separarea caracteristicilor și a etichetei
X = data.drop("level", axis=1).values

# 5️⃣ Împărțirea în train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 6️⃣ Crearea modelului Keras
model = Sequential([
    Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
    Dense(16, activation='relu'),
    Dense(3, activation='softmax')  # 3 clase: beginner, intermediate, advanced
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# 7️⃣ Antrenarea modelului
model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.2)

# 8️⃣ Evaluarea modelului
loss, acc = model.evaluate(X_test, y_test)
print(f"\nAccuracy on test set: {acc:.2f}")

# 9️⃣ Prezicerea nivelurilor pe setul de test
y_pred_prob = model.predict(X_test)
y_pred = np.argmax(y_pred_prob, axis=1)

# 10️⃣ Maparea numerelor înapoi la nivel
inv_level_map = {v:k for k,v in level_map.items()}
y_pred_labels = [inv_level_map[i] for i in y_pred]
y_test_labels = [inv_level_map[i] for i in y_test]

# 11️⃣ Afișarea unui raport simplu
from sklearn.metrics import classification_report
print("\nClassification Report:")
print(classification_report(y_test_labels, y_pred_labels))

# 12️⃣ Salvarea modelului
model.save("student_level_tf_model.h5")
print("Model salvat cu succes!")