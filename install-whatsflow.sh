#!/bin/bash

# WhatsFlow - Instalação Ultra-Simples (LOCALHOST)
# Sistema completo de Automação WhatsApp com Baileys
# Instalação automática com apenas 1 comando

set -e

echo "🤖 WHATSFLOW - Instalação Automática Localhost"
echo "==============================================="
echo ""

# Detectar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ Sistema detectado: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ Sistema detectado: macOS"
else
    echo "❌ Sistema não suportado: $OSTYPE"
    exit 1
fi

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Atualizar sistema
echo "📦 Atualizando sistema..."
if command_exists apt-get; then
    sudo apt-get update -qq
elif command_exists yum; then
    sudo yum update -y -q
elif command_exists brew; then
    brew update
fi

# Instalar Node.js
if ! command_exists node; then
    echo "📦 Instalando Node.js..."
    if command_exists apt-get; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif command_exists yum; then
        curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
        sudo yum install -y nodejs npm
    elif command_exists brew; then
        brew install node
    fi
else
    echo "✅ Node.js já instalado"
fi

# Instalar Python
if ! command_exists python3; then
    echo "📦 Instalando Python..."
    if command_exists apt-get; then
        sudo apt-get install -y python3 python3-pip
    elif command_exists yum; then
        sudo yum install -y python3 python3-pip
    elif command_exists brew; then
        brew install python
    fi
else
    echo "✅ Python já instalado"
fi

# Instalar MongoDB
if ! command_exists mongod; then
    echo "📦 Instalando MongoDB..."
    if command_exists apt-get; then
        wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
        echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
        sudo apt-get update
        sudo apt-get install -y mongodb-org
    elif command_exists yum; then
        sudo tee /etc/yum.repos.d/mongodb-org-6.0.repo << 'EOF'
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
EOF
        sudo yum install -y mongodb-org
    elif command_exists brew; then
        brew tap mongodb/brew
        brew install mongodb-community
    fi
else
    echo "✅ MongoDB já instalado"
fi

# Instalar Yarn globalmente
if ! command_exists yarn; then
    echo "📦 Instalando Yarn..."
    sudo npm install -g yarn
else
    echo "✅ Yarn já instalado"
fi

# Criar diretório de trabalho
INSTALL_DIR="$HOME/whatsflow"
echo "📁 Criando diretório: $INSTALL_DIR"
rm -rf "$INSTALL_DIR" # Remove se já existir
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "⬇️ Criando aplicação WhatsFlow completa..."

# Criar estrutura de diretórios
mkdir -p backend frontend/src/components frontend/public whatsapp-service

# ============================================
# BACKEND COMPLETO
# ============================================
echo "🔧 Criando backend completo..."

cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
motor==3.3.2
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.25.2
starlette==0.27.0
EOF

cat > backend/.env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=whatsflow
CORS_ORIGINS=http://localhost:3000
EOF

# Criar o arquivo server.py completo (backend completo do WhatsFlow)
cat > backend/server.py << 'EOF'
from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

WHATSAPP_SERVICE_URL = "http://localhost:3001"

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class Contact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phone_number: str
    name: str
    device_id: str = "whatsapp_1"
    device_name: str = "WhatsApp 1"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_message_at: Optional[datetime] = None
    tags: List[str] = []
    is_active: bool = True

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contact_id: str
    phone_number: str
    device_id: str = "whatsapp_1"
    device_name: str = "WhatsApp 1"
    message: str
    direction: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_id: Optional[str] = None
    delivered: bool = False
    read: bool = False

class IncomingMessage(BaseModel):
    phone_number: str
    message: str
    message_id: str
    timestamp: int
    push_name: Optional[str] = None
    device_id: Optional[str] = "whatsapp_1"
    device_name: Optional[str] = "WhatsApp 1"

class OutgoingMessage(BaseModel):
    phone_number: str
    message: str
    device_id: Optional[str] = "whatsapp_1"

class MacroTrigger(BaseModel):
    contact_id: str
    macro_name: str
    webhook_url: str

class MessageResponse(BaseModel):
    reply: Optional[str] = None
    success: bool = True

class QRUpdate(BaseModel):
    qr: str

class ConnectionUpdate(BaseModel):
    connected: bool
    user: Optional[dict] = None

