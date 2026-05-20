import csv
import os

from app.core.config import META_DIR

CSV_PATH = f"{META_DIR}/papers.csv"

FIELDS = [
    "paper_id",
    "pubmed_id",
    "title",
    "source_file"
]

os.makedirs(META_DIR, exist_ok=True)


def add_paper(row):

    exists = os.path.exists(CSV_PATH)

    with open(CSV_PATH, "a", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=FIELDS
        )

        if not exists:
            writer.writeheader()

        writer.writerow(row)
