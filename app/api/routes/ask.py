from fastapi import APIRouter

from app.services.rag_service import ask_question

router = APIRouter()


@router.post("/ask")
async def ask(payload: dict):

    answer = ask_question(
        payload["question"],
        payload.get("pubmed_id")
    )

    return {
        "answer": answer
    }
