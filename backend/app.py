from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from document_processor import extract_text
from question_generator import generate_questions
from database import init_db, save_quiz, get_quiz
from ml_models import predict_level_and_chances

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db()


@app.route("/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    text = extract_text(filepath)
    if not text:
        return jsonify({"error": "Could not extract text from document"}), 422
    questions = generate_questions(text)
    quiz_id = save_quiz(filename, questions)
    return jsonify({"quiz_id": quiz_id, "questions": questions}), 200
@app.route("/quiz/<int:quiz_id>", methods=["GET"])
def get_quiz_route(quiz_id):
    quiz = get_quiz(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    return jsonify(quiz), 200
@app.route("/submit", methods=["POST"])
def submit_answers():
    """Step 5: Receive answers, run TensorFlow models, return level + chances."""
    data = request.get_json()
    answers = data.get("answers", [])       
    quiz_id = data.get("quiz_id")
    if not answers:
        return jsonify({"error": "No answers provided"}), 400
    result = predict_level_and_chances(answers)
    return jsonify({
        "quiz_id": quiz_id,
        "level": result["level"],         
        "chances_percent": result["chances_percent"]  
    }), 200
if __name__ == "__main__":
    app.run(debug=True, port=5000)
