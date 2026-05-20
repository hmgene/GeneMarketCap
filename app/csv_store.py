import os
import csv
import pandas as pd
from datetime import datetime
from app.config import CSV_PATH

HEADERS = [
    "paper_id",
    "pubmed_id",
    "title",
    "authors",
    "pub_date",
    "found_genes",
    "source_file",
    "created_at"
]


def init_csv():
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)


def add_paper(row):
    init_csv()

    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            row["paper_id"],
            row.get("pubmed_id", "unknown"),
            row.get("title", ""),
            "|".join(row.get("authors", [])),
            row.get("pub_date", "unknown"),
            "",
            row.get("source_file", ""),
            datetime.now().isoformat()
        ])


def update_genes(paper_id, genes):
    df = pd.read_csv(CSV_PATH)

    df.loc[df["paper_id"] == paper_id, "found_genes"] = "|".join(genes)

    df.to_csv(CSV_PATH, index=False)
