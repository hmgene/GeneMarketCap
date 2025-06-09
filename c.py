import requests

query = "cancer"
url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax=10&retmode=json"
response = requests.get(url)

if response.status_code == 200:
    print(response.json())
else:
    print("Error:", response.status_code, response.text)

