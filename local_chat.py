"""
Chat local que funciona sem API externa
Para usar quando a quota da OpenAI acabar
Execute: poetry run python local_chat.py
"""

import random
import uvicorn
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List

app = FastAPI(
    title="Chat Local - Assistente de Viagem",
    description="Versão local que funciona sem APIs externas",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    model_used: str

# Base de conhecimento local sobre viagens
DESTINOS_BRASIL = {
    "são domingos de goiás": {
        "descricao": "Pequena cidade em Goiás conhecida pela tranquilidade e natureza",
        "atrações": ["Cachoeiras", "Trilhas ecológicas", "Turismo rural", "Pesca esportiva"],
        "dicas": ["Leve repelente", "Use roupas confortáveis", "Aproveite a gastronomia local", "Melhor época: maio a setembro"],
        "hospedagem": ["Pousadas rurais", "Fazendas", "Camping"],
        "gastronomia": ["Comida caseira", "Peixe fresco", "Doces regionais"]
    },
    "goiás": {
        "descricao": "Estado no centro-oeste brasileiro com rica cultura e natureza",
        "atrações": ["Chapada dos Veadeiros", "Cidade de Goiás", "Caldas Novas", "Pirenópolis"],
        "dicas": ["Melhor época: maio a setembro", "Leve protetor solar", "Prove o pequi", "Cuidado com o sol forte"],
        "hospedagem": ["Hotéis fazenda", "Pousadas", "Resorts em Caldas Novas"],
        "gastronomia": ["Pequi", "Pacu", "Guariroba", "Doce de leite"]
    },
    "santa catarina": {
        "descricao": "Estado do sul do Brasil famoso pelas praias e montanhas",
        "atrações": ["Florianópolis", "Blumenau", "Balneário Camboriú", "São Joaquim", "Urubici"],
        "dicas": ["Verão: praias lotadas", "Inverno: serra nevada", "Oktoberfest em outubro", "Trânsito intenso no verão"],
        "hospedagem": ["Hotéis de praia", "Pousadas na serra", "Resorts", "Airbnb"],
        "gastronomia": ["Sequência de camarão", "Mariscos", "Cerveja artesanal", "Cucas alemãs"]
    },
    "florianópolis": {
        "descricao": "Capital de Santa Catarina, famosa pelas 42 praias",
        "atrações": ["Lagoa da Conceição", "Praia do Campeche", "Centro histórico", "Ponte Hercílio Luz"],
        "dicas": ["Verão muito movimentado", "Alugue carro", "Prove a sequência de camarão", "Cuidado com o trânsito"],
        "hospedagem": ["Hotéis no centro", "Pousadas na Lagoa", "Resorts na praia"],
        "gastronomia": ["Ostras", "Camarão", "Tainha", "Cachaça artesanal"]
    },
    "brasil": {
        "descricao": "País continental com diversidade incrível de destinos",
        "atrações": ["Amazônia", "Pantanal", "Nordeste", "Sul", "Sudeste", "Centro-Oeste"],
        "dicas": ["Cada região tem clima diferente", "Documentos sempre em dia", "Vacinas em dia para algumas regiões"],
        "hospedagem": ["De hostels a resorts de luxo"],
        "gastronomia": ["Cada região tem pratos típicos únicos"]
    }
}

RESPOSTAS_CONTEXTUAIS = {
    "saudacao": [
        "Olá! 🌍 Seja bem-vindo ao seu assistente de viagem! Estou aqui para te ajudar a planejar uma viagem incrível.",
        "Oi! 👋 Que bom te ver aqui! Sou seu assistente de viagem e vou te ajudar a criar roteiros incríveis.",
        "Olá, viajante! ✈️ Pronto para descobrir destinos incríveis? Me conte: onde você gostaria de ir?"
    ],
    "despedida": [
        "Foi um prazer te ajudar! 🌟 Boa viagem e que seja uma experiência inesquecível!",
        "Até logo! 👋 Espero que sua viagem seja incrível! Volte sempre que precisar de dicas!",
        "Tchau! ✨ Que sua aventura seja repleta de momentos especiais!"
    ],
    "pessoas": [
        "Perfeito! 👥 Viajar acompanhado é sempre mais especial. Agora me conte:",
        "Que legal! 🤝 Grupo bom para viajar. Vamos planejar algo incrível para vocês:",
        "Ótimo! 👨‍👩‍👧‍👦 Vou dar dicas pensando no grupo todo. Me ajude com mais detalhes:"
    ],
    "orcamento": [
        "💰 Entendi! Com essas informações de orçamento posso sugerir opções mais direcionadas.",
        "💵 Ótimo! Vou adaptar as sugestões ao seu orçamento. Algumas dicas para economizar:",
        "💳 Perfeito! Com esse orçamento dá para fazer uma viagem bem legal."
    ],
    "quando": [
        "📅 A época da viagem faz toda diferença na experiência!",
        "🗓️ Boa pergunta! A temporada influencia muito no roteiro e nos preços.",
        "⏰ Timing perfeito! Vou te dar dicas específicas para essa época."
    ],
    "duvidas": [
        "🤔 Que dúvida interessante! Vou te ajudar com isso.",
        "❓ Boa pergunta! Deixa eu te explicar melhor sobre isso.",
        "💭 Entendo sua dúvida. Vou esclarecer isso para você."
    ]
}

DICAS_GERAIS = [
    "💡 Dica: Reserve hospedagens com antecedência para melhores preços!",
    "🎒 Lembre-se: menos bagagem = mais liberdade para explorar!",
    "📱 Baixe apps offline de mapas antes de viajar!",
    "💊 Sempre leve uma farmacinha básica na viagem!",
    "📋 Faça uma lista do que levar para não esquecer nada importante!",
    "🔌 Não esqueça carregadores e adaptadores de tomada!",
    "💧 Mantenha-se sempre hidratado durante a viagem!",
    "📸 Reserve um tempinho para simplesmente curtir, sem fotos!"
]

# Armazenar conversas
conversas: Dict[str, Dict] = {}

def detectar_contexto(mensagem: str) -> str:
    """Detectar o contexto da mensagem"""
    mensagem_lower = mensagem.lower()
    
    # Saudações
    if any(palavra in mensagem_lower for palavra in ["olá", "oi", "bom dia", "boa tarde", "boa noite", "hello"]):
        return "saudacao"
    
    # Despedidas
    if any(palavra in mensagem_lower for palavra in ["tchau", "até logo", "obrigado", "valeu", "bye"]):
        return "despedida"
    
    # Pessoas/grupo
    if any(palavra in mensagem_lower for palavra in ["pessoas", "pessoa", "gente", "nós", "casal", "família", "amigos"]):
        return "pessoas"
    
    # Orçamento
    if any(palavra in mensagem_lower for palavra in ["real", "reais", "dinheiro", "orçamento", "gasto", "custo", "preço"]):
        return "orcamento"
    
    # Tempo/quando
    if any(palavra in mensagem_lower for palavra in ["quando", "época", "mês", "temporada", "data", "período"]):
        return "quando"
    
    # Dúvidas
    if any(palavra in mensagem_lower for palavra in ["como", "onde", "qual", "quanto", "porque", "dúvida"]):
        return "duvidas"
    
    return "geral"

def gerar_resposta_local(mensagem: str, session_id: str) -> str:
    """Gerar resposta usando lógica local"""
    mensagem_lower = mensagem.lower()
    
    # Inicializar conversa se não existir
    if session_id not in conversas:
        conversas[session_id] = {
            "mensagens": [],
            "contexto": {},
            "destino_atual": None,
            "pessoas": None,
            "orcamento": None
        }
    
    conversa = conversas[session_id]
    
    # Adicionar mensagem do usuário
    conversa["mensagens"].append({"role": "user", "content": mensagem})
    
    # Detectar contexto
    contexto = detectar_contexto(mensagem)
    
    # Primeira mensagem - saudação
    if len(conversa["mensagens"]) == 1:
        resposta = random.choice(RESPOSTAS_CONTEXTUAIS["saudacao"])
        resposta += "\n\nPara começar, me conte: qual é o seu destino dos sonhos? E quantas pessoas vão viajar com você?"
    
    # Verificar se mencionou algum destino conhecido
    elif any(dest in mensagem_lower for dest in DESTINOS_BRASIL.keys()):
        for destino, info in DESTINOS_BRASIL.items():
            if destino in mensagem_lower:
                conversa["destino_atual"] = destino
                resposta = f"🎯 Excelente escolha! {info['descricao']}!\n\n"
                resposta += f"🏞️ **Principais atrações:**\n• {chr(10) + '• '.join(info['atrações'])}\n\n"
                resposta += f"🏨 **Opções de hospedagem:**\n• {chr(10) + '• '.join(info['hospedagem'])}\n\n"
                resposta += f"🍽️ **Gastronomia local:**\n• {chr(10) + '• '.join(info['gastronomia'])}\n\n"
                resposta += f"💡 **Dicas importantes:**\n• {chr(10) + '• '.join(info['dicas'])}\n\n"
                resposta += "Agora me conte: quantas pessoas vão viajar? E qual é a duração pretendida da viagem?"
                break
    
    # Respostas baseadas no contexto
    elif contexto in RESPOSTAS_CONTEXTUAIS:
        resposta_base = random.choice(RESPOSTAS_CONTEXTUAIS[contexto])
        
        if contexto == "pessoas":
            # Extrair número de pessoas
            import re
            numeros = re.findall(r'\d+', mensagem)
            if numeros:
                conversa["pessoas"] = int(numeros[0])
                resposta = f"{resposta_base}\n"
                resposta += f"• Qual é o orçamento aproximado por pessoa?\n"
                resposta += f"• Vocês preferem hospedagem simples ou mais confortável?\n"
                resposta += f"• Gostam mais de aventura ou relaxamento?\n"
                resposta += f"• Alguma restrição alimentar ou de mobilidade?"
            else:
                resposta = resposta_base + " Quantas pessoas exatamente vão viajar?"
        
        elif contexto == "orcamento":
            resposta = f"{resposta_base}\n\n"
            resposta += "**Dicas para economizar:**\n"
            resposta += "• 📅 Reserve com antecedência\n"
            resposta += "• 📉 Considere viajar na baixa temporada\n"
            resposta += "• 🏠 Procure hospedagens locais ou Airbnb\n"
            resposta += "• 🍽️ Experimente a gastronomia de rua\n"
            resposta += "• 🚌 Use transporte público quando possível\n\n"
            resposta += "Quer que eu monte um roteiro detalhado considerando seu orçamento?"
        
        elif contexto == "quando":
            destino = conversa.get("destino_atual")
            if destino and destino in DESTINOS_BRASIL:
                info = DESTINOS_BRASIL[destino]
                resposta = f"{resposta_base}\n\n"
                resposta += f"Para **{destino.title()}**:\n"
                # Adicionar dicas específicas de época se disponível
                dicas_epoca = [dica for dica in info['dicas'] if any(palavra in dica.lower() for palavra in ['época', 'temporada', 'maio', 'setembro', 'verão', 'inverno'])]
                if dicas_epoca:
                    resposta += f"• {chr(10) + '• '.join(dicas_epoca)}\n\n"
                resposta += "Você já tem uma data específica em mente?"
            else:
                resposta = resposta_base + "\n\nMe conte qual é o destino para eu dar dicas mais específicas de época!"
        
        elif contexto == "despedida":
            resposta = random.choice(RESPOSTAS_CONTEXTUAIS["despedida"])
        
        else:
            resposta = resposta_base
    
    # Resposta genérica com dica
    else:
        respostas_genericas = [
            "Interessante! Me conte mais detalhes sobre o que você tem em mente.",
            "Entendi! Vou te ajudar com isso. Pode me dar mais informações?",
            "Que legal! Vamos planejar algo incrível juntos.",
            "Perfeito! Adoro ajudar com planejamentos de viagem.",
            "Ótima ideia! Me conte mais sobre suas preferências."
        ]
        resposta = random.choice(respostas_genericas)
        resposta += f"\n\n{random.choice(DICAS_GERAIS)}"
    
    # Adicionar resposta do assistente
    conversa["mensagens"].append({"role": "assistant", "content": resposta})
    
    return resposta

@app.get("/")
async def root():
    return {
        "message": "🏠 Chat Local funcionando!",
        "status": "success",
        "mode": "local",
        "version": "1.0.0",
        "features": ["Offline", "Sem APIs externas", "Conhecimento local do Brasil"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "chat-local",
        "mode": "offline",
        "api_required": False,
        "openai_configured": False,
        "local_ready": True
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_local(request: ChatRequest):
    """Chat local sem APIs externas"""
    try:
        resposta = gerar_resposta_local(request.message, request.session_id)
        
        return ChatResponse(
            response=resposta,
            session_id=request.session_id,
            model_used="local-assistant"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no chat local: {str(e)}")

@app.get("/sessions")
async def list_sessions():
    """Listar sessões ativas"""
    return {
        "active_sessions": list(conversas.keys()),
        "total_sessions": len(conversas)
    }

@app.get("/sessions/{session_id}/history")
async def get_history(session_id: str):
    """Obter histórico da sessão"""
    if session_id in conversas:
        return {
            "session_id": session_id,
            "messages": conversas[session_id]["mensagens"],
            "total_messages": len(conversas[session_id]["mensagens"]),
            "context": conversas[session_id]["contexto"]
        }
    return {"session_id": session_id, "messages": [], "total_messages": 0}

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Limpar histórico de uma sessão"""
    if session_id in conversas:
        del conversas[session_id]
        return {"message": f"Sessão {session_id} limpa com sucesso"}
    else:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

@app.delete("/sessions")
async def clear_all_sessions():
    """Limpar todas as sessões"""
    conversas.clear()
    return {"message": "Todas as sessões foram limpas"}

@app.get("/destinations")
async def list_destinations():
    """Listar destinos disponíveis no conhecimento local"""
    destinos = []
    for nome, info in DESTINOS_BRASIL.items():
        destinos.append({
            "nome": nome.title(),
            "descricao": info["descricao"],
            "total_atracoes": len(info["atrações"])
        })
    
    return {
        "total_destinations": len(destinos),
        "destinations": destinos
    }

if __name__ == "__main__":
    print("🏠 Iniciando Chat Local - Assistente de Viagem")
    print("🌐 Será executado em: http://localhost:8001")
    print("📚 Base de conhecimento: Brasil")
    print("🔧 Modo: Offline (sem APIs externas)")
    
    uvicorn.run(
        "local_chat:app", 
        host="127.0.0.1", 
        port=8001, 
        reload=True,
        log_level="info"
    )