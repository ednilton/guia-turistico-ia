import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Carregar variáveis de ambiente
load_dotenv()

# Verificar configuração na inicialização
print("🔧 Inicializando aplicação...")
openai_key = os.getenv("OPENAI_API_KEY")
print(f"🔍 OpenAI key configured: {bool(openai_key)}")
if openai_key:
    print(f"🔍 OpenAI key prefix: {openai_key[:10]}...")
else:
    print("⚠️ WARNING: OPENAI_API_KEY not found in environment")

# Importações do LangChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Criar instância do FastAPI
app = FastAPI(
    title="Chat Inteligente API",
    description="API para o projeto de chat inteligente com LangChain",
    version="1.0.0"
)

# Modelos Pydantic para as requisições
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    model_used: str

# Configuração do LangChain
template = """
Você é um assistente de Viagem que ajuda os usuários a planejar suas viagens, 
dando sugestões de destinos, roteiros e dicas práticas. A primeira coisa que 
você deve fazer é perguntar ao usuário qual é o destino da viagem e com 
quantas pessoas ele está viajando.

Histórico da conversa: {history}

Entrada do usuário: {input}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", template),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# Inicializar o modelo
try:
    llm = ChatOpenAI(
        temperature=0.7, 
        model="gpt-3.5-turbo",  # Modelo mais barato
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    print("✅ LLM initialized successfully")
except Exception as e:
    print(f"❌ Error initializing LLM: {e}")
    llm = None

# Criar a chain
chain = prompt | llm

# Store para histórico de conversas
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Obtém o histórico de mensagens para uma sessão específica."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Chain com histórico
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# Endpoints da API
@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "🚀 Chat Inteligente API está funcionando!",
        "status": "success",
        "version": "1.0.0",
        "features": ["FastAPI", "LangChain", "OpenAI", "Chat History"]
    }

@app.get("/health")
async def health_check():
    """Verificar saúde da API"""
    # Verificar se a chave da OpenAI está configurada
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    
    return {
        "status": "healthy",
        "service": "chat-inteligente",
        "openai_configured": openai_configured,
        "langchain_ready": True
    }

@app.get("/info")
async def info():
    """Informações sobre a API"""
    return {
        "name": "Chat Inteligente",
        "description": "API para chat com IA usando LangChain",
        "model": "gpt-4o-mini",
        "features": [
            "Assistente de Viagem",
            "Histórico de Conversas",
            "Múltiplas Sessões"
        ],
        "endpoints": {
            "root": "/",
            "health": "/health",
            "chat": "/chat",
            "sessions": "/sessions",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint principal de chat"""
    try:
        # Debug: Verificar variáveis de ambiente
        openai_key = os.getenv("OPENAI_API_KEY")
        print(f"🔍 DEBUG: OpenAI key configured: {bool(openai_key)}")
        if openai_key:
            print(f"🔍 DEBUG: OpenAI key starts with: {openai_key[:10]}...")
        
        # Verificar se a chave da OpenAI está configurada
        if not openai_key:
            print("❌ ERROR: OPENAI_API_KEY não encontrada")
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY não configurada. Adicione no arquivo .env"
            )
        
        print(f"🔍 DEBUG: Processing message: {request.message[:50]}...")
        print(f"🔍 DEBUG: Session ID: {request.session_id}")
        
        # Processar a mensagem
        resposta = chain_with_history.invoke(
            {'input': request.message},
            config={'configurable': {'session_id': request.session_id}}
        )
        
        print(f"✅ DEBUG: Response generated successfully")
        
        return ChatResponse(
            response=resposta.content,
            session_id=request.session_id,
            model_used="gpt-3.5-turbo"
        )
        
    except Exception as e:
        print(f"❌ ERROR in chat endpoint: {str(e)}")
        print(f"❌ ERROR type: {type(e).__name__}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")

@app.get("/sessions")
async def list_sessions():
    """Listar sessões ativas"""
    return {
        "active_sessions": list(store.keys()),
        "total_sessions": len(store)
    }

@app.get("/sessions/{session_id}/history")
async def get_session_history_endpoint(session_id: str):
    """Obter histórico de uma sessão específica"""
    if session_id not in store:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    history = store[session_id]
    messages = []
    
    for message in history.messages:
        messages.append({
            "type": message.__class__.__name__,
            "content": message.content
        })
    
    return {
        "session_id": session_id,
        "messages": messages,
        "total_messages": len(messages)
    }

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Limpar histórico de uma sessão"""
    if session_id in store:
        del store[session_id]
        return {"message": f"Sessão {session_id} limpa com sucesso"}
    else:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

@app.delete("/sessions")
async def clear_all_sessions():
    """Limpar todas as sessões"""
    store.clear()
    return {"message": "Todas as sessões foram limpas"}

# Função para executar o servidor
def run_server():
    """Executar o servidor FastAPI"""
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_server()