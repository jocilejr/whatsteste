#!/usr/bin/env python3
"""
Teste de importação de mensagens/chats manual
Para debugar o problema de importação
"""

import requests
import json
from datetime import datetime
import uuid

def test_chat_import():
    print("🔍 TESTE DE IMPORTAÇÃO DE CHAT")
    print("="*50)
    
    # Dados de teste simulando conversas importadas do WhatsApp
    test_chats = [
        {
            "id": "5511999999999@s.whatsapp.net",
            "name": "João Silva Teste",
            "unreadCount": 2,
            "messages": [
                {
                    "key": {"id": "msg_001"},
                    "message": {"conversation": "Olá! Teste de importação"}
                }
            ]
        },
        {
            "id": "5511888888888@s.whatsapp.net", 
            "name": "Maria Santos Teste",
            "unreadCount": 0,
            "messages": [
                {
                    "key": {"id": "msg_002"},
                    "message": {"conversation": "Como está o sistema?"}
                }
            ]
        }
    ]
    
    # Dados do usuário simulado
    test_user = {
        "id": "558199999999@s.whatsapp.net",
        "name": "Usuário Teste",
        "phone": "558199999999"
    }
    
    try:
        print("1. Testando importação via API /api/chats/import...")
        
        response = requests.post('http://localhost:8889/api/chats/import', 
            json={
                "instanceId": "test-instance",
                "chats": test_chats,
                "user": test_user,
                "batchNumber": 1,
                "totalBatches": 1
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Importação funcionou!")
            
            # Verificar se os dados foram salvos
            print("\n2. Verificando se chats foram salvos...")
            chats_response = requests.get('http://localhost:8889/api/chats')
            chats = chats_response.json()
            print(f"Chats encontrados: {len(chats)}")
            
            for chat in chats[-2:]:  # Últimos 2 chats
                print(f"  - {chat.get('contact_name')}: {chat.get('last_message')}")
            
            print("\n3. Verificando contatos...")
            contacts_response = requests.get('http://localhost:8889/api/contacts') 
            contacts = contacts_response.json()
            print(f"Contatos encontrados: {len(contacts)}")
            
        else:
            print("❌ Importação falhou!")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def test_message_receive():
    print("\n🔍 TESTE DE RECEBIMENTO DE MENSAGEM")
    print("="*50)
    
    try:
        print("1. Simulando recebimento de mensagem...")
        
        response = requests.post('http://localhost:8889/api/messages/receive',
            json={
                "instanceId": "test-instance",
                "from": "5511999999999@s.whatsapp.net",
                "message": "Mensagem de teste para debugging",
                "timestamp": datetime.now().isoformat(),
                "messageId": f"test_{uuid.uuid4()}",
                "messageType": "text"
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Recebimento de mensagem funcionou!")
            
            # Verificar mensagens
            print("\n2. Verificando mensagens salvas...")
            messages_response = requests.get('http://localhost:8889/api/messages')
            messages = messages_response.json()
            print(f"Total de mensagens: {len(messages)}")
            
            if messages:
                latest = messages[0]
                print(f"Última mensagem: {latest.get('contact_name')} - {latest.get('message')}")
        else:
            print("❌ Recebimento falhou!")
            
    except Exception as e:
        print(f"❌ Erro no teste de mensagem: {e}")

if __name__ == "__main__":
    test_chat_import()
    test_message_receive()