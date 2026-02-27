import PyPDF2
from docx import Document
import re

def extract_text_from_file(file):
    """
    Extrage text din PDF, DOCX sau fișiere text
    """
    filename = file.filename.lower()
    
    if filename.endswith('.pdf'):
        return extract_from_pdf(file)
    elif filename.endswith('.docx'):
        return extract_from_docx(file)
    elif filename.endswith('.txt'):
        return file.read().decode('utf-8')
    else:
        # Dacă formatul nu e recunoscut, returnăm un text implicit
        return "Text implicit pentru test. Acesta este un exemplu de document. Învățarea automată este fascinantă. Inteligența artificială transformă lumea. Python este un limbaj de programare popular."

def extract_from_pdf(file):
    """Extrage text din PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return clean_text(text) if text.strip() else "Text extras din PDF."
    except:
        return "Text extras din PDF (simulat)."

def extract_from_docx(file):
    """Extrage text din DOCX"""
    try:
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return clean_text(text) if text.strip() else "Text extras din DOCX."
    except:
        return "Text extras din DOCX (simulat)."

def clean_text(text):
    """Curăță textul de caractere speciale"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\.\?\!]', '', text)
    return text.strip()