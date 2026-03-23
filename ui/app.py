import streamlit as st
import requests
import json
from io import BytesIO
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Configuration de la page
st.set_page_config(
    page_title="RAG System Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour le design moderne
st.markdown("""
<style>
    /* Dégradé de fond */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Style des cartes */
    .card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Titre principal */
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Bouton flottant du chatbot */
    .chat-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(45deg, #667eea, #764ba2);
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        transition: all 0.3s ease;
    }
    
    .chat-button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
    }
    
    /* Fenêtre de chat */
    .chat-window {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        z-index: 999;
        display: none;
        flex-direction: column;
        overflow: hidden;
    }
    
    .chat-header {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 15px;
        font-weight: bold;
        border-radius: 15px 15px 0 0;
    }
    
    .chat-messages {
        flex: 1;
        padding: 15px;
        overflow-y: auto;
        background: #f8f9fa;
    }
    
    .chat-input {
        padding: 15px;
        border-top: 1px solid #e0e0e0;
        background: white;
    }
    
    /* Style des boutons */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Style des inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Messages de chat */
    .user-message {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 5px 15px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
        text-align: right;
    }
    
    .bot-message {
        background: #f1f3f4;
        color: #333;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 5px;
        margin: 10px 0;
        max-width: 80%;
    }
    
    /* Cache les éléments par défaut de Streamlit */
    .stDeployButton {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# État de la session
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Fonctions utilitaires
def api_request(method: str, endpoint: str, data: Dict[str, Any] = None, files: Dict[str, Any] = None) -> Dict[str, Any]:
    """Effectue une requête à l'API"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            return {"error": f"Méthode {method} non supportée"}
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Erreur {response.status_code}: {response.text}"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"Erreur de connexion: {str(e)}"}

# Interface principale
st.markdown('<h1 class="main-title">🤖 RAG System Dashboard</h1>', unsafe_allow_html=True)

# Colonnes pour les différentes fonctionnalités
col1, col2 = st.columns(2)

with col1:
    # Carte Chat
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💬 Test Chat Endpoint")
        
        question = st.text_area("Question:", placeholder="Entrez votre question ici...", height=100)
        
        if st.button("Envoyer la question"):
            if question:
                with st.spinner("Envoi en cours..."):
                    result = api_request("POST", "/chat", {"question": question})
                    
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.success("✅ Réponse reçue!")
                    st.markdown(f"**Réponse:** {result.get('response', 'Aucune réponse')}")
            else:
                st.warning("⚠️ Veuillez entrer une question")
        
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Carte Upload
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📁 Test Upload Endpoint")
        
        uploaded_file = st.file_uploader("Choisissez un fichier", type=['pdf', 'xlsx'])
        
        if uploaded_file:
            st.info(f"Fichier sélectionné: {uploaded_file.name}")
            
            if st.button("Uploader le fichier"):
                with st.spinner("Upload en cours..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    result = api_request("POST", "/upload", files=files)
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.success("✅ Fichier uploadé avec succès!")
                    st.json(result)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Carte History
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📜 Test History Endpoint")
    
    col_hist1, col_hist2 = st.columns([1, 1])
    
    with col_hist1:
        if st.button("Récupérer l'historique"):
            with st.spinner("Récupération en cours..."):
                result = api_request("GET", "/history")
            
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.success("✅ Historique récupéré!")
                st.session_state.history_data = result
    
    with col_hist2:
        if st.button("Vider l'historique"):
            st.session_state.history_data = None
            st.rerun()
    
    if 'history_data' in st.session_state and st.session_state.history_data:
        st.markdown("**Historique des conversations:**")
        for i, conv in enumerate(st.session_state.history_data[:5]):  # Limite à 5 pour l'affichage
            with st.expander(f"Conversation {i+1} - {conv.get('created_at', 'N/A')}"):
                st.markdown(f"**Question:** {conv.get('question', 'N/A')}")
                st.markdown(f"**Réponse:** {conv.get('answer', 'N/A')}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Carte API Tester
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔧 API Endpoint Tester")
    
    col_api1, col_api2, col_api3 = st.columns([1, 1, 1])
    
    with col_api1:
        method = st.selectbox("Méthode HTTP:", ["GET", "POST", "PUT", "DELETE"])
    
    with col_api2:
        endpoint = st.text_input("Endpoint:", placeholder="/chat")
    
    with col_api3:
        if st.button("Tester l'endpoint"):
            if endpoint:
                # Préparer les données selon la méthode
                data = None
                if method in ["POST", "PUT"]:
                    try:
                        data = json.loads(st.text_area("JSON Data:", "{}", height=100))
                    except:
                        data = {}
                
                with st.spinner("Test en cours..."):
                    result = api_request(method, endpoint, data)
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.success("✅ Requête réussie!")
                    st.json(result)
            else:
                st.warning("⚠️ Veuillez entrer un endpoint")
    
    if method in ["POST", "PUT"]:
        json_data = st.text_area("JSON Data (optionnel):", "{}", height=100)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Bouton flottant et fenêtre de chat
st.markdown(f"""
<button class="chat-button" onclick="toggleChat()">💬</button>

<div class="chat-window" id="chatWindow">
    <div class="chat-header">
        Chatbot RAG
        <button onclick="toggleChat()" style="float: right; background: none; border: none; color: white; font-size: 20px; cursor: pointer;">×</button>
    </div>
    <div class="chat-messages" id="chatMessages">
        {''.join([f'<div class="bot-message">{msg}</div>' if i%2==0 else f'<div class="user-message">{msg}</div>' for i, msg in enumerate(st.session_state.chat_messages)])}
    </div>
    <div class="chat-input">
        <input type="text" id="chatInput" placeholder="Tapez votre message..." style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;" onkeypress="if(event.key=='Enter') sendMessage()">
        <button onclick="sendMessage()" style="margin-top: 5px; width: 100%; padding: 8px; background: linear-gradient(45deg, #667eea, #764ba2); color: white; border: none; border-radius: 5px; cursor: pointer;">Envoyer</button>
    </div>
</div>

<script>
function toggleChat() {{
    const chatWindow = document.getElementById('chatWindow');
    const isOpen = chatWindow.style.display === 'flex';
    chatWindow.style.display = isOpen ? 'none' : 'flex';
}}

function sendMessage() {{
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (message) {{
        // Ajouter le message à l'interface
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.innerHTML += `<div class="user-message">${{message}}</div>`;
        
        // Envoyer à l'API
        fetch('{API_BASE_URL}/chat', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify({{question: message}})
        }})
        .then(response => response.json())
        .then(data => {{
            messagesDiv.innerHTML += `<div class="bot-message">${{data.response || 'Erreur'}}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }})
        .catch(error => {{
            messagesDiv.innerHTML += `<div class="bot-message">Erreur: ${{error.message}}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }});
        
        input.value = '';
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }}
}}

// Auto-scroll pour les messages
document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
</script>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: white; margin-top: 2rem;">'
    '<p>🚀 RAG System Dashboard | Connecté à ' + API_BASE_URL + '</p>'
    '</div>', 
    unsafe_allow_html=True
)
