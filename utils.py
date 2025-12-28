import os
from dotenv import load_dotenv
import google.generativeai as genai
from PyPDF2 import PdfReader
import docx

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

# Configure Gemini
genai.configure(api_key=API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-pro")


def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def get_answer_from_doc(file_path, question):
    if file_path.endswith(".pdf"):
        content = read_pdf(file_path)
    elif file_path.endswith(".docx"):
        content = read_docx(file_path)
    else:
        return "Unsupported file format"

    prompt = f"""
    Answer the question using the document below.

    Document:
    {content}

    Question:
    {question}
    """

    response = model.generate_content(prompt)
    return response.text