class Webhook(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    description: Optional[str] = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True

class WebhookCreate(BaseModel):
    name: str
    url: str
    description: Optional[str] = ""

class WebhookTrigger(BaseModel):
    webhook_id: str
    webhook_url: str
    data: Dict[str, Any]

class WhatsAppInstance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    device_id: str
    device_name: str
    connected: bool = False
    user: Optional[Dict[str, Any]] = None
    contacts_count: int = 0
    messages_today: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_connected_at: Optional[datetime] = None

class WhatsAppInstanceCreate(BaseModel):
    name: str
    device_name: Optional[str] = None

# Database helpers
async def get_or_create_contact(phone_number: str, name: str = None, device_id: str = "whatsapp_1", device_name: str = "WhatsApp 1") -> dict:
    contacts_collection = db.contacts
    
    contact = await contacts_collection.find_one({
        "phone_number": phone_number,
        "device_id": device_id
    })
    
    if not contact:
        contact_data = Contact(
            phone_number=phone_number,
            name=name or f"Contact {phone_number[-4:]}",
            device_id=device_id,
            device_name=device_name,
            last_message_at=datetime.now(timezone.utc)
        )
        result = await contacts_collection.insert_one(contact_data.dict())
        contact_data.id = str(result.inserted_id)
        return contact_data.dict()
    else:
        await contacts_collection.update_one(
            {"phone_number": phone_number, "device_id": device_id},
            {"$set": {"last_message_at": datetime.now(timezone.utc)}}
        )
        contact['id'] = str(contact.get('_id', contact.get('id')))
    
    return contact

async def save_message(contact_id: str, phone_number: str, message: str, direction: str, device_id: str = "whatsapp_1", device_name: str = "WhatsApp 1", message_id: str = None):
    messages_collection = db.messages
    
    message_data = Message(
        contact_id=contact_id,
        phone_number=phone_number,
        device_id=device_id,
        device_name=device_name,
        message=message,
        direction=direction,
        message_id=message_id
    )
    
    await messages_collection.insert_one(message_data.dict())
    return message_data

# Background task for webhook triggers
async def trigger_webhook_async(webhook_url: str, data: Dict[str, Any]):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            logging.info(f"Webhook triggered: {webhook_url} - Status: {response.status_code}")
            return {"success": True, "status_code": response.status_code}
            
    except Exception as e:
        logging.error(f"Webhook trigger failed: {webhook_url} - Error: {str(e)}")
        return {"success": False, "error": str(e)}

# WhatsApp Instances Routes
@api_router.get("/whatsapp/instances")
async def get_whatsapp_instances():
    """Get all WhatsApp instances"""
    try:
        instances = await db.whatsapp_instances.find().to_list(100)
        
        for instance in instances:
            instance['id'] = str(instance.get('_id'))
            if '_id' in instance:
                del instance['_id']
            
            contacts_count = await db.contacts.count_documents({
                "device_id": instance.get('device_id')
            })
            instance['contacts_count'] = contacts_count
            
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            messages_today = await db.messages.count_documents({
                "device_id": instance.get('device_id'),
                "timestamp": {"$gte": today}
            })
            instance['messages_today'] = messages_today
        
        return instances
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/whatsapp/instances")
async def create_whatsapp_instance(instance_data: WhatsAppInstanceCreate):
    """Create a new WhatsApp instance"""
    try:
        device_id = f"whatsapp_{str(uuid.uuid4())[:8]}"
        device_name = instance_data.device_name or instance_data.name
        
        instance = WhatsAppInstance(
            name=instance_data.name,
            device_id=device_id,
            device_name=device_name
        )
        
        result = await db.whatsapp_instances.insert_one(instance.dict())
        instance.id = str(result.inserted_id)
        
        return {"success": True, "instance": instance.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/whatsapp/instances/{instance_id}/connect")
async def connect_whatsapp_instance(instance_id: str):
    """Start connection process for a WhatsApp instance"""
    try:
        instance = await db.whatsapp_instances.find_one({"id": instance_id})
        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")
        
        return {"success": True, "message": "Connection initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/whatsapp/instances/{instance_id}/qr")
async def get_instance_qr(instance_id: str):
    """Get QR code for specific instance"""
    try:
        instance = await db.whatsapp_instances.find_one({"id": instance_id})
        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")
        
        qr_data = f"whatsapp-instance-{instance_id}-{datetime.now().timestamp()}"
        
        return {"qr": qr_data, "connected": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/whatsapp/instances/{instance_id}/disconnect")
async def disconnect_whatsapp_instance(instance_id: str):
    """Disconnect a WhatsApp instance"""
    try:
        result = await db.whatsapp_instances.update_one(
            {"id": instance_id},
            {"$set": {
                "connected": False,
                "user": None,
                "last_connected_at": datetime.now(timezone.utc)
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Instance not found")
        
        return {"success": True, "message": "Instance disconnected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/whatsapp/instances/{instance_id}")
async def delete_whatsapp_instance(instance_id: str):
    """Delete a WhatsApp instance"""
    try:
        result = await db.whatsapp_instances.delete_one({"id": instance_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Instance not found")
        
        return {"success": True, "message": "Instance deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WhatsApp Routes
@api_router.post("/whatsapp/message", response_model=MessageResponse)
async def handle_whatsapp_message(message_data: IncomingMessage):
    """Process incoming WhatsApp messages"""
    try:
        phone_number = message_data.phone_number
        message_text = message_data.message
        push_name = message_data.push_name
        device_id = message_data.device_id or "whatsapp_1"
        device_name = message_data.device_name or "WhatsApp 1"
        
        contact = await get_or_create_contact(phone_number, push_name, device_id, device_name)
        
        await save_message(
            contact['id'], 
            phone_number, 
            message_text, 
            'incoming',
            device_id,
            device_name,
            message_data.message_id
        )
        
        reply = f"Mensagem recebida via {device_name}: '{message_text}'"
        
        await save_message(contact['id'], phone_number, reply, 'outgoing', device_id, device_name)
        
        return MessageResponse(reply=reply)
        
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        return MessageResponse(
            reply="Desculpe, ocorreu um erro ao processar sua mensagem.",
            success=False
        )

@api_router.post("/whatsapp/send")
async def send_whatsapp_message(message: OutgoingMessage):
    """Send message via WhatsApp service"""
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                f"{WHATSAPP_SERVICE_URL}/send",
                json={
                    "phone_number": message.phone_number,
                    "message": message.message
                }
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/whatsapp/qr")
async def get_qr_code():
    """Get current QR code for authentication"""
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(f"{WHATSAPP_SERVICE_URL}/qr")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/whatsapp/status")
async def get_whatsapp_status():
    """Get WhatsApp connection status"""
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(f"{WHATSAPP_SERVICE_URL}/status")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Messages and Contacts Routes
@api_router.get("/contacts")
async def get_contacts(device_id: Optional[str] = None):
    """Get all contacts, optionally filtered by device"""
    query = {}
    if device_id and device_id != "all":
        query["device_id"] = device_id
        
    contacts = await db.contacts.find(query).sort("last_message_at", -1).to_list(100)
    for contact in contacts:
        contact['id'] = str(contact.get('_id'))
        if '_id' in contact:
            del contact['_id']
    return contacts

@api_router.get("/devices")
async def get_devices():
    """Get list of all devices"""
    pipeline = [
        {"$group": {"_id": "$device_id", "device_name": {"$first": "$device_name"}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    devices = await db.contacts.aggregate(pipeline).to_list(100)
    
    result = []
    for device in devices:
        result.append({
            "device_id": device["_id"],
            "device_name": device["device_name"],
            "contact_count": device["count"]
        })
    
    total_contacts = await db.contacts.count_documents({})
    result.insert(0, {
        "device_id": "all",
        "device_name": "Todos os Dispositivos",
        "contact_count": total_contacts
    })
    
    return result

@api_router.get("/contacts/{contact_id}/messages")
async def get_contact_messages(contact_id: str):
    """Get messages for a specific contact"""
    messages = await db.messages.find({"contact_id": contact_id}).sort("timestamp", 1).to_list(1000)
    for message in messages:
        message['id'] = str(message.get('_id'))
        if '_id' in message:
            del message['_id']
    return messages

@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        new_contacts_today = await db.contacts.count_documents({
            "created_at": {"$gte": today}
        })
        
        active_conversations = await db.contacts.count_documents({
            "is_active": True
        })
        
        messages_today = await db.messages.count_documents({
            "timestamp": {"$gte": today}
        })
        
        return {
            "new_contacts_today": new_contacts_today,
            "active_conversations": active_conversations,
            "messages_today": messages_today
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Webhook Routes
@api_router.get("/webhooks")
async def get_webhooks():
    """Get all webhooks"""
    webhooks = await db.webhooks.find({"active": True}).to_list(100)
    for webhook in webhooks:
        webhook['id'] = str(webhook.get('_id'))
        if '_id' in webhook:
            del webhook['_id']
    return webhooks

@api_router.post("/webhooks")
async def create_webhook(webhook: WebhookCreate):
    """Create a new webhook"""
    try:
        webhook_data = Webhook(**webhook.dict())
        result = await db.webhooks.insert_one(webhook_data.dict())
        webhook_data.id = str(result.inserted_id)
        return webhook_data.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """Delete a webhook"""
    try:
        result = await db.webhooks.update_one(
            {"_id": webhook_id},
            {"$set": {"active": False}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Webhook not found")
        return {"message": "Webhook deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/webhooks/trigger")
async def trigger_webhook(webhook_trigger: WebhookTrigger, background_tasks: BackgroundTasks):
    """Trigger a webhook with contact data"""
    try:
        background_tasks.add_task(
            trigger_webhook_async,
            webhook_trigger.webhook_url,
            webhook_trigger.data
        )
        
        webhook_log = {
            "webhook_id": webhook_trigger.webhook_id,
            "webhook_url": webhook_trigger.webhook_url,
            "data": webhook_trigger.data,
            "triggered_at": datetime.now(timezone.utc),
            "status": "triggered"
        }
        await db.webhook_logs.insert_one(webhook_log)
        
        return {"message": "Webhook triggered successfully", "status": "processing"}
        
    except Exception as e:
        logging.error(f"Error triggering webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/macros/trigger")
async def trigger_macro(macro: MacroTrigger, background_tasks: BackgroundTasks):
    """Trigger a macro (webhook) for a specific contact"""
    try:
        contact = await db.contacts.find_one({"_id": macro.contact_id})
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        webhook_data = {
            "contact_name": contact["name"],
            "phone_number": contact["phone_number"],
            "device_id": contact.get("device_id", "whatsapp_1"),
            "device_name": contact.get("device_name", "WhatsApp 1"),
            "jid": f"{contact['phone_number']}@s.whatsapp.net",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "macro_name": macro.macro_name,
            "tags": contact.get("tags", [])
        }
        
        background_tasks.add_task(
            trigger_webhook_async,
            macro.webhook_url,
            webhook_data
        )
        
        macro_log = {
            "contact_id": macro.contact_id,
            "macro_name": macro.macro_name,
            "webhook_url": macro.webhook_url,
            "data": webhook_data,
            "triggered_at": datetime.now(timezone.utc),
            "status": "triggered"
        }
        await db.macro_logs.insert_one(macro_log)
        
        return {"message": f"Macro '{macro.macro_name}' triggered successfully", "status": "processing"}
        
    except Exception as e:
        logging.error(f"Error triggering macro: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Original routes
@api_router.get("/")
async def root():
    return {"message": "WhatsFlow API - Sistema de Automação WhatsApp"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
EOF

# ============================================
# FRONTEND COMPLETO
# ============================================
echo "🎨 Criando frontend completo..."

cat > frontend/package.json << 'EOF'
{
  "name": "whatsflow-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "reactflow": "^11.10.0",
    "@tailwindcss/forms": "^0.5.7"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

cat > frontend/.env << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
EOF

cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="WhatsFlow - Sistema de Automação WhatsApp" />
    <title>WhatsFlow - Automação WhatsApp</title>
  </head>
  <body>
    <noscript>Você precisa habilitar JavaScript para usar este app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

cat > frontend/src/index.css << 'EOF'
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
EOF# Continuação do script de instalação - App.js e componentes

# Criar App.js completo
cat > frontend/src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import FlowEditor from './components/FlowEditor';
import FlowList from './components/FlowList';
import MessagesCenter from './components/MessagesCenter';
import WhatsAppInstances from './components/WhatsAppInstances';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// QR Code Component
const QRCode = ({ value }) => {
  if (!value) return null;
  
  return (
    <div className="qr-container">
      <div className="qr-code">
        <img 
          src={`https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodeURIComponent(value)}`}
          alt="QR Code"
          className="qr-image"
        />
      </div>
    </div>
  );
};

// Navigation Component
const Navigation = ({ currentView, onViewChange }) => {
  return (
    <nav className="main-navigation">
      <div className="nav-items">
        <button 
          className={`nav-item ${currentView === 'dashboard' ? 'active' : ''}`}
          onClick={() => onViewChange('dashboard')}
        >
          <span className="nav-icon">📊</span>
          <span>Dashboard</span>
        </button>
        <button 
          className={`nav-item ${currentView === 'flows' ? 'active' : ''}`}
          onClick={() => onViewChange('flows')}
        >
          <span className="nav-icon">🎯</span>
          <span>Fluxos</span>
        </button>
        <button 
          className={`nav-item ${currentView === 'contacts' ? 'active' : ''}`}
          onClick={() => onViewChange('contacts')}
        >
          <span className="nav-icon">👥</span>
          <span>Contatos</span>
        </button>
        <button 
          className={`nav-item ${currentView === 'messages' ? 'active' : ''}`}
          onClick={() => onViewChange('messages')}
        >
          <span className="nav-icon">💬</span>
          <span>Mensagens</span>
        </button>
        <button 
          className={`nav-item ${currentView === 'instances' ? 'active' : ''}`}
          onClick={() => onViewChange('instances')}
        >
          <span className="nav-icon">📱</span>
          <span>Instâncias</span>
        </button>
      </div>
    </nav>
  );
};

// WhatsApp Connection Component
const WhatsAppConnection = () => {
  const [qrCode, setQrCode] = useState(null);
  const [status, setStatus] = useState('disconnected');
  const [loading, setLoading] = useState(false);
  const [connectedUser, setConnectedUser] = useState(null);
  const [isDemoMode, setIsDemoMode] = useState(false);

  const checkStatus = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/status`);
      setStatus(response.data.connected ? 'connected' : 'disconnected');
      setConnectedUser(response.data.user);
      setIsDemoMode(response.data.demo || false);
      return response.data.connected;
    } catch (error) {
      console.error('Status check failed:', error);
      setStatus('error');
      return false;
    }
  };

  const fetchQR = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/qr`);
      if (response.data.qr) {
        setQrCode(response.data.qr);
      } else {
        setQrCode(null);
      }
    } catch (error) {
      console.error('QR fetch failed:', error);
    }
  };

  const simulateConnection = async () => {
    try {
      const response = await axios.post('http://localhost:3001/demo/connect');
      if (response.data.success) {
        await checkStatus();
      }
    } catch (error) {
      console.error('Demo connection failed:', error);
    }
  };

  const startPolling = () => {
    const interval = setInterval(async () => {
      const isConnected = await checkStatus();
      if (isConnected) {
        setQrCode(null);
        clearInterval(interval);
      } else {
        await fetchQR();
      }
    }, 3000);

    return interval;
  };

  useEffect(() => {
    checkStatus();
    const interval = startPolling();

    return () => clearInterval(interval);
  }, []);

  const handleConnect = async () => {
    setLoading(true);
    await checkStatus();
    if (status !== 'connected') {
      startPolling();
    }
    setLoading(false);
  };

  return (
    <div className="whatsapp-connection">
      <div className="connection-header">
        <h2>🔗 Conexão WhatsApp</h2>
        <div className={`status-indicator ${status}`}>
          <div className="status-dot"></div>
          <span className="status-text">
            {status === 'connected' ? 'Conectado' : 
             status === 'disconnected' ? 'Desconectado' : 'Erro'}
            {isDemoMode && ' (Demo)'}
          </span>
        </div>
      </div>

      {isDemoMode && (
        <div className="demo-badge">
          🚧 <strong>Modo Demonstração</strong> - Simulando funcionalidade WhatsApp para testes
        </div>
      )}

      {status === 'connected' && connectedUser && (
        <div className="connected-info">
          <div className="success-badge">
            ✅ WhatsApp conectado com sucesso!
          </div>
          <div className="user-info">
            <strong>Usuário:</strong> {connectedUser.name || connectedUser.id}
          </div>
        </div>
      )}

      {status === 'disconnected' && (
        <div className="qr-section">
          <div className="warning-badge">
            ⚠️ WhatsApp não está conectado. {isDemoMode ? 'Clique para simular conexão ou ' : ''}Escaneie o QR code para conectar.
          </div>
          
          {qrCode && (
            <div className="qr-display">
              <h3>Escaneie este QR Code com o WhatsApp:</h3>
              <QRCode value={qrCode} />
              <p className="qr-instructions">
                Abra o WhatsApp → Configurações → Aparelhos conectados → Conectar um aparelho
              </p>
            </div>
          )}
          
          <div className="button-group">
            <button 
              className="connect-button"
              onClick={handleConnect}
              disabled={loading}
            >
              {loading ? 'Conectando...' : 'Conectar WhatsApp'}
            </button>
            
            {isDemoMode && (
              <button 
                className="demo-button"
                onClick={simulateConnection}
                disabled={loading}
              >
                🎯 Simular Conexão (Demo)
              </button>
            )}
          </div>
        </div>
      )}

      {status === 'error' && (
        <div className="error-badge">
          ❌ Erro de conexão. Verifique se o serviço WhatsApp está em execução.
        </div>
      )}
    </div>
  );
};

// Dashboard Stats Component
const DashboardStats = () => {
  const [stats, setStats] = useState({
    new_contacts_today: 0,
    active_conversations: 0,
    messages_today: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/dashboard/stats`);
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-stats">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{stats.new_contacts_today}</h3>
            <p>Novos contatos hoje</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">💬</div>
          <div className="stat-content">
            <h3>{stats.active_conversations}</h3>
            <p>Conversas ativas</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📨</div>
          <div className="stat-content">
            <h3>{stats.messages_today}</h3>
            <p>Mensagens hoje</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Contacts List Component
const ContactsList = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const response = await axios.get(`${API}/contacts`);
        setContacts(response.data);
      } catch (error) {
        console.error('Failed to fetch contacts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchContacts();
  }, []);

  if (loading) {
    return <div className="loading">Carregando contatos...</div>;
  }

  return (
    <div className="contacts-list">
      <h3>📞 Contatos Recentes</h3>
      {contacts.length === 0 ? (
        <div className="empty-state">
          <p>Nenhum contato encontrado ainda.</p>
          <p>Os contatos aparecerão aqui quando começarem a enviar mensagens.</p>
        </div>
      ) : (
        <div className="contacts-grid">
          {contacts.slice(0, 6).map(contact => (
            <div key={contact.id} className="contact-card">
              <div className="contact-avatar">
                {contact.name.charAt(0).toUpperCase()}
              </div>
              <div className="contact-info">
                <h4>{contact.name}</h4>
                <p>{contact.phone_number}</p>
                <div className="contact-tags">
                  {contact.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [showFlowEditor, setShowFlowEditor] = useState(false);
  const [editingFlow, setEditingFlow] = useState(null);

  const handleCreateFlow = () => {
    setEditingFlow(null);
    setShowFlowEditor(true);
  };

  const handleEditFlow = (flow) => {
    setEditingFlow(flow);
    setShowFlowEditor(true);
  };

  const handleCloseFlowEditor = () => {
    setShowFlowEditor(false);
    setEditingFlow(null);
  };

  const handleSaveFlow = (flowData) => {
    console.log('Flow saved:', flowData);
    setShowFlowEditor(false);
    setEditingFlow(null);
  };

  if (showFlowEditor) {
    return (
      <FlowEditor
        flowId={editingFlow?.id}
        onSave={handleSaveFlow}
        onClose={handleCloseFlowEditor}
      />
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 WhatsFlow</h1>
          <p>Sistema de Automação para WhatsApp</p>
        </div>
      </header>

      <Navigation currentView={currentView} onViewChange={setCurrentView} />

      <main className="app-main">
        <div className="container">
          {currentView === 'dashboard' && (
            <>
              <WhatsAppConnection />
              
              <section className="dashboard-section">
                <h2>📊 Dashboard</h2>
                <DashboardStats />
              </section>

              <section className="contacts-section">
                <ContactsList />
              </section>
            </>
          )}

          {currentView === 'flows' && (
            <FlowList
              onCreateFlow={handleCreateFlow}
              onEditFlow={handleEditFlow}
            />
          )}

          {currentView === 'contacts' && (
            <section className="contacts-section">
              <h2>👥 Gerenciamento de Contatos</h2>
              <ContactsList />
            </section>
          )}

          {currentView === 'messages' && (
            <MessagesCenter />
          )}

          {currentView === 'instances' && (
            <WhatsAppInstances />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
EOF