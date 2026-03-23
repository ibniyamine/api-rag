from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from app.rag.vectorstores import vector_store, search_supabase
from app.config import ANTHROPIC_API_KEY
from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

model = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    temperature=0,
    api_key=ANTHROPIC_API_KEY
)


def get_memory(limit=5):
    response = supabase.table("conversations") \
        .select("*") \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()

    history = ""
    for item in reversed(response.data):
        history += f"Utilisateur: {item['question']}\nAssistant: {item['answer']}\n\n"

    return history

memory = get_memory()


prompt = ChatPromptTemplate.from_template("""
Tu es un agent de support client professionnel travaillant pour une agence spécialisée dans la gestion et la vente de timbres fiscaux et et billet de footbal.
                                          
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
    docs = search_supabase(question, k=4)
    context = "\n\n".join([d.page_content for d in docs])
    chain = prompt | model
    response = chain.invoke({"context": context, "memory": memory, "question": question})
    return response.content

