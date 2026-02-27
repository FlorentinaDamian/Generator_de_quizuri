import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split

def create_level_classifier():
    """
    Model pentru clasificarea nivelului (3 clase)
    """
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax')  # 3 niveluri
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def create_chances_predictor():
    """
    Model pentru predicția șanselor de promovare (regresie)
    """
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(32, activation='relu', input_shape=(10,)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')  # valoare între 0 și 1
    ])
    
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    return model

def generate_training_data(num_samples=10000):
    """
    Generează date sintetice pentru antrenament
    """
    X = []  # răspunsuri (10 întrebări, 0/1)
    y_level = []  # nivel (0, 1, 2)
    y_chances = []  # șanse (0-1)
    
    for _ in range(num_samples):
        # Generează răspunsuri aleatorii
        answers = np.random.randint(0, 2, 10)
        score = answers.sum() / 10
        
        # Nivel pe baza scorului
        if score < 0.4:
            level = 0  # începător
            chances = np.random.uniform(0.2, 0.45)
        elif score < 0.7:
            level = 1  # intermediar
            chances = np.random.uniform(0.45, 0.75)
        else:
            level = 2  # avansat
            chances = np.random.uniform(0.75, 0.95)
        
        X.append(answers)
        y_level.append(level)
        y_chances.append(chances)
    
    return np.array(X), np.array(y_level), np.array(y_chances)

def train_and_save_models():
    """
    Antrenează și salvează ambele modele
    """
    print("Generare date de antrenament...")
    X, y_level, y_chances = generate_training_data(20000)
    
    # Împărțire în train/validation
    X_train, X_val, y_level_train, y_level_val, y_chances_train, y_chances_val = train_test_split(
        X, y_level, y_chances, test_size=0.2, random_state=42
    )
    
    # 1. Antrenare model nivel
    print("\nAntrenare model pentru clasificarea nivelului...")
    level_model = create_level_classifier()
    level_history = level_model.fit(
        X_train, y_level_train,
        validation_data=(X_val, y_level_val),
        epochs=50,
        batch_size=32,
        verbose=1
    )
    
    # 2. Antrenare model șanse
    print("\nAntrenare model pentru predicția șanselor...")
    chances_model = create_chances_predictor()
    chances_history = chances_model.fit(
        X_train, y_chances_train,
        validation_data=(X_val, y_chances_val),
        epochs=50,
        batch_size=32,
        verbose=1
    )
    
    # Salvare modele
    level_model.save('level_model.h5')
    chances_model.save('chances_model.h5')
    print("\nModele salvate cu succes!")
    
    # Evaluare
    level_loss, level_acc = level_model.evaluate(X_val, y_level_val)
    print(f"Acuratețe model nivel: {level_acc:.2%}")
    
    chances_loss, chances_mae = chances_model.evaluate(X_val, y_chances_val)
    print(f"Eroare medie model șanse: {chances_mae:.3f}")
    
    return level_model, chances_model

if __name__ == '__main__':
    train_and_save_models()