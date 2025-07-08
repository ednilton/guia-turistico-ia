#!/usr/bin/env python3
"""
Cliente de terminal para interagir com a API Chat Inteligente
Execute: poetry run python client.py
"""

import requests
import json
import sys
from datetime import datetime
from typing import Optional

class ChatClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"terminal_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def check_api_health(self) -> bool:
        """Verificar se a API está rodando"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API está online - Status: {data['status']}")
                return True
            else:
                print(f"❌ API retornou status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao conectar com a API: {e}")
            print("   Verifique se o servidor está rodando em http://localhost:8000")
            return False
    
    def send_message(self, message: str, session_id: Optional[str] = None) -> Optional[str]:
        """Enviar mensagem para a API"""
        if not session_id:
            session_id = self.session_id
            
        try:
            payload = {
                "message": message,
                "session_id": session_id
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["response"]
            else:
                error_data = response.json()
                print(f"❌ Erro da API: {error_data.get('detail', 'Erro desconhecido')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return None
    
    def get_session_history(self, session_id: Optional[str] = None) -> Optional[dict]:
        """Obter histórico da sessão"""
        if not session_id:
            session_id = self.session_id
            
        try:
            response = requests.get(f"{self.base_url}/sessions/{session_id}/history")
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def list_sessions(self) -> Optional[dict]:
        """Listar todas as sessões"""
        try:
            response = requests.get(f"{self.base_url}/sessions")
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def clear_session(self, session_id: Optional[str] = None) -> bool:
        """Limpar sessão atual"""
        if not session_id:
            session_id = self.session_id
            
        try:
            response = requests.delete(f"{self.base_url}/sessions/{session_id}")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def interactive_chat(self):
        """Modo de chat interativo"""
        print("=" * 60)
        print("🤖 CHAT INTELIGENTE - ASSISTENTE DE VIAGEM")
        print("=" * 60)
        print(f"📱 Sessão: {self.session_id}")
        print("💡 Comandos especiais:")
        print("   /help     - Mostrar ajuda")
        print("   /history  - Ver histórico da conversa")
        print("   /sessions - Listar todas as sessões")
        print("   /clear    - Limpar conversa atual")
        print("   /quit     - Sair do chat")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n🧑 Você: ").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiais
                if user_input.startswith('/'):
                    if user_input == '/help':
                        self.show_help()
                    elif user_input == '/history':
                        self.show_history()
                    elif user_input == '/sessions':
                        self.show_sessions()
                    elif user_input == '/clear':
                        self.clear_current_session()
                    elif user_input == '/quit':
                        print("\n👋 Até logo! Boa viagem!")
                        break
                    else:
                        print("❌ Comando não reconhecido. Digite /help para ver os comandos.")
                    continue
                
                # Enviar mensagem para a API
                print("🤖 Assistente: ", end="", flush=True)
                response = self.send_message(user_input)
                
                if response:
                    print(response)
                else:
                    print("❌ Erro ao processar sua mensagem. Tente novamente.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrompido. Até logo!")
                break
            except EOFError:
                print("\n\n👋 Até logo!")
                break
    
    def show_help(self):
        """Mostrar ajuda"""
        print("\n📚 AJUDA - COMANDOS DISPONÍVEIS:")
        print("   /help     - Mostrar esta ajuda")
        print("   /history  - Ver histórico da conversa atual")
        print("   /sessions - Listar todas as sessões ativas")
        print("   /clear    - Limpar histórico da conversa atual")
        print("   /quit     - Sair do chat")
        print("\n💬 Para conversar, simplesmente digite sua mensagem!")
    
    def show_history(self):
        """Mostrar histórico da sessão"""
        print(f"\n📜 HISTÓRICO DA SESSÃO: {self.session_id}")
        history = self.get_session_history()
        
        if history and history.get('messages'):
            for i, msg in enumerate(history['messages'], 1):
                role = "🧑 Você" if "Human" in msg['type'] else "🤖 Assistente"
                print(f"{i:2d}. {role}: {msg['content']}")
            print(f"\nTotal de mensagens: {history['total_messages']}")
        else:
            print("   (Nenhuma mensagem na sessão atual)")
    
    def show_sessions(self):
        """Mostrar todas as sessões"""
        print("\n📱 SESSÕES ATIVAS:")
        sessions = self.list_sessions()
        
        if sessions and sessions.get('active_sessions'):
            for i, session in enumerate(sessions['active_sessions'], 1):
                current = " (atual)" if session == self.session_id else ""
                print(f"{i:2d}. {session}{current}")
            print(f"\nTotal: {sessions['total_sessions']} sessões")
        else:
            print("   (Nenhuma sessão ativa)")
    
    def clear_current_session(self):
        """Limpar sessão atual"""
        print(f"\n🗑️  Limpando sessão {self.session_id}...")
        if self.clear_session():
            print("✅ Sessão limpa com sucesso!")
        else:
            print("❌ Erro ao limpar a sessão.")

def main():
    """Função principal"""
    client = ChatClient()
    
    # Verificar se a API está rodando
    if not client.check_api_health():
        print("\n💡 Para iniciar a API, execute em outro terminal:")
        print("   poetry run uvicorn main:app --reload")
        sys.exit(1)
    
    # Modo interativo por padrão
    if len(sys.argv) == 1:
        client.interactive_chat()
    
    # Comandos via argumentos
    elif len(sys.argv) >= 2:
        command = sys.argv[1]
        
        if command == "send" and len(sys.argv) >= 3:
            message = " ".join(sys.argv[2:])
            response = client.send_message(message)
            if response:
                print(f"🤖 Resposta: {response}")
        
        elif command == "history":
            client.show_history()
        
        elif command == "sessions":
            client.show_sessions()
        
        elif command == "clear":
            client.clear_current_session()
        
        else:
            print("❌ Comando inválido.")
            print("💡 Uso:")
            print("   python client.py                    # Modo interativo")
            print("   python client.py send 'mensagem'    # Enviar mensagem única")
            print("   python client.py history            # Ver histórico")
            print("   python client.py sessions           # Listar sessões")
            print("   python client.py clear              # Limpar sessão")

if __name__ == "__main__":
    main()