from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.pipeline import rag_answer
from app.rag.vectorstores import get_connection # Importe ta fonction de connexion
from psycopg2.extras import RealDictCursor

router = APIRouter()

class Query(BaseModel):
    question: str

@router.post("/chat")
def chat(query: Query):
    # 1) Obtenir la réponse du RAG
    answer = rag_answer(query.question)

    # 2) Sauvegarder dans Postgres (Docker)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO conversations (question, answer) VALUES (%s, %s)",
        (query.question, answer)
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"response": answer}

@router.get("/history")
def history():
    conn = get_connection()
    # RealDictCursor permet de retourner des dictionnaires (comme Supabase)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM conversations ORDER BY created_at DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

@router.get("/stats")
def get_stats():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM stats ORDER BY created_at DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data
