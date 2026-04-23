# from supabase import create_client
# from langchain_community.vectorstores import SupabaseVectorStore
# from app.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE, SUPABASE_QUERY_NAME
import psycopg2
from langchain_core.documents import Document
from langchain_postgres.vectorstores import PGVector
from app.config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD
)
from app.rag.embeddings import embeddings

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. Construire l'URL de connexion (format SQLAlchemy)
CONNECTION_STRING = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def get_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

COLLECTION_NAME = "my_rag_documents"
def search_vectorstore(query: str, k: int = 4):
    # Plus besoin de curseur SQL manuel, on utilise l'abstraction LangChain
    docs = vector_store.similarity_search(query, k=k)
    return docs

# 3. Initialiser le VectorStore
vector_store = PGVector(
    embeddings=embeddings,
    collection_name=COLLECTION_NAME,
    connection=CONNECTION_STRING,
    use_jsonb=True, # Recommandé pour les métadonnées
)
