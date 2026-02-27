from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils.document_parser import extract_text_from_file
from utils.quiz_generator import generate_questions
import numpy as np

app = Flask(__name__)
CORS(app)

# Versiune simplificată - fără TensorFlow
print("Aplicație pornită în modul simplificat (fără modele TensorFlow)")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Niciun fișier încărcat'}), 400
        
        file = request.files['file']
        text = extract_text_from_file(file)
        questions = generate_questions(text, num_questions=5)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'document_text': text[:200] + '...'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/evaluate', methods=['POST'])
def evaluate_answers():
    try:
        data = request.json
        answers = data.get('answers', [])
        
        # Calculează scorul
        score = sum(answers) / len(answers) * 100 if answers else 0
        
        # Reguli simple pentru nivel și șanse
        if score < 50:
            level = "Începător"
            chances = 30
        elif score < 75:
            level = "Intermediar"
            chances = 60
        else:
            level = "Avansat"
            chances = 90
        
        return jsonify({
            'success': True,
            'level': level,
            'chances': chances,
            'score': round(score, 1)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Server pornit pe http://localhost:5000")
    app.run(debug=True, port=5000)