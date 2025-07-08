#!/usr/bin/env python3
"""
Cliente inteligente que detecta automaticamente qual API usar
- Tenta OpenAI primeiro (porta 8000)
- Se falhar, usa chat local (porta 8001)
"""

import requests
import json
import sys
from datetime import datetime
from typing import Optional

class SmartChatClient:
    def __init__(self):
        self.openai_url = "http://localhost:8000"
        self.local_url = "http://localhost:8001"
        self.current_url = None
        self.session_id = f"smart_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def detect_available_api(self) -> str:
        """Detectar qual API está disponível e funcionando"""
        
        # Testar OpenAI API primeiro
        try:
            response = requests.get(f"{self.openai_url}/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                # Verificar se OpenAI está configurada
                if data.get('openai_configured'):
                    print("🤖 Detectado: API OpenAI disponível e configurada")
                    return self.openai_url
                else:
                    print("⚠️  API OpenAI disponível mas não configurada")
        except requests.exceptions.RequestException:
            print("❌ API OpenAI não disponível")
        
        # Testar API local
        try:
            response = requests.get(f"{self.local_url}/health", timeout=3)
            if response.status_code == 200:
                print("🏠 Detectado: Chat local disponível")
                return self.local_url
        except requests.exceptions.RequestException:
            print("❌ Chat local não disponível")
        
        return None
    
    def start_local_server(self):
        """Iniciar servidor local automaticamente"""
        print("🚀 Tentando iniciar chat local...")
        import subprocess
        import time
        
        try:
            # Iniciar servidor local em background
            subprocess.Popen([
                'poetry', 'run', 'python', 'local_chat.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Aguardar servidor iniciar
            time.sleep(3)
            
            # Testar se funcionou
            try:
                response = requests.get(f"{self.local_url}/health", timeout=3)
                if response.status_code == 200:
                    print("✅ Chat local iniciado com sucesso!")
                    return True
            except:
                pass
                
        except Exception as e:
            print(f"❌ Erro ao iniciar chat local: {e}")
        
        return False
    
    def send_message(self, message: str) -> Optional[str]:
        """Enviar mensagem para a API disponível"""
        if not self.current_url:
            print("❌ Nenhuma API disponível")
            return None
            
        try:
            payload = {
                "message": message,
                "session_id": self.session_id
            }
            
            response = requests.post(
                f"{self.current_url}/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["response"]
            elif response.status_code == 500:
                error_data = response.json()
                error_msg = error_data.get('detail', '')
                
                # Se for erro de quota da OpenAI, tentar local
                if 'quota' in error_msg.lower() or '429' in error_msg:
                    print("⚠️  Quota OpenAI excedida. Tentando chat local...")
                    if self.fallback_to_local():
                        return self.send_message(message)
                    
                print(f"❌ Erro da API: {error_msg}")
                return None
            else:
                print(f"❌ Status HTTP: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
            return None
    
    def fallback_to_local(self) -> bool:
        """Tentar usar chat local como fallback"""
        print("🔄 Mudando para chat local...")
        
        # Verificar se local está disponível
        try:
            response = requests.get(f"{self.local_url}/health", timeout=3)
            if response.status_code == 200:
                self.current_url = self.local_url
                print("✅ Conectado ao chat local")
                return True
        except:
            pass
        
        # Tentar iniciar servidor local
        if self.start_local_server():
            self.current_url = self.local_url
            return True
        
        print("❌ Não foi possível conectar ao chat local")
        return False
    
    def interactive_chat(self):
        """Chat interativo inteligente"""
        print("=" * 60)
        print("🧠 CHAT INTELIGENTE - DETECÇÃO AUTOMÁTICA")
        print("=" * 60)
        
        # Detectar API disponível
        self.current_url = self.detect_available_api()
        
        if not self.current_url:
            print("❌ Nenhuma API disponível.")
            print("\n💡 Para resolver:")
            print("   1. Para OpenAI: poetry run uvicorn main:app --reload")
            print("   2. Para local: poetry run python local_chat.py")
            return
        
        api_type = "OpenAI" if self.current_url == self.openai_url else "Local"
        print(f"🎯 Usando: {api_type} API")
        print(f"📱 Sessão: {self.session_id}")
        print("💡 Digite /quit para sair")
        print("=" * 60)
        
        while True:
            try:
                user_input = input(f"\n🧑 Você: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['/quit', '/exit', 'sair']:
                    print("\n👋 Até logo! Boa viagem!")
                    break
                
                # Enviar mensagem
                print("🤖 Assistente: ", end="", flush=True)
                response = self.send_message(user_input)
                
                if response:
                    print(response)
                else:
                    print("❌ Erro ao processar mensagem.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrompido!")
                break
            except EOFError:
                print("\n\n👋 Até logo!")
                break
    
    def show_status(self):
        """Mostrar status das APIs"""
        print("\n🔍 STATUS DAS APIs:")
        
        # Testar OpenAI
        try:
            response = requests.get(f"{self.openai_url}/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                status = "✅ Online"
                if not data.get('openai_configured'):
                    status += " (sem OpenAI key)"
                print(f"   OpenAI API: {status}")
            else:
                print(f"   OpenAI API: ❌ Error {response.status_code}")
        except:
            print("   OpenAI API: ❌ Offline")
        
        # Testar Local
        try:
            response = requests.get(f"{self.local_url}/health", timeout=3)
            if response.status_code == 200:
                print("   Local API:  ✅ Online")
            else:
                print(f"   Local API:  ❌ Error {response.status_code}")
        except:
            print("   Local API:  ❌ Offline")

def main():
    """Função principal"""
    client = SmartChatClient()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        client.show_status()
    else:
        client.interactive_chat()

if __name__ == "__main__":
    main()