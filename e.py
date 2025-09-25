import pandas as pd
from Bio import Entrez
import datetime
import os

Entrez.email = "your.email@example.com"
DATA_PATH = "data/pubmed.csv"

def fetch_pubmed(term, max_records=100):
    handle = Entrez.esearch(db="pubmed", term=term, retmax=max_records, sort="pub+date")
    record = Entrez.read(handle)
    ids = record["IdList"]
    handle.close()

    abstracts = []
    for pmid in ids:
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        rec = Entrez.read(handle)
        handle.close()
        try:
            abstract = rec[0]["MedlineCitation"]["Article"]["Abstract"]["AbstractText"][0]
            title = rec[0]["MedlineCitation"]["Article"]["ArticleTitle"]
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            abstracts.append({"pmid": pmid, "title": title, "abstract": abstract, "date": date})
        except KeyError:
            continue

    return pd.DataFrame(abstracts)

if __name__ == "__main__":
    new_data = fetch_pubmed("gene regulation", max_records=100)

    if os.path.exists(DATA_PATH):
        old_data = pd.read_csv(DATA_PATH)
        combined = pd.concat([old_data, new_data]).drop_duplicates(subset="pmid")
    else:
        combined = new_data

    combined.to_csv(DATA_PATH, index=False)

