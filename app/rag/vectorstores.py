from supabase import create_client
from langchain_community.vectorstores import SupabaseVectorStore
from app.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE, SUPABASE_QUERY_NAME
from app.rag.embeddings import embeddings

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def search_supabase(query: str, k: int = 4):
    # 1. Embedding de la question
    query_embedding = embeddings.embed_query(query)

    # 2. Appel direct à la fonction RPC Supabase
    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_count": k
        }
    ).execute()

    # 3. Convertir en objets Document
    from langchain_core.documents import Document

    docs = []
    for item in response.data:
        docs.append(
            Document(
                page_content=item["content"],
                metadata=item["metadata"]
            )
        )

    return docs

vector_store = SupabaseVectorStore(
    client=supabase,
    table_name=SUPABASE_TABLE,
    query_name=SUPABASE_QUERY_NAME,
    embedding=embeddings
)
