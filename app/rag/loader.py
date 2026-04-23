from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
import pandas as pd

def load_pdf(path):
    loader = PyPDFLoader(path)
    return loader.load()

def load_excel(path):
    df = pd.read_excel(path, engine='openpyxl')
    docs = []
    for _, row in df.iterrows():
        content = " ".join([str(v) for v in row.values])
        # Ajouter le nom du fichier en métadonnée par exemple
        docs.append(Document(page_content=content, metadata={"source": path}))
    return docs

