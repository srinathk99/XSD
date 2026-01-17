
import pdfplumber

def read_pdf(path: str) -> str:
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def load_xsd_as_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
