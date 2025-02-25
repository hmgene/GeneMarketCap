import fitz  # PyMuPDF for extracting text
import spacy

# Load the SciSpaCy biomedical NER model
nlp = spacy.load("en_ner_bionlp13cg_md")

# Step 1: Extract Text from PDF
def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    return text

# Step 2: Extract Gene Names Using SciSpaCy
def extract_gene_names(text):
    """Uses SciSpaCy's biomedical NER model to extract gene names."""
    doc = nlp(text)
    #genes = {ent.text for ent in doc.ents if ent.label_ in {"GENE_OR_GENE_PRODUCT"}}
    genes = {ent.text for ent in doc.ents if ent.label_ in {"CELL"}}
    return sorted(genes)

if __name__ == "__main__":
    pdf_path = "data/s41577-025-01129-6.pdf"  # Change to your actual file

    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)

    # Extract gene names
    genes = extract_gene_names(text)

    print("Extracted Gene Names:", genes if genes else "No gene names found.")

