#  Quiz Generator AI

> A web application that automatically generates quizzes from PDF/DOCX documents using NLP and evaluates the user with TensorFlow models.

---
## Demo




https://github.com/user-attachments/assets/f317bfde-c1ff-4cc9-9d3f-2d26932c6fef




## Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  BROWSER - Frontend                     │
│           HTML + CSS + JavaScript                       │
│                                                         │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP Requests (fetch API)
                      │ POST /upload   → send document
                      │ POST /submit   → send answers
                      ▼
┌─────────────────────────────────────────────────────────┐
│                FLASK SERVER - Python                    │
│                  app.py (port 5000)                     │
│             Flask + Flask-CORS + REST API               │
└──────┬──────────────┬────────────────────────┬──────────┘
       │              │                        │
       ▼              ▼                        ▼
┌──────────┐  ┌───────────────┐  ┌────────────────────────┐
│ Document │  │   Question    │  │     Save Quiz          │
│Processing│  │  Generation   │  │  SQLite / PostgreSQL   │
│          │  │     NLP       │  │                        │
│ PyPDF2   │  │ Rule-based +  │  │  Tables:               │
│ python-  │  │ Transformers  │  │  - quizzes             │
│ docx     │  │ (extensible)  │  │  - questions           │
└──────────┘  └───────────────┘  │  - results             │
                                 └────────────────────────┘
                      │
                      │ After answers are submitted
                      ▼
┌─────────────────────────────────────────────────────────┐
│              TENSORFLOW - Python                        │
│                   ml_models.py                          │
│                                                         │
│  ┌──────────────────────┐  ┌───────────────────────┐   │
│  │  Model 1             │  │  Model 2              │   │
│  │  Level Classifier    │  │  Chance Predictor     │   │
│  │                      │  │                       │   │
│  │  Input: 5 features   │  │  Input: 5 features    │   │
│  │  Dense(32) → relu    │  │  Dense(32) → relu     │   │
│  │  Dropout(0.2)        │  │  Dense(16) → relu     │   │
│  │  Dense(16) → relu    │  │  Dense(1) → sigmoid   │   │
│  │  Dense(3) → softmax  │  │                       │   │
│  │                      │  │  Output: 0–100%       │   │
│  │  Output:             │  │  success probability  │   │
│  │  Beginner /          │  └───────────────────────┘   │
│  │  Intermediate /      │                              │
│  │  Advanced            │                              │
│  └──────────────────────┘                              │
└─────────────────────────────────────────────────────────┘
                      │
                      │ JSON response
                      ▼
┌─────────────────────────────────────────────────────────┐
│              BROWSER - Results                          │
│       { level: "Advanced", chances_percent: 87.3 }     │
└─────────────────────────────────────────────────────────┘
```

---

##  Project Structure

```
quiz_app/
│
├── backend/
│   ├── app.py                  # Flask server — routes & orchestration
│   ├── document_processor.py   # Text extraction from PDF and DOCX
│   ├── question_generator.py   # NLP-based question generation
│   ├── database.py             # SQLite — CRUD for quizzes
│   ├── ml_models.py            # TensorFlow — classification & prediction
│   ├── test_ai.py              # AI model testing script
│   ├── test_extract.py         # Text extraction testing script
│   ├── requirements.txt        # Python dependencies
│   ├── quiz_app.db             # SQLite database (auto-generated)
│   └── saved_models/           # Saved TF models (auto-generated)
│       ├── level_model.keras
│       └── chances_model.keras
│
├── frontend/
    └── index.html              # Single Page App — upload, quiz, results
```

---

##  Technologies Used

### Backend
| Technology  | Role |
|---|---|
| **Python** | Main backend language |
| **Flask** | Web server & REST API |
| **Flask-CORS** | Cross-Origin Resource Sharing |
| **PyPDF2** |  Text extraction from PDF files |
| **python-docx** |  Text extraction from Word files (.docx) |
| **TensorFlow** |ML models for classification & pre


diction |
| **NumPy** |  Numerical processing & feature engineering |
| **SQLite** | Local database for quizzes and results |

### Frontend
| Technology | Role |
|---|---|
| **HTML5** | Page structure |
| **CSS3** | Styling — gradients, animations, responsive layout |
| **JavaScript (Vanilla)** | Frontend logic — fetch API, DOM manipulation |

---

##  Running

### Step 1 — Start the Flask server
```bash
python app.py
```
You should see:
```
* Running on http://127.0.0.1:5000
* Debugger is active!
```

### Step 2 — Open the app
```
http://localhost:5000
```
> Flask automatically serves the frontend too. No separate server needed.

---

##  TensorFlow Models

### Model 1 — Level Classifier
- **Input:** 5-feature vector (score ratio, total questions, avg answer index, first correct, last correct)
- **Architecture:** Dense(32, relu) → Dropout(0.2) → Dense(16, relu) → Dense(3, softmax)
- **Output:** `Beginner` / `Intermediate` / `Advanced`

### Model 2 — Chance Predictor
- **Input:** same 5-feature vector
- **Architecture:** Dense(32, relu) → Dense(16, relu) → Dense(1, sigmoid)
- **Output:** success probability 0–100%

> Both models train automatically on first run using synthetic data and are saved to `saved_models/`. Replace synthetic data with real data in `ml_models.py` for production use.

---

