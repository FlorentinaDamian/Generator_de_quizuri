import re
import random
from typing import List, Dict
def generate_questions(text: str, num_questions: int = 5) -> List[Dict]:
    sentences = _clean_sentences(text)
    if len(sentences) < 4:
        raise ValueError("Document too short to generate questions.")

    questions = []
    used_indices = set()

    attempts = 0
    while len(questions) < num_questions and attempts < 100:
        attempts += 1
        idx = random.randint(0, len(sentences) - 1)
        if idx in used_indices:
            continue

        sentence = sentences[idx]
        words = sentence.split()
        if len(words) < 6:
            continue
        key_word = max(words, key=len)
        if len(key_word) < 4:
            continue

        question_text = sentence.replace(key_word, "________", 1)
        correct = key_word
        distractors = []
        for _ in range(20):
            d_idx = random.randint(0, len(sentences) - 1)
            if d_idx == idx:
                continue
            d_words = sentences[d_idx].split()
            candidate = max(d_words, key=len) if d_words else ""
            if candidate and candidate != correct and candidate not in distractors:
                distractors.append(candidate)
            if len(distractors) == 3:
                break

        if len(distractors) < 3:
            continue

        options = [correct] + distractors
        random.shuffle(options)

        questions.append({
            "id": len(questions) + 1,
            "question": f"Complete the sentence: {question_text}",
            "options": options,
            "correct_answer": correct,
        })
        used_indices.add(idx)

    return questions


def _clean_sentences(text: str) -> List[str]:
    """Split text into clean sentences."""
    raw = re.split(r"(?<=[.!?])\s+", text)
    cleaned = []
    for s in raw:
        s = s.strip()
        s = re.sub(r"\s+", " ", s)
        if len(s.split()) >= 6:
            cleaned.append(s)
    return cleaned
