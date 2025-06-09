def fetch_pubmed_articles(query, max_results=100):
    pmids = fetch_pmids(query, max_results)
    all_data = []
    for pmid in pmids:
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="text")
            record = Entrez.read(handle)
            handle.close()
            article = record["PubmedArticle"][0]
            title = article["MedlineCitation"]["Article"]["ArticleTitle"]
            abstract_text = article["MedlineCitation"]["Article"]["Abstract"]["AbstractText"][0]
            authors = article["MedlineCitation"]["Article"]["AuthorList"]
            author_names = ["{} {}".format(a["ForeName"], a["LastName"]) for a in authors if "ForeName" in a and "LastName" in a]
            genes = extract_gene_like_entities(abstract_text)
            all_data.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract_text,
                "author_list": "; ".join(author_names),
                "genes_found": "; ".join(genes)
            })
            time.sleep(0.4)  # Be respectful to NCBI
        except Exception as e:
            print(f"Error fetching PMID {pmid}: {e}")
    df = pd.DataFrame(all_data)
    df.to_csv("pubmed_articles.csv", index=False)
    return df

from Bio import Entrez
import time
import pandas as pd

Entrez.email = "your_email@example.com"  # Always set this

def fetch_pubmed_articles(query, retmax=10):
    handle = Entrez.esearch(db="pubmed", term=query, retmax=retmax)
    record = Entrez.read(handle)
    handle.close()
    pmids = record["IdList"]
    all_data = []
    for pmid in pmids:
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="text")
            record = Entrez.read(handle)
            handle.close()
            article = record["PubmedArticle"][0]
            title = str(article["MedlineCitation"]["Article"]["ArticleTitle"])
            abstract_list = article["MedlineCitation"]["Article"].get("Abstract", {}).get("AbstractText", [])
            abstract_text = " ".join([str(t) for t in abstract_list]) if abstract_list else ""
            authors = article["MedlineCitation"]["Article"].get("AuthorList", [])
            author_names = [
                "{} {}".format(a.get("ForeName", ""), a.get("LastName", ""))
                for a in authors if "LastName" in a
            ]
            all_data.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract_text,
                "authors": "; ".join(author_names)
            })
            time.sleep(0.4)  # Be polite to NCBI
        except Exception as e:
            print(f"Error fetching PMID {pmid}: {e}")
            continue
    df = pd.DataFrame(all_data)
    return df

# Example usage
query = "cancer AND gene expression"
articles = fetch_pubmed_articles(query)
print(f"Fetched {len(articles)} articles")
articles.to_csv("pubmed_articles.csv", index=False)

