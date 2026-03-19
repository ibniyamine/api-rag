from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from app.rag.vectorstores import vector_store, search_supabase
from app.config import ANTHROPIC_API_KEY

model = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    temperature=0,
    api_key=ANTHROPIC_API_KEY
)

prompt = ChatPromptTemplate.from_template("""
Tu es un assistant basé sur des documents.
Voici les informations trouvées :

{context}

Question : {question}

Réponds uniquement avec les informations du contexte.
""")

def rag_answer(question):
    docs = search_supabase(question, k=4)
    context = "\n\n".join([d.page_content for d in docs])
    chain = prompt | model
    response = chain.invoke({"context": context, "question": question})
    return response.content

