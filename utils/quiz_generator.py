import random
import re

def generate_questions(text, num_questions=5):
    """
    Generează întrebări pe baza textului
    """
    # Împărțim textul în propoziții
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Dacă nu sunt destule propoziții, folosim paragrafe
    if len(sentences) < num_questions:
        paragraphs = text.split('\n\n')
        sentences = [p for p in paragraphs if len(p) > 30]
    
    # Dacă tot nu sunt destule, generăm întrebări implicite
    if len(sentences) < num_questions:
        return generate_fallback_questions(text, num_questions)
    
    # Selectăm aleatoriu propoziții pentru întrebări
    selected = random.sample(sentences, min(num_questions, len(sentences)))
    
    questions = []
    for i, sentence in enumerate(selected):
        # Extragem cuvinte cheie
        words = sentence.split()
        # Cuvinte cu lungime > 4 (probabil cuvinte importante)
        keywords = [w for w in words if len(w) > 4 and w.lower() not in ['acesta', 'aceasta', 'pentru', 'despre']]
        
        if keywords:
            keyword = keywords[0]
        else:
            keyword = "acest concept"
        
        # Generăm întrebare
        question = {
            'id': i,
            'text': f"Care dintre următoarele afirmații este corectă despre '{keyword}' în text?",
            'options': generate_options(sentence, keyword),
            'correct': 0  # prima opțiune e cea corectă
        }
        questions.append(question)
    
    # Dacă nu am generat suficiente întrebări, completăm cu întrebări implicite
    while len(questions) < num_questions:
        questions.append(generate_simple_question(len(questions)))
    
    return questions

def generate_options(sentence, keyword):
    """Generează opțiuni de răspuns"""
    # Opțiunea corectă - un fragment din text
    corect = sentence[:100] + "..." if len(sentence) > 100 else sentence
    
    # Opțiuni greșite
    gresite = [
        f"Textul nu menționează nimic despre {keyword}",
        f"Afirmația contrazice ideea principală despre {keyword}",
        f"Nu există informații suficiente despre {keyword} în text",
        f"{keyword} nu este definit în contextul dat"
    ]
    
    # Amestecăm opțiunile
    all_options = [corect] + gresite[:3]  # luăm doar 3 greșite
    random.shuffle(all_options)
    
    return all_options

def generate_fallback_questions(text, num_questions):
    """Generează întrebări implicite când textul e prea scurt"""
    questions = []
    for i in range(num_questions):
        question = {
            'id': i,
            'text': f"Întrebarea {i+1} despre textul încărcat",
            'options': [
                f"Opțiunea A pentru întrebarea {i+1}",
                f"Opțiunea B pentru întrebarea {i+1}",
                f"Opțiunea C pentru întrebarea {i+1}",
                f"Opțiunea D pentru întrebarea {i+1}"
            ],
            'correct': 0
        }
        questions.append(question)
    return questions

def generate_simple_question(index):
    """Generează o întrebare simplă de completare"""
    return {
        'id': index,
        'text': f"Întrebare suplimentară {index+1}",
        'options': [
            "Prima variantă de răspuns",
            "A doua variantă de răspuns", 
            "A treia variantă de răspuns",
            "A patra variantă de răspuns"
        ],
        'correct': 0
    }