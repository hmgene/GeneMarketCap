from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

import os

from app.services.ingest_service import ingest_pdf

router = APIRouter()


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    pubmed_id: str = None,
    title: str = None
):

    os.makedirs("./data/pdfs", exist_ok=True)

    path = f"./data/pdfs/{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    return ingest_pdf(
        path,
        pubmed_id,
        title
    )
