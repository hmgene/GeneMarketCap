import requests
import pandas as pd
import xml.etree.ElementTree as ET

pmids = [
    "40764463",
    "40233738",
    "39923316",
    "39216838",
    "38914824",
    "38388531",
    "38260655",
    "37803141",
    "37131660",
    "36123820"
]

records = []

for pmid in pmids:
    url = f"https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocxml?pmids={pmid}&full=true"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"⚠️ Failed to fetch {pmid}")
        continue

    root = ET.fromstring(response.content)

    for passage in root.findall('.//passage'):
        for annotation in passage.findall('annotation'):
            infons = annotation.findall('infon')
            types = [i.text for i in infons if i.attrib.get('key') == 'type']
            if 'Gene' in types:
                gene_text = annotation.find('text').text
                records.append({"pubmed_id": pmid, "gene": gene_text})

# Convert to DataFrame
df_genes = pd.DataFrame(records)
print(df_genes)
df_genes.to_csv("o.csv")


