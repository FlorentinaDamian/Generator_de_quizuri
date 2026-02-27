import tensorflow as tf
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

class ModelTrainer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
        
    def create_advanced_models(self):
        """Creează modele avansate"""
        
        # 1. Model deep learning pentru nivel
        self.models['level_deep'] = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(20,)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.4),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(3, activation='softmax')
        ])
        
        # 2. Model LSTM pentru pattern-uri temporale
        self.models['level_lstm'] = tf.keras.Sequential([
            tf.keras.layers.LSTM(64, return_sequences=True, input_shape=(10, 5)),
            tf.keras.layers.LSTM(32),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(3, activation='softmax')
        ])
        
        # 3. Random Forest pentru clasificare robustă
        self.models['level_rf'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # 4. Random Forest pentru regresie (șanse)
        self.models['chances_rf'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        return self.models
    
    def generate_realistic_data(self, num_samples=10000):
        """Generează date realiste pentru antrenament"""
        
        X = []
        y_level = []
        y_chances = []
        
        for _ in range(num_samples):
            # Generează pattern-uri realiste de răspuns
            base_score = np.random.beta(2, 2)  # distribuit între 0 și 1
            
            # Adaugă variații
            answers = []
            for i in range(10):
                # Probabilitatea de a răspunde corect crește cu scorul de bază
                prob = base_score + np.random.normal(0, 0.1)
                prob = np.clip(prob, 0, 1)
                answers.append(1 if np.random.random() < prob else 0)
            
            # Features avansate
            features = []
            features.extend(answers)
            
            # Timpi de răspuns (simulați)
            response_times = np.random.exponential(scale=5, size=10)
            features.extend(response_times)
            
            # Corectitudine consecutivă
            consecutive_correct = 0
            max_consecutive = 0
            for a in answers:
                if a == 1:
                    consecutive_correct += 1
                    max_consecutive = max(max_consecutive, consecutive_correct)
                else:
                    consecutive_correct = 0
            features.append(max_consecutive)
            
            # Scor pe primele vs ultimele întrebări
            first_half = np.mean(answers[:5])
            second_half = np.mean(answers[5:])
            features.append(first_half - second_half)
            
            X.append(features)
            
            # Determină nivelul
            score = np.mean(answers)
            if score < 0.4:
                level = 0
                chances = score * 0.7 + np.random.normal(0, 0.05)
            elif score < 0.7:
                level = 1
                chances = score * 0.8 + np.random.normal(0, 0.05)
            else:
                level = 2
                chances = score * 0.9 + np.random.normal(0, 0.05)
            
            y_level.append(level)
            y_chances.append(np.clip(chances, 0, 1))
        
        return np.array(X), np.array(y_level), np.array(y_chances)
    
    def train_ensemble(self):
        """Antrenează un ansamblu de modele"""
        
        print("Generare date de antrenament...")
        X, y_level, y_chances = self.generate_realistic_data(20000)
        
        # Standardizare
        X_scaled = self.scaler.fit_transform(X)
        
        # Salvare scaler
        joblib.dump(self.scaler, 'models/scaler.pkl')
        
        # Antrenare modele deep learning
        print("\nAntrenare modele deep learning...")
        
        # Model pentru clasificare nivel
        level_model = self.create_advanced_models()['level_deep']
        level_model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        history = level_model.fit(
            X_scaled, y_level,
            validation_split=0.2,
            epochs=50,
            batch_size=64,
            verbose=1
        )
        
        # Salvare model
        level_model.save('models/level_model_v2.h5')
        
        # Model pentru predicție șanse
        chances_model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(X.shape[1],)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        chances_model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        history = chances_model.fit(
            X_scaled, y_chances,
            validation_split=0.2,
            epochs=50,
            batch_size=64,
            verbose=1
        )
        
        chances_model.save('models/chances_model_v2.h5')
        
        # Antrenare Random Forest
        print("\nAntrenare Random Forest...")
        rf_level = RandomForestClassifier(n_estimators=100, n_jobs=-1)
        rf_level.fit(X_scaled, y_level)
        joblib.dump(rf_level, 'models/rf_level.pkl')
        
        rf_chances = RandomForestRegressor(n_estimators=100, n_jobs=-1)
        rf_chances.fit(X_scaled, y_chances)
        joblib.dump(rf_chances, 'models/rf_chances.pkl')
        
        print("\n✅ Toate modelele au fost antrenate și salvate!")
        
        return {
            'level_deep': level_model,
            'chances_deep': chances_model,
            'level_rf': rf_level,
            'chances_rf': rf_chances
        }
    
    def load_ensemble_models(self):
        """Încarcă toate modelele pentru predicții ensemble"""
        
        models = {}
        
        # Încărcare modele deep learning
        if os.path.exists('models/level_model_v2.h5'):
            models['level_deep'] = tf.keras.models.load_model('models/level_model_v2.h5')
        
        if os.path.exists('models/chances_model_v2.h5'):
            models['chances_deep'] = tf.keras.models.load_model('models/chances_model_v2.h5')
        
        # Încărcare Random Forest
        if os.path.exists('models/rf_level.pkl'):
            models['level_rf'] = joblib.load('models/rf_level.pkl')
        
        if os.path.exists('models/rf_chances.pkl'):
            models['chances_rf'] = joblib.load('models/rf_chances.pkl')
        
        # Încărcare scaler
        if os.path.exists('models/scaler.pkl'):
            models['scaler'] = joblib.load('models/scaler.pkl')
        
        return models