import os
import shutil

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from app.ingest import ingest_pdf
from app.rag import ask_question

from app.config import PDF_PATH


app = FastAPI()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
async def root():

    return {
        "message": "Research Agent API running"
    }


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):

    save_path = os.path.join(PDF_PATH, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_pdf(save_path)

    return result


@app.post("/ask")
async def ask(req: QuestionRequest):

    answer = ask_question(req.question)

    return {
        "question": req.question,
        "answer": answer
    }
