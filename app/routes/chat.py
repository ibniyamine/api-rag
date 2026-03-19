from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.pipeline import rag_answer

router = APIRouter()

class Query(BaseModel):
    question: str

@router.post("/chat")
def chat(query: Query):
    answer = rag_answer(query.question)
    return {"response": answer}
