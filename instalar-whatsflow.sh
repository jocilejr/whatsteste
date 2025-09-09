#!/bin/bash

# WhatsFlow Local - Instalador Ultra-Simples
# Sem sudo, sem MongoDB, sem complicações!

echo "🤖 WhatsFlow Local - Instalador Ultra-Simples"
echo "=============================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "   Instale com: sudo apt install python3 python3-pip"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar diretório
INSTALL_DIR="$HOME/whatsflow-local"
echo "📁 Criando diretório: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Baixar WhatsFlow
echo "⬇️ Criando WhatsFlow Local..."
cat > whatsflow.py << 'WHATSFLOW_CODE'#!/usr/bin/env python3
"""
WhatsFlow Local - Versão Ultra-Simplificada
Sistema de Automação WhatsApp sem dependências complexas

Requisitos: Apenas Python 3.8+ (já vem no Ubuntu)
Instalação: python3 whatsflow-simple.py
Acesso: http://localhost:8000
"""

import json
import sqlite3
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
import asyncio
import subprocess
import sys
import os

# Tentar importar dependências, instalar se necessário
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("📦 Instalando dependências necessárias...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "fastapi", "uvicorn", "pydantic"])
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    import uvicorn

# Configurações
DB_FILE = "whatsflow.db"
PORT = 8000

# Models
class WhatsAppInstance(BaseModel):
    id: str
    name: str
    connected: bool = False
    contacts_count: int = 0
    messages_today: int = 0
    created_at: str

class InstanceCreate(BaseModel):
    name: str

class Message(BaseModel):
    id: str
    contact_name: str
    phone: str
    message: str
    direction: str  # 'incoming' or 'outgoing'
    timestamp: str

class Contact(BaseModel):
    id: str
    name: str
    phone: str
    last_message: str
    timestamp: str

# Database setup
def init_db():
    """Inicializar banco SQLite"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabela de instâncias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instances (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            connected BOOLEAN DEFAULT 0,
            contacts_count INTEGER DEFAULT 0,
            messages_today INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Tabela de contatos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            last_message TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Tabela de mensagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            contact_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            direction TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# FastAPI app
app = FastAPI(title="WhatsFlow Local", description="Sistema de Automação WhatsApp Simplificado")

# Database helper functions
def get_db():
    return sqlite3.connect(DB_FILE)

def dict_factory(cursor, row):
    """Convert sqlite row to dict"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Frontend HTML (embutido no Python)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsFlow Local</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        
        .nav {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .nav-btn {
            background: rgba(255,255,255,0.9);
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .nav-btn:hover { background: white; transform: translateY(-2px); }
        .nav-btn.active { background: white; color: #667eea; }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 500;
            font-size: 0.9rem;
        }
        .status-connected { background: #d4edda; color: #155724; }
        .status-disconnected { background: #f8d7da; color: #721c24; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
        }
        .stat-number { font-size: 2rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 5px; }
        
        .instances-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .instance-card {
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            background: white;
        }
        .instance-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .instance-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { transform: translateY(-1px); opacity: 0.9; }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px;
            border-radius: 16px;
            width: 90%;
            max-width: 500px;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .close { cursor: pointer; font-size: 24px; }
        
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        .empty-state h3 { margin-bottom: 10px; color: #333; }
        
        .loading { text-align: center; padding: 40px; color: #666; }
        
        .qr-container {
            text-align: center;
            padding: 20px;
        }
        .qr-code {
            background: white;
            padding: 20px;
            border-radius: 12px;
            display: inline-block;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        @media (max-width: 768px) {
            .nav { justify-content: center; }
            .stats-grid { grid-template-columns: 1fr; }
            .instances-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 WhatsFlow Local</h1>
            <p>Sistema de Automação WhatsApp Simplificado</p>
        </div>
        
        <div class="nav">
            <button class="nav-btn active" onclick="showSection('dashboard')">📊 Dashboard</button>
            <button class="nav-btn" onclick="showSection('instances')">📱 Instâncias</button>
            <button class="nav-btn" onclick="showSection('messages')">💬 Mensagens</button>
            <button class="nav-btn" onclick="showSection('macros')">🎯 Macros</button>
        </div>
        
        <div id="dashboard" class="section">
            <div class="card">
                <h2>🔗 Status da Conexão</h2>
                <div id="connection-status" class="status-disconnected status-indicator">
                    <span>●</span> WhatsApp não conectado
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Estatísticas</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="contacts-count">0</div>
                        <div class="stat-label">Novos contatos hoje</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="conversations-count">0</div>
                        <div class="stat-label">Conversas ativas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="messages-count">0</div>
                        <div class="stat-label">Mensagens hoje</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="instances" class="section" style="display:none;">
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
                    <h2>📱 Instâncias WhatsApp</h2>
                    <button class="btn btn-primary" onclick="showCreateModal()">➕ Nova Instância</button>
                </div>
                <div id="instances-container" class="instances-grid">
                    <div class="loading">Carregando instâncias...</div>
                </div>
            </div>
        </div>
        
        <div id="messages" class="section" style="display:none;">
            <div class="card">
                <h2>💬 Central de Mensagens</h2>
                <div class="empty-state">
                    <h3>Em desenvolvimento</h3>
                    <p>Central de mensagens será implementada em breve</p>
                </div>
            </div>
        </div>
        
        <div id="macros" class="section" style="display:none;">
            <div class="card">
                <h2>🎯 Macros e Automações</h2>
                <div class="empty-state">
                    <h3>Em desenvolvimento</h3>
                    <p>Sistema de macros será implementado em breve</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Modal Criar Instância -->
    <div id="createModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>➕ Nova Instância WhatsApp</h3>
                <span class="close" onclick="hideCreateModal()">&times;</span>
            </div>
            <form onsubmit="createInstance(event)">
                <div class="form-group">
                    <label>📝 Nome da Instância:</label>
                    <input type="text" id="instanceName" placeholder="Ex: WhatsApp Vendas, WhatsApp Suporte..." required>
                </div>
                <div style="display:flex;gap:10px;">
                    <button type="button" class="btn" onclick="hideCreateModal()">❌ Cancelar</button>
                    <button type="submit" class="btn btn-success" style="flex:1;">✅ Criar Instância</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Modal QR Code -->
    <div id="qrModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>📱 Conectar WhatsApp</h3>
                <span class="close" onclick="hideQRModal()">&times;</span>
            </div>
            <div class="qr-container">
                <p><strong>Como conectar:</strong></p>
                <ol style="text-align:left;margin:20px 0;">
                    <li>Abra o WhatsApp no seu celular</li>
                    <li>Toque em Configurações ⚙️</li>
                    <li>Toque em Aparelhos conectados</li>
                    <li>Toque em Conectar um aparelho</li>
                    <li>Escaneie o QR Code abaixo</li>
                </ol>
                <div id="qr-code-container" class="qr-code">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=demo-qr-whatsflow-local" alt="QR Code">
                </div>
                <p style="margin-top:20px;"><small>🚧 Modo demonstração - QR Code simulado</small></p>
            </div>
            <div style="text-align:center;margin-top:20px;">
                <button class="btn btn-danger" onclick="hideQRModal()">🚫 Fechar</button>
            </div>
        </div>
    </div>

    <script>
        // State management
        let instances = [];
        let currentSection = 'dashboard';
        
        // Navigation
        function showSection(section) {
            document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(section).style.display = 'block';
            event.target.classList.add('active');
            currentSection = section;
            
            if (section === 'instances') {
                loadInstances();
            }
        }
        
        // Modal management
        function showCreateModal() {
            document.getElementById('createModal').style.display = 'block';
        }
        
        function hideCreateModal() {
            document.getElementById('createModal').style.display = 'none';
            document.getElementById('instanceName').value = '';
        }
        
        function showQRModal(instanceId) {
            document.getElementById('qrModal').style.display = 'block';
        }
        
        function hideQRModal() {
            document.getElementById('qrModal').style.display = 'none';
        }
        
        // API calls
        async function loadInstances() {
            try {
                const response = await fetch('/api/instances');
                instances = await response.json();
                renderInstances();
            } catch (error) {
                console.error('Erro ao carregar instâncias:', error);
                document.getElementById('instances-container').innerHTML = 
                    '<div class="empty-state"><h3>Erro ao carregar</h3><p>Tente recarregar a página</p></div>';
            }
        }
        
        async function createInstance(event) {
            event.preventDefault();
            const name = document.getElementById('instanceName').value;
            
            try {
                const response = await fetch('/api/instances', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name })
                });
                
                if (response.ok) {
                    hideCreateModal();
                    loadInstances();
                    alert(`✅ Instância "${name}" criada com sucesso!`);
                } else {
                    alert('❌ Erro ao criar instância');
                }
            } catch (error) {
                alert('❌ Erro de conexão');
            }
        }
        
        async function connectInstance(instanceId) {
            showQRModal(instanceId);
            // Simular conexão após 3 segundos
            setTimeout(() => {
                hideQRModal();
                alert('✅ WhatsApp conectado com sucesso! (modo demo)');
                loadInstances();
            }, 3000);
        }
        
        async function deleteInstance(instanceId) {
            if (!confirm('Tem certeza que deseja excluir esta instância?')) return;
            
            try {
                const response = await fetch(`/api/instances/${instanceId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    loadInstances();
                    alert('✅ Instância excluída com sucesso!');
                } else {
                    alert('❌ Erro ao excluir instância');
                }
            } catch (error) {
                alert('❌ Erro de conexão');
            }
        }
        
        // Render functions
        function renderInstances() {
            const container = document.getElementById('instances-container');
            
            if (instances.length === 0) {
                container.innerHTML = `
                    <div class="empty-state" style="grid-column: 1/-1;">
                        <h3>📱 Nenhuma instância WhatsApp</h3>
                        <p>Crie sua primeira instância para começar</p>
                        <br>
                        <button class="btn btn-primary" onclick="showCreateModal()">🚀 Criar Primeira Instância</button>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = instances.map(instance => `
                <div class="instance-card">
                    <div class="instance-header">
                        <div>
                            <h3>${instance.name}</h3>
                            <small>ID: ${instance.id.substring(0, 8)}...</small>
                        </div>
                        <div class="status-indicator ${instance.connected ? 'status-connected' : 'status-disconnected'}">
                            <span>●</span> ${instance.connected ? 'Conectado' : 'Desconectado'}
                        </div>
                    </div>
                    
                    <div class="stats-grid" style="grid-template-columns: 1fr 1fr;">
                        <div class="stat-card">
                            <div class="stat-number">${instance.contacts_count}</div>
                            <div class="stat-label">Contatos</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${instance.messages_today}</div>
                            <div class="stat-label">Mensagens hoje</div>
                        </div>
                    </div>
                    
                    <div class="instance-actions">
                        ${!instance.connected ? 
                            `<button class="btn btn-success" onclick="connectInstance('${instance.id}')" style="flex:1;">🔗 Conectar</button>` :
                            `<button class="btn btn-danger" onclick="disconnectInstance('${instance.id}')" style="flex:1;">⏸️ Desconectar</button>`
                        }
                        <button class="btn btn-danger" onclick="deleteInstance('${instance.id}')">🗑️ Excluir</button>
                    </div>
                </div>
            `).join('');
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Load initial stats
            updateStats();
            
            // Update stats every 30 seconds
            setInterval(updateStats, 30000);
        });
        
        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('contacts-count').textContent = stats.contacts_count;
                document.getElementById('conversations-count').textContent = stats.conversations_count;
                document.getElementById('messages-count').textContent = stats.messages_count;
            } catch (error) {
                console.error('Erro ao carregar estatísticas:', error);
            }
        }
    </script>
</body>
</html>
'''

# API Routes
@app.get("/", response_class=HTMLResponse)
async def home():
    """Página principal"""
    return HTML_TEMPLATE

@app.get("/api/instances")
async def get_instances():
    """Listar todas as instâncias"""
    conn = get_db()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM instances ORDER BY created_at DESC")
    instances = cursor.fetchall()
    conn.close()
    
    return instances

@app.post("/api/instances")
async def create_instance(instance: InstanceCreate):
    """Criar nova instância"""
    conn = get_db()
    cursor = conn.cursor()
    
    instance_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("""
        INSERT INTO instances (id, name, created_at)
        VALUES (?, ?, ?)
    """, (instance_id, instance.name, created_at))
    
    conn.commit()
    conn.close()
    
    return {"id": instance_id, "name": instance.name, "created_at": created_at}

@app.delete("/api/instances/{instance_id}")
async def delete_instance(instance_id: str):
    """Excluir instância"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM instances WHERE id = ?", (instance_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Instance not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Instance deleted successfully"}

@app.get("/api/stats")
async def get_stats():
    """Obter estatísticas do dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Contar contatos
    cursor.execute("SELECT COUNT(*) FROM contacts")
    contacts_count = cursor.fetchone()[0]
    
    # Contar mensagens hoje
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE timestamp >= ?", (today,))
    messages_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "contacts_count": contacts_count,
        "conversations_count": contacts_count,  # Simplificado
        "messages_count": messages_count
    }

# Adicionar alguns dados de demonstração
def add_demo_data():
    """Adicionar dados de demonstração"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verificar se já existem dados
    cursor.execute("SELECT COUNT(*) FROM instances")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Adicionar instâncias de exemplo
    demo_instances = [
        {"id": str(uuid.uuid4()), "name": "WhatsApp Vendas", "connected": False},
        {"id": str(uuid.uuid4()), "name": "WhatsApp Suporte", "connected": True}
    ]
    
    for instance in demo_instances:
        cursor.execute("""
            INSERT INTO instances (id, name, connected, contacts_count, messages_today, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            instance["id"], 
            instance["name"], 
            instance["connected"],
            3 if instance["connected"] else 0,
            5 if instance["connected"] else 0,
            datetime.now(timezone.utc).isoformat()
        ))
    
    # Adicionar contatos de exemplo
    demo_contacts = [
        {"id": str(uuid.uuid4()), "name": "João Silva", "phone": "+5511999999999"},
        {"id": str(uuid.uuid4()), "name": "Maria Santos", "phone": "+5511888888888"},
        {"id": str(uuid.uuid4()), "name": "Pedro Costa", "phone": "+5511777777777"}
    ]
    
    for contact in demo_contacts:
        cursor.execute("""
            INSERT INTO contacts (id, name, phone, last_message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            contact["id"],
            contact["name"],
            contact["phone"],
            "Olá! Como posso ajudar?",
            datetime.now(timezone.utc).isoformat()
        ))
    
    # Adicionar mensagens de exemplo
    demo_messages = [
        {"contact_name": "João Silva", "phone": "+5511999999999", "message": "Olá! Gostaria de saber sobre os produtos", "direction": "incoming"},
        {"contact_name": "João Silva", "phone": "+5511999999999", "message": "Claro! Temos várias opções disponíveis", "direction": "outgoing"},
        {"contact_name": "Maria Santos", "phone": "+5511888888888", "message": "Qual o horário de funcionamento?", "direction": "incoming"},
        {"contact_name": "Maria Santos", "phone": "+5511888888888", "message": "Funcionamos de 8h às 18h", "direction": "outgoing"},
        {"contact_name": "Pedro Costa", "phone": "+5511777777777", "message": "Obrigado pelo atendimento!", "direction": "incoming"}
    ]
    
    for msg in demo_messages:
        cursor.execute("""
            INSERT INTO messages (id, contact_name, phone, message, direction, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            msg["contact_name"],
            msg["phone"],
            msg["message"],
            msg["direction"],
            datetime.now(timezone.utc).isoformat()
        ))
    
    conn.commit()
    conn.close()

def main():
    """Função principal"""
    print("🤖 WhatsFlow Local - Versão Ultra-Simplificada")
    print("=" * 50)
    
    # Inicializar banco de dados
    print("📁 Inicializando banco de dados...")
    init_db()
    add_demo_data()
    
    print("✅ WhatsFlow Local configurado com sucesso!")
    print(f"🌐 Acesse: http://localhost:{PORT}")
    print(f"📁 Banco de dados: {Path(DB_FILE).absolute()}")
    print()
    print("🚀 Iniciando servidor...")
    print("   Para parar: Ctrl+C")
    print()
    
    # Iniciar servidor
    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 WhatsFlow Local finalizado!")

if __name__ == "__main__":
    main()