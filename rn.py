# Example using Entrez ESearch
from Bio import Entrez
Entrez.email = "your_email@example.com"

def search_gene_day(gene_name, date_str):
    query = f'"{gene_name}"[Title/Abstract] AND {date_str}[PDAT]'
    handle = Entrez.esearch(db="pubmed", term=query, retmax=10000)
    record = Entrez.read(handle)
    return record['IdList']

