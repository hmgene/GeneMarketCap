import fitz


def extract_text(pdf_path: str) -> str:

    doc = fitz.open(pdf_path)

    text = []

    for page in doc:
        text.append(page.get_text())

    return "\n".join(text)
