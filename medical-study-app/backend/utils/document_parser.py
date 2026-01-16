import PyPDF2
from pptx import Presentation
from docx import Document
import os

class DocumentParser:
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")

    @staticmethod
    def parse_pptx(file_path: str) -> str:
        """Extract text from PowerPoint file."""
        try:
            prs = Presentation(file_path)
            text = ""
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing PPTX: {str(e)}")

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """Extract text from Word document."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")

    @staticmethod
    def parse_document(file_path: str) -> str:
        """Parse document based on file extension."""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            return DocumentParser.parse_pdf(file_path)
        elif ext in ['.pptx', '.ppt']:
            return DocumentParser.parse_pptx(file_path)
        elif ext in ['.docx', '.doc']:
            return DocumentParser.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def get_supported_extensions():
        """Return list of supported file extensions."""
        return ['.pdf', '.pptx', '.ppt', '.docx', '.doc']
