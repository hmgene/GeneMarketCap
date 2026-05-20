from fastapi import FastAPI, UploadFile, File
import os

from app.ingest import ingest_pdf
from app.rag import ask_question

app = FastAPI()


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    os.makedirs("./data/pdfs", exist_ok=True)

    path = f"./data/pdfs/{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    result = ingest_pdf(path)

    return result


@app.post("/ask")
async def ask(payload: dict):

    return ask_question(
        payload["question"],
        payload.get("paper_id")
    )
