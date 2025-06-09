from Bio import Entrez
import datetime, sys, csv
import xml.etree.ElementTree as ET

Entrez.email = "your_email@example.com"
today = datetime.date.today().strftime("%Y/%m/%d")

## Query PubMed for new articles mentioning "gene"
def pmid(q, d):
    query = f'{q}[Title/Abstract] AND ("{today}"[PDAT])'  # PDAT = Publication Date
    #query = f'("{today}"[PDAT])'  # PDAT = Publication Date
    handle = Entrez.esearch(db="pubmed", term=query, retmax=100)
    record = Entrez.read(handle)
    handle.close()
    pmids = record["IdList"]
    articles = []

    handle = Entrez.efetch(db="pubmed", id=",".join(pmids), rettype="abstract", retmode="xml")
    records = handle.read() 
    handle.close()
    return records

xmlfile="data/"+today.replace("/","_")+".xml"
records = pmid("lung",today)
with open(xmlfile, "w", encoding="utf-8") as f:
    f.write(records.decode("utf-8"))
tree = ET.parse(xmlfile)
root = tree.getroot()
articles = []

for article in root.findall(".//PubmedArticle"):
    pmid = article.find(".//PMID").text if article.find(".//PMID") is not None else "N/A"
    title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") is not None else "N/A"
    abstract_texts = article.findall(".//AbstractText")
    abstract = " ".join([abs_text.text for abs_text in abstract_texts if abs_text.text]) if abstract_texts else "N/A"
    articles.append({"PMID": pmid, "Title": title, "Abstract": abstract})

for article in articles:
    print(f"PMID: {article['PMID']}\nTitle: {article['Title']}\nAbstract: {article['Abstract']}\n{'-'*40}")

from Bio import Entrez

# Set email for NCBI Entrez
Entrez.email = "your_email@example.com"

def fetch_pubmed_articles(query, max_results=10):
    """Fetches PubMed articles for a given query and returns a list of dictionaries with PMID, Title, and Abstract."""
    
    # Search PubMed
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    handle.close()

    pmids = record["IdList"]  # List of PubMed IDs
    return articles


# Example usage
query = "cancer AND gene expression"
articles = fetch_pubmed_articles(query)

print(f"Saved {len(articles)} articles to pubmed_articles.csv")






import spacy
handle = Entrez.efetch(db="pubmed", id=",".join(pmids), rettype="abstract", retmode="text")
abstracts = handle.read()
handle.close()

# Load a biomedical NLP model (SciSpaCy)
nlp = spacy.load("en_ner_bionlp13cg_md")  

# Process the abstracts
doc = nlp(abstracts)

# Extract gene names
genes = set(ent.text for ent in doc.ents if ent.label_ == "GENE_OR_GENE_PRODUCT")
print("Extracted Genes:", genes)

