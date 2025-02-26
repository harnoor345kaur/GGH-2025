import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file"""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "\n".join([page.get_text("text") for page in doc])
    return text

