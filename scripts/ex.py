import requests
import xml.etree.ElementTree as ET

url = "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/publications/export/biocxml?pmids=36002195&full=true"
response = requests.get(url)
xml_data = response.content

root = ET.fromstring(xml_data)

gene_mentions = []

# Iterate through passages and annotations
for passage in root.findall('.//passage'):
    for annotation in passage.findall('annotation'):
        # Check if type is Gene
        infons = annotation.findall('infon')
        types = [i.text for i in infons if i.attrib.get('key') == 'type']
        if 'Gene' in types:
            gene_mentions.append(annotation.find('text').text)

print(gene_mentions)

