from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import random
import nltk
import numpy as np

class QuestionGenerator:
    def __init__(self):
        # Încărcare modele pentru limba română
        self.qa_pipeline = pipeline(
            "question-answering",
            model="readerbench/RoBERT-small"
        )
        
        # Model pentru generare întrebări
        self.qg_pipeline = pipeline(
            "text2text-generation",
            model="t5-small"  # sau model pentru română
        )
        
    def generate_advanced(self, text, num_questions=10, difficulty_levels=None):
        """Generează întrebări avansate cu niveluri de dificultate"""
        
        # Împarte textul în paragrafe
        paragraphs = self.split_into_paragraphs(text)
        
        questions = []
        for i, para in enumerate(paragraphs[:num_questions]):
            # Determină dificultatea
            if difficulty_levels:
                difficulty = difficulty_levels[i % len(difficulty_levels)]
            else:
                difficulty = self.estimate_difficulty(para)
            
            # Generează întrebare
            question = self.generate_question_from_text(para, difficulty)
            
            # Generează opțiuni
            options = self.generate_options_advanced(para, question['answer'], difficulty)
            
            questions.append({
                'id': i,
                'text': question['question'],
                'options': options,
                'correct': 0,
                'difficulty': difficulty,
                'explanation': question.get('explanation', ''),
                'context': para[:200] + '...'
            })
        
        return questions
    
    def generate_question_from_text(self, text, difficulty):
        """Generează întrebare folosind modelul T5"""
        try:
            # Prompt pentru generare întrebare
            prompt = f"generate question: {text}"
            
            result = self.qg_pipeline(
                prompt,
                max_length=100,
                num_return_sequences=1
            )
            
            question = result[0]['generated_text']
            
            # Folosește modelul QA pentru a găsi răspunsul
            answer = self.qa_pipeline({
                'question': question,
                'context': text
            })
            
            return {
                'question': question,
                'answer': answer['answer']
            }
            
        except:
            # Fallback la metodă simplă
            return self.generate_simple_question(text)
    
    def generate_simple_question(self, text):
        """Metodă simplă de generare (fallback)"""
        sentences = nltk.sent_tokenize(text)
        if not sentences:
            return {'question': 'Care este ideea principală?', 'answer': text[:100]}
        
        sentence = random.choice(sentences)
        words = nltk.word_tokenize(sentence)
        
        if len(words) > 5:
            keyword = random.choice([w for w in words if len(w) > 4])
            question = f"Ce înseamnă '{keyword}' în context?"
            return {'question': question, 'answer': sentence}
        
        return {'question': 'Despre ce este vorba în text?', 'answer': text[:100]}
    
    def generate_options_advanced(self, context, correct_answer, difficulty):
        """Generează opțiuni de răspuns inteligente"""
        
        options = [correct_answer]
        
        # Generează opțiuni greșite bazate pe context
        sentences = nltk.sent_tokenize(context)
        
        # Opțiuni greșite din alte părți ale textului
        for sent in sentences[:3]:
            if sent != correct_answer and len(sent) > 20:
                options.append(sent[:100])
        
        # Completează cu opțiuni generice
        while len(options) < 4:
            if difficulty == 'easy':
                options.append(f"Nu există informații suficiente")
            elif difficulty == 'medium':
                options.append(f"Textul nu specifică acest detaliu")
            else:
                options.append(f"Aceasta este o interpretare greșită")
        
        random.shuffle(options)
        return options[:4]
    
    def estimate_difficulty(self, text):
        """Estimează dificultatea textului"""
        # Factori: lungime propoziții, cuvinte rare, complexitate
        sentences = nltk.sent_tokenize(text)
        avg_sentence_len = np.mean([len(nltk.word_tokenize(s)) for s in sentences])
        
        if avg_sentence_len < 10:
            return 'easy'
        elif avg_sentence_len < 20:
            return 'medium'
        else:
            return 'hard'
    
    def split_into_paragraphs(self, text):
        """Împarte textul în paragrafe relevante"""
        # Împarte după linii goale sau punctuație
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Filtrează paragrafele prea scurte
        paragraphs = [p for p in paragraphs if len(p.split()) > 20]
        
        return paragraphs