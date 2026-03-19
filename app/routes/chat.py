from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.pipeline import rag_answer, supabase


router = APIRouter()



class Query(BaseModel):
    question: str


@router.post("/chat")
def chat(query: Query):
    # 1) Obtenir la réponse du RAG
    answer = rag_answer(query.question)

    # 2) Sauvegarder question + réponse dans Supabase
    supabase.table("conversations").insert({
        "question": query.question,
        "answer": answer
    }).execute()

    # 3) Retourner la réponse
    return {"response": answer}


@router.get("/history")
def history():
    response = supabase.table("conversations") \
        .select("*") \
        .order("created_at", desc=True) \
        .execute()

    return response.data

