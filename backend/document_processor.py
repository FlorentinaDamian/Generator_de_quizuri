import os

def extract_text(filepath: str) -> str:
    """
    Extract plain text from PDF or DOCX files.
    Uses PyPDF2 for PDFs and python-docx for Word documents.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        return _extract_from_pdf(filepath)
    elif ext in (".docx", ".doc"):
        return _extract_from_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_from_pdf(filepath: str) -> str:
    try:
        import PyPDF2
        text_parts = []
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except ImportError:
        raise ImportError("Install PyPDF2: pip install PyPDF2")


def _extract_from_docx(filepath: str) -> str:
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except ImportError:
        raise ImportError("Install python-docx: pip install python-docx")
