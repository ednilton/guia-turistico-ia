# 🤖 guia-turistico-ia

Uma API moderna para chat com IA focada em planejamento de viagens, construída com **FastAPI** + **LangChain** + **OpenAI**, com fallback local para funcionamento offline.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Funcionalidades

- 🌐 **API REST completa** com FastAPI
- 🧠 **Chat inteligente** com LangChain + OpenAI
- 💾 **Histórico de conversas** persistente
- 🏠 **Modo local** sem APIs externas
- 🔄 **Detecção automática** de APIs disponíveis
- 📱 **Cliente de terminal** interativo
- 📚 **Base de conhecimento** sobre destinos brasileiros
- 🔧 **Documentação automática** (Swagger/ReDoc)

## 🚀 Quick Start

### Pré-requisitos

- Python 3.9+
- Poetry (gerenciador de dependências)
- Chave API da OpenAI (opcional)

### Instalação

```bash
# 1. Clonar o repositório
git clone <url-do-repo>
cd chat-inteligente

# 2. Instalar dependências
poetry install

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com sua chave OpenAI (opcional)

# 4. Executar a API
poetry run uvicorn main:app --reload
```

### Uso Rápido

```bash
# Chat interativo inteligente (recomendado)
poetry run python smart_client.py

# Ou chat simples
poetry run python chat.py

# Testar via curl
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Quero viajar para Florianópolis", "session_id": "test"}'
```

## 🏗️ Arquitetura

```
chat-inteligente/
├── 📁 app/                    # Módulos da aplicação
│   ├── config.py             # Configurações centralizadas
│   ├── models.py             # Modelos Pydantic
│   └── services.py           # Serviços de IA
├── 📁 routers/               # Endpoints organizados
├── 📁 tests/                 # Testes automatizados
├── 📄 main.py                # FastAPI principal (OpenAI)
├── 📄 local_chat.py          # Chat local (offline)
├── 📄 client.py              # Cliente de terminal
├── 📄 smart_client.py        # Cliente inteligente
├── 📄 chat.py                # Cliente simples
├── 📄 pyproject.toml         # Dependências Poetry
└── 📄 .env                   # Variáveis de ambiente
```

## 🌐 APIs Disponíveis

### API Principal (OpenAI) - Porta 8000

- **Endpoint:** `http://localhost:8000`
- **Modelo:** GPT-3.5-turbo / GPT-4
- **Recursos:** Chat avançado, contexto global, múltiplos idiomas

### API Local (Offline) - Porta 8001

- **Endpoint:** `http://localhost:8001`
- **Modelo:** Lógica local personalizada
- **Recursos:** Conhecimento sobre Brasil, funciona sem internet

## 📋 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Status da API |
| `GET` | `/health` | Verificação de saúde |
| `GET` | `/docs` | Documentação interativa |
| `POST` | `/chat` | Enviar mensagem de chat |
| `GET` | `/sessions` | Listar sessões ativas |
| `GET` | `/sessions/{id}/history` | Histórico da sessão |
| `DELETE` | `/sessions/{id}` | Limpar sessão |

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```bash
# API Keys
OPENAI_API_KEY=sk-sua-chave-openai-aqui
ANTHROPIC_API_KEY=sk-ant-sua-chave-anthropic-aqui

# Configurações da aplicação
APP_NAME="Chat Inteligente"
DEBUG=True
HOST=127.0.0.1
PORT=8000

# Configurações de chat
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=1000
```

### Modelos Suportados

**OpenAI:**
- `gpt-3.5-turbo` (recomendado)
- `gpt-4`
- `gpt-4-turbo-preview`

**Local:**
- `local-assistant` (conhecimento sobre Brasil)

## 💬 Clientes Disponíveis

### 1. Cliente Inteligente (Recomendado)

```bash
poetry run python smart_client.py
```

**Recursos:**
- ✅ Detecção automática de APIs
- ✅ Fallback OpenAI → Local
- ✅ Comandos especiais (/help, /history)
- ✅ Tratamento de erros

### 2. Cliente Simples

```bash
poetry run python chat.py
```

**Recursos:**
- ✅ Interface minimalista
- ✅ Chat direto
- ✅ Ideal para testes rápidos

### 3. Cliente Completo

```bash
poetry run python client.py
```

**Recursos:**
- ✅ Comandos avançados
- ✅ Gerenciamento de sessões
- ✅ Histórico detalhado

## 🧪 Testes

```bash
# Executar todos os testes
poetry run pytest

# Testes com cobertura
poetry run pytest --cov=.

# Testar configuração
poetry run python test_setup.py
```

## 📚 Exemplos de Uso

### Chat sobre Viagem

```python
import requests

response = requests.post("http://localhost:8000/chat", json={
    "message": "Quero viajar para São Domingos de Goiás com 2 pessoas",
    "session_id": "viagem_goias"
})

print(response.json()["response"])
```

### Obter Histórico

```python
response = requests.get("http://localhost:8000/sessions/viagem_goias/history")
print(response.json())
```

### Cliente Python

```python
from smart_client import SmartChatClient

client = SmartChatClient()
response = client.send_message("Olá! Quero planejar uma viagem")
print(response)
```

## 🚨 Resolução de Problemas

### Erro 429 - Quota Excedida (OpenAI)

```bash
# Usar chat local automaticamente
poetry run python smart_client.py

# Ou iniciar apenas o local
poetry run python local_chat.py
```

### APIs não encontradas

```bash
# Verificar status
poetry run python smart_client.py status

# Verificar saúde
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Dependências

```bash
# Reinstalar dependências
poetry install --sync

# Verificar versões
poetry show
```

## 🛠️ Desenvolvimento

### Estrutura de Desenvolvimento

```bash
# Ativar ambiente virtual
poetry shell

# Executar em modo desenvolvimento
poetry run uvicorn main:app --reload --log-level debug

# Executar chat local
poetry run python local_chat.py

# Executar testes
poetry run pytest -v
```

### Adicionar Novas Funcionalidades

1. **Novos endpoints:** Adicionar em `main.py` ou criar em `routers/`
2. **Novos modelos:** Definir em `app/models.py`
3. **Nova lógica:** Implementar em `app/services.py`
4. **Novos destinos:** Expandir base em `local_chat.py`

### Integração com Outras IAs

```python
# Exemplo: Adicionar Anthropic Claude
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

## 📊 Performance

- **Latência típica:** 1-3 segundos (OpenAI)
- **Latência local:** < 100ms
- **Memória:** ~50MB base + histórico
- **Concorrência:** Suporta múltiplas sessões

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**Ednilton Rauh - Linuxell**
- Email: ednilton.rauh@outlook.com
- GitHub: [@ednilton](https://github.com/ednilton)

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [LangChain](https://langchain.com/) - Orquestração de LLMs
- [OpenAI](https://openai.com/) - Modelos de linguagem
- [Claude (Anthropic)](https://claude.ai/) - Modelos de linguagem
- [Poetry](https://python-poetry.org/) - Gerenciamento de dependências

## 🔄 Roadmap

- [ ] Interface web com Angular/React/Vue
- [ ] Integração com Anthropic Claude
- [ ] Sistema de usuários e autenticação
- [ ] Banco de dados PostgreSQL/MongoDB
- [ ] Deploy automatizado (Docker/K8s)
- [ ] Integração com WhatsApp/Telegram
- [ ] Sistema de plugins
- [ ] Análise de sentimentos
- [ ] Suporte a múltiplos idiomas
- [ ] Cache Redis para performance

---

⭐ **Se este projeto te ajudou, deixe uma estrela!** ⭐
