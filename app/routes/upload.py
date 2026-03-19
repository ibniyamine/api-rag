from fastapi import APIRouter, UploadFile, File
import shutil
from app.rag.loader import load_pdf, load_excel
from app.rag.vectorstores import vector_store

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    path = f"uploads/{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.endswith(".pdf"):
        docs = load_pdf(path)
    elif file.filename.endswith(".xlsx"):
        docs = load_excel(path)
    else:
        return {"error": "Format non supporté"}

    vector_store.add_documents(docs)
    return {"status": "Document indexé"}
