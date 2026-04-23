from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
# On importe le nouveau vector_store et la nouvelle fonction de recherche
from app.rag.vectorstores import vector_store 
from app.config import ANTHROPIC_API_KEY, POSTGRES_DB # Importe tes configs PG
from app.rag.services import compute_cost
from psycopg2.extras import RealDictCursor
from app.rag.vectorstores import get_connection

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

model = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    temperature=0,
    api_key=ANTHROPIC_API_KEY
)


def get_memory(limit=5):
    # Utilise ta fonction get_connection() définie précédemment
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT question, answer 
        FROM conversations 
        ORDER BY created_at DESC 
        LIMIT %s
    """, (limit,))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()

    history = ""
    for item in reversed(rows):
        history += f"Utilisateur: {item['question']}\nAssistant: {item['answer']}\n\n"
    return history

memory = get_memory()


prompt = ChatPromptTemplate.from_template("""
Tu es un agent de support client professionnel travaillant pour une agence spécialisée dans la gestion et la vente de timbres fiscaux
                                          
Règles importantes :
- Utilise la mémoire pour comprendre le contexte.
- Réponds de manière naturelle et continue, comme dans une vraie conversation.
- Ne répète pas les informations déjà données précédemment.
- Si la mémoire contient déjà une réponse similaire, fais référence à celle-ci plutôt que de répéter.
Voici les informations trouvées :
{context}
Voici l'historique récent des conversations avec les clients :
{memory}

Question : {question}

### Style de réponse attendu :

* Réponse courte
* Structure claire
* Ton neutre
* Pas d’introduction inutile
* Pas de conclusion commerciale
""")

def rag_answer(question):
    # 1. Utilise la recherche PGVector (via LangChain c'est plus simple)
    docs = vector_store.similarity_search(question, k=4)
    context = "\n\n".join([d.page_content for d in docs])
    
    # 2. Récupérer la mémoire via SQL
    memory = get_memory()
    
    chain = prompt | model
    response = chain.invoke({"context": context, "memory": memory, "question": question})

    # 3. Statistiques et Coûts
    tokens_in = response.usage_metadata["input_tokens"]
    tokens_out = response.usage_metadata["output_tokens"]
    cost = compute_cost("claude-haiku-4-5-20251001", tokens_in, tokens_out)

    # 4. Sauvegarde des stats dans PostgreSQL (Docker)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO stats (model, input_tokens, output_tokens, total_tokens, cost)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        "claude-haiku-4-5-20251001", 
        tokens_in, 
        tokens_out, 
        tokens_in + tokens_out, 
        cost
    ))
    conn.commit()
    cur.close()
    conn.close()

    return response.content

