#!/usr/bin/env python3
"""
Cliente simples para chat rápido
Execute: poetry run python chat.py
"""

import requests
import json

def chat_simples():
    """Chat simples e direto"""
    print("🤖 Assistente de Viagem - Chat Rápido")
    print("Digite 'sair' para encerrar\n")
    
    session_id = "quick_chat"
    base_url = "http://localhost:8000"
    
    while True:
        try:
            # Input do usuário
            mensagem = input("Você: ").strip()
            
            if mensagem.lower() in ['sair', 'quit', 'exit']:
                print("Até logo! 👋")
                break
            
            if not mensagem:
                continue
            
            # Enviar para API
            payload = {
                "message": mensagem,
                "session_id": session_id
            }
            
            response = requests.post(f"{base_url}/chat", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖: {data['response']}\n")
            else:
                print("❌ Erro na API. Verifique se o servidor está rodando.\n")
                
        except KeyboardInterrupt:
            print("\n\nChat interrompido! 👋")
            break
        except Exception as e:
            print(f"❌ Erro: {e}\n")

if __name__ == "__main__":
    chat_simples()