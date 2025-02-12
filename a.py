from Bio import Entrez
import datetime

# Set your email for NCBI API
Entrez.email = "your_email@example.com"

# Get today's date in YYYY/MM/DD format
today = datetime.date.today().strftime("%Y/%m/%d")
print(today)

# Query PubMed for new articles mentioning "gene"
query = f'gene[Title/Abstract] AND ("{today}"[PDAT])'  # PDAT = Publication Date
handle = Entrez.esearch(db="pubmed", term=query, retmax=100)
record = Entrez.read(handle)
handle.close()

# Get PubMed IDs (PMIDs)
pmids = record["IdList"]
print("New PubMed articles today:", pmids)

import spacy

# Load PubMed abstract extraction
handle = Entrez.efetch(db="pubmed", id=",".join(pmids), rettype="abstract", retmode="text")
abstracts = handle.read()
handle.close()

# Load a biomedical NLP model (SciSpaCy)
nlp = spacy.load("en_core_sci_sm")  # Install via: pip install scispacy && pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.0/en_core_sci_sm-0.5.0.tar.gz

# Process the abstracts
doc = nlp(abstracts)

# Extract gene names
genes = set(ent.text for ent in doc.ents if ent.label_ == "GENE_OR_GENE_PRODUCT")
print("Extracted Genes:", genes)

