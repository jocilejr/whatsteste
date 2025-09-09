#!/usr/bin/env python3
"""
WhatsFlow Zero-Deps - Versão SEM dependências externas
Sistema de Automação WhatsApp com ZERO complicações

Requisitos: APENAS Python 3 (nada mais!)
Instalação: python3 whatsflow-zero-deps.py
Acesso: http://localhost:8090
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
import subprocess
import sys
import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.parse

# Auto-instalar dependências mínimas se necessário
def ensure_dependencies():
    try:
        import fastapi, uvicorn, pydantic
        return True
    except ImportError:
        print("📦 Instalando dependências mínimas...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "fastapi", "uvicorn[standard]", "pydantic"])
            return True
        except Exception as e:
            print(f"❌ Erro ao instalar dependências: {e}")
            print("🔧 Tentativa alternativa sem dependências externas...")
            return False

# Verificar se pode usar FastAPI
USE_FASTAPI = ensure_dependencies()

if USE_FASTAPI:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, JSONResponse
    from pydantic import BaseModel
    import uvicorn

# Configurações
DB_FILE = "whatsflow.db"
PORT = 8090

# HTML da aplicação (CSS puro, sem frameworks)
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsFlow Zero-Deps</title>
    <style>
        /* Reset básico */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            min-height: 100vh;
            color: #1f2937;
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        /* Header */
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        
        /* Navigation */
        .nav {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .nav-btn {
            background: rgba(255,255,255,0.9);
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        .nav-btn:hover { background: white; transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .nav-btn.active { background: white; color: #6366f1; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        /* Status */
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 500;
            font-size: 14px;
        }
        .status-connected { background: #d1fae5; color: #065f46; }
        .status-disconnected { background: #fef2f2; color: #991b1b; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; }
        .status-connected .status-dot { background: #10b981; }
        .status-disconnected .status-dot { background: #ef4444; }
        
        /* Stats */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            text-align: center;
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }
        .stat-number { font-size: 2rem; font-weight: bold; color: #6366f1; margin-bottom: 5px; }
        .stat-label { color: #6b7280; font-size: 14px; }
        
        /* Instances */
        .instances-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .instance-card {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            background: white;
            transition: all 0.3s ease;
        }
        .instance-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        
        .instance-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        .instance-name { font-size: 1.2rem; font-weight: 600; color: #1f2937; margin-bottom: 5px; }
        .instance-id { font-size: 12px; color: #6b7280; font-family: monospace; }
        
        .instance-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }
        .instance-stat {
            text-align: center;
            padding: 15px;
            background: #f9fafb;
            border-radius: 8px;
        }
        .instance-stat-number { font-size: 1.5rem; font-weight: bold; color: #6366f1; }
        .instance-stat-label { font-size: 12px; color: #6b7280; margin-top: 5px; }
        
        .instance-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        /* Buttons */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            font-size: 14px;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        .btn-primary { background: #6366f1; color: white; }
        .btn-success { background: #10b981; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .btn-secondary { background: #6b7280; color: white; }
        .btn:hover { transform: translateY(-1px); opacity: 0.9; }
        .btn:active { transform: translateY(0); }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal.show { display: flex; }
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 16px;
            width: 90%;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .modal-title { font-size: 1.3rem; font-weight: 600; color: #1f2937; }
        .close-btn { background: none; border: none; font-size: 24px; cursor: pointer; color: #6b7280; }
        .close-btn:hover { color: #374151; }
        
        /* Forms */
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; margin-bottom: 8px; font-weight: 500; color: #374151; }
        .form-input {
            width: 100%;
            padding: 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        .form-input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); }
        .form-help { font-size: 12px; color: #6b7280; margin-top: 5px; }
        
        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6b7280;
        }
        .empty-icon { font-size: 4rem; margin-bottom: 20px; }
        .empty-title { font-size: 1.5rem; font-weight: 600; color: #1f2937; margin-bottom: 10px; }
        .empty-description { margin-bottom: 30px; line-height: 1.6; }
        
        /* QR Code */
        .qr-section { text-align: center; padding: 20px; }
        .qr-instructions {
            text-align: left;
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #e5e7eb;
        }
        .qr-instructions h4 { color: #1f2937; margin-bottom: 15px; }
        .qr-instructions ol { color: #6b7280; line-height: 1.6; }
        .qr-instructions li { margin-bottom: 8px; }
        .qr-code-container {
            background: white;
            padding: 20px;
            border-radius: 12px;
            display: inline-block;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        .qr-footer { margin-top: 20px; }
        .qr-demo-note { color: #f59e0b; font-weight: 500; }
        
        /* Loading */
        .loading { text-align: center; padding: 40px; color: #6b7280; }
        .loading-spinner { font-size: 2rem; margin-bottom: 15px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        
        /* Responsive */
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .header h1 { font-size: 2rem; }
            .nav { justify-content: center; }
            .stats-grid { grid-template-columns: 1fr; }
            .instances-grid { grid-template-columns: 1fr; }
            .instance-actions { flex-direction: column; }
            .modal-content { margin: 20px; width: calc(100% - 40px); }
        }
        
        .section { display: none; }
        .section.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 WhatsFlow Zero-Deps</h1>
            <p>Sistema de Automação WhatsApp sem complicações</p>
        </div>
        
        <nav class="nav">
            <button class="nav-btn active" onclick="showSection('dashboard')">📊 Dashboard</button>
            <button class="nav-btn" onclick="showSection('instances')">📱 Instâncias</button>
            <button class="nav-btn" onclick="showSection('messages')">💬 Mensagens</button>
            <button class="nav-btn" onclick="showSection('macros')">🎯 Macros</button>
        </nav>
        
        <!-- Dashboard Section -->
        <div id="dashboard" class="section active">
            <div class="card">
                <h2>🔗 Status da Conexão</h2>
                <div class="status-indicator status-disconnected">
                    <div class="status-dot"></div>
                    <span>WhatsApp não conectado</span>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Estatísticas do Sistema</h2>
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
        
        <!-- Instances Section -->
        <div id="instances" class="section">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>📱 Instâncias WhatsApp</h2>
                    <button class="btn btn-primary" onclick="showCreateModal()">➕ Nova Instância</button>
                </div>
                <div id="instances-container" class="instances-grid">
                    <div class="loading">
                        <div class="loading-spinner">🔄</div>
                        <p>Carregando instâncias...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Messages Section -->
        <div id="messages" class="section">
            <div class="card">
                <h2>💬 Central de Mensagens</h2>
                <div class="empty-state">
                    <div class="empty-icon">💬</div>
                    <div class="empty-title">Central de Mensagens</div>
                    <div class="empty-description">Esta funcionalidade será implementada em breve. Aqui você poderá gerenciar todas as conversas do WhatsApp.</div>
                </div>
            </div>
        </div>
        
        <!-- Macros Section -->
        <div id="macros" class="section">
            <div class="card">
                <h2>🎯 Macros e Automações</h2>
                <div class="empty-state">
                    <div class="empty-icon">🎯</div>
                    <div class="empty-title">Sistema de Macros</div>
                    <div class="empty-description">Aqui você poderá criar automações e macros para responder automaticamente suas mensagens do WhatsApp.</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Create Instance Modal -->
    <div id="createModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">➕ Nova Instância WhatsApp</div>
                <button class="close-btn" onclick="hideCreateModal()">&times;</button>
            </div>
            <form onsubmit="createInstance(event)">
                <div class="form-group">
                    <label class="form-label">📝 Nome da Instância</label>
                    <input type="text" id="instanceName" class="form-input" 
                           placeholder="Ex: WhatsApp Vendas, WhatsApp Suporte..." 
                           required maxlength="50">
                    <div class="form-help">Este nome aparecerá na lista de instâncias e relatórios</div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="button" class="btn btn-secondary" onclick="hideCreateModal()">❌ Cancelar</button>
                    <button type="submit" class="btn btn-success" style="flex: 1;">✅ Criar Instância</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- QR Code Modal -->
    <div id="qrModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">📱 Conectar WhatsApp</div>
                <button class="close-btn" onclick="hideQRModal()">&times;</button>
            </div>
            <div class="qr-section">
                <div class="qr-instructions">
                    <h4>📲 Como conectar seu WhatsApp:</h4>
                    <ol>
                        <li>Abra o <strong>WhatsApp</strong> no seu celular</li>
                        <li>Toque em <strong>Configurações ⚙️</strong></li>
                        <li>Toque em <strong>Aparelhos conectados</strong></li>
                        <li>Toque em <strong>Conectar um aparelho</strong></li>
                        <li><strong>Escaneie o QR Code</strong> abaixo</li>
                    </ol>
                </div>
                
                <div class="qr-code-container">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=whatsflow-zero-deps-demo" 
                         alt="QR Code WhatsApp" style="border-radius: 8px;">
                </div>
                
                <div class="qr-footer">
                    <p class="qr-demo-note">🚧 Modo demonstração - QR Code simulado para testes</p>
                </div>
                
                <div style="margin-top: 30px; text-align: center;">
                    <button class="btn btn-danger" onclick="hideQRModal()">🚫 Fechar</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let instances = [];
        let currentInstanceId = null;

        // Navigation
        function showSection(sectionName) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Remove active class from all nav buttons
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected section
            document.getElementById(sectionName).classList.add('active');
            event.target.classList.add('active');
            
            // Load data if needed
            if (sectionName === 'instances') {
                loadInstances();
            } else if (sectionName === 'dashboard') {
                loadStats();
            }
        }

        // Modal functions
        function showCreateModal() {
            document.getElementById('createModal').classList.add('show');
        }

        function hideCreateModal() {
            document.getElementById('createModal').classList.remove('show');
            document.getElementById('instanceName').value = '';
        }

        function showQRModal(instanceId) {
            currentInstanceId = instanceId;
            document.getElementById('qrModal').classList.add('show');
            
            // Simulate connection after 3 seconds
            setTimeout(() => {
                hideQRModal();
                alert('✅ WhatsApp conectado com sucesso! (modo demonstração)');
                loadInstances();
            }, 3000);
        }

        function hideQRModal() {
            document.getElementById('qrModal').classList.remove('show');
            currentInstanceId = null;
        }

        // API functions
        async function loadInstances() {
            try {
                const response = await fetch('/api/instances');
                if (response.ok) {
                    instances = await response.json();
                    renderInstances();
                } else {
                    throw new Error('Failed to load instances');
                }
            } catch (error) {
                console.error('Error loading instances:', error);
                document.getElementById('instances-container').innerHTML = `
                    <div class="empty-state" style="grid-column: 1 / -1;">
                        <div class="empty-icon">❌</div>
                        <div class="empty-title">Erro ao carregar</div>
                        <div class="empty-description">Não foi possível carregar as instâncias. Verifique se o servidor está funcionando.</div>
                    </div>
                `;
            }
        }

        async function createInstance(event) {
            event.preventDefault();
            const name = document.getElementById('instanceName').value.trim();
            
            if (!name) return;
            
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
                    throw new Error('Failed to create instance');
                }
            } catch (error) {
                console.error('Error creating instance:', error);
                alert('❌ Erro ao criar instância. Tente novamente.');
            }
        }

        async function deleteInstance(instanceId, instanceName) {
            if (!confirm(`Tem certeza que deseja excluir a instância "${instanceName}"?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/instances/${instanceId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    loadInstances();
                    alert(`✅ Instância "${instanceName}" excluída com sucesso!`);
                } else {
                    throw new Error('Failed to delete instance');
                }
            } catch (error) {
                console.error('Error deleting instance:', error);
                alert('❌ Erro ao excluir instância. Tente novamente.');
            }
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                if (response.ok) {
                    const stats = await response.json();
                    document.getElementById('contacts-count').textContent = stats.contacts_count || 0;
                    document.getElementById('conversations-count').textContent = stats.conversations_count || 0;
                    document.getElementById('messages-count').textContent = stats.messages_count || 0;
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        // Render functions
        function renderInstances() {
            const container = document.getElementById('instances-container');
            
            if (!instances || instances.length === 0) {
                container.innerHTML = `
                    <div class="empty-state" style="grid-column: 1 / -1;">
                        <div class="empty-icon">📱</div>
                        <div class="empty-title">Nenhuma instância WhatsApp</div>
                        <div class="empty-description">Crie sua primeira instância para começar a gerenciar suas automações do WhatsApp.</div>
                        <button class="btn btn-primary" onclick="showCreateModal()">🚀 Criar Primeira Instância</button>
                    </div>
                `;
                return;
            }

            container.innerHTML = instances.map(instance => `
                <div class="instance-card">
                    <div class="instance-header">
                        <div>
                            <div class="instance-name">${escapeHtml(instance.name)}</div>
                            <div class="instance-id">ID: ${instance.id.substring(0, 8)}...</div>
                        </div>
                        <div class="status-indicator ${instance.connected ? 'status-connected' : 'status-disconnected'}">
                            <div class="status-dot"></div>
                            <span>${instance.connected ? 'Conectado' : 'Desconectado'}</span>
                        </div>
                    </div>
                    
                    <div class="instance-stats">
                        <div class="instance-stat">
                            <div class="instance-stat-number">${instance.contacts_count || 0}</div>
                            <div class="instance-stat-label">Contatos</div>
                        </div>
                        <div class="instance-stat">
                            <div class="instance-stat-number">${instance.messages_today || 0}</div>
                            <div class="instance-stat-label">Mensagens hoje</div>
                        </div>
                    </div>
                    
                    <div class="instance-actions">
                        ${!instance.connected ? 
                            `<button class="btn btn-success" onclick="showQRModal('${instance.id}')" style="flex: 1;">🔗 Conectar</button>` :
                            `<button class="btn btn-secondary" onclick="disconnectInstance('${instance.id}')" style="flex: 1;">⏸️ Desconectar</button>`
                        }
                        <button class="btn btn-danger" onclick="deleteInstance('${instance.id}', '${escapeHtml(instance.name)}')">🗑️ Excluir</button>
                    </div>
                </div>
            `).join('');
        }

        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            
            // Update stats every 30 seconds
            setInterval(loadStats, 30000);
            
            // Close modals when clicking outside
            document.querySelectorAll('.modal').forEach(modal => {
                modal.addEventListener('click', function(e) {
                    if (e.target === modal) {
                        modal.classList.remove('show');
                    }
                });
            });
        });
    </script>
</body>
</html>'''

# Database functions
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instances (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            connected INTEGER DEFAULT 0,
            contacts_count INTEGER DEFAULT 0,
            messages_today INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            instance_id TEXT,
            last_message TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            instance_id TEXT,
            contact_id TEXT,
            message TEXT NOT NULL,
            direction TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_demo_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM instances")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Add demo instances
    demo_instances = [
        {"id": str(uuid.uuid4()), "name": "WhatsApp Vendas", "connected": 0, "contacts_count": 3, "messages_today": 5},
        {"id": str(uuid.uuid4()), "name": "WhatsApp Suporte", "connected": 1, "contacts_count": 7, "messages_today": 12}
    ]
    
    current_time = datetime.now(timezone.utc).isoformat()
    
    for instance in demo_instances:
        cursor.execute("""
            INSERT INTO instances (id, name, connected, contacts_count, messages_today, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (instance["id"], instance["name"], instance["connected"], 
              instance["contacts_count"], instance["messages_today"], current_time))
    
    # Add demo contacts
    demo_contacts = [
        {"name": "João Silva", "phone": "+5511999999999"},
        {"name": "Maria Santos", "phone": "+5511888888888"},
        {"name": "Pedro Costa", "phone": "+5511777777777"}
    ]
    
    for contact in demo_contacts:
        cursor.execute("""
            INSERT INTO contacts (id, name, phone, instance_id, last_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), contact["name"], contact["phone"], 
              demo_instances[0]["id"], "Olá! Como posso ajudar?", current_time))
    
    conn.commit()
    conn.close()

# HTTP Request Handler for simple server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        elif self.path == '/api/instances':
            self.handle_get_instances()
        elif self.path == '/api/stats':
            self.handle_get_stats()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/instances':
            self.handle_create_instance()
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        if self.path.startswith('/api/instances/'):
            instance_id = self.path.split('/')[-1]
            self.handle_delete_instance(instance_id)
        else:
            self.send_error(404)
    
    def handle_get_instances(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM instances ORDER BY created_at DESC")
            instances = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            self.send_json_response(instances)
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_get_stats(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM contacts")
            contacts_count = cursor.fetchone()[0]
            
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            cursor.execute("SELECT COUNT(*) FROM messages WHERE created_at >= ?", (today,))
            messages_count = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                "contacts_count": contacts_count,
                "conversations_count": contacts_count,
                "messages_count": messages_count
            }
            
            self.send_json_response(stats)
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_create_instance(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = str(uuid.uuid4())
            created_at = datetime.now(timezone.utc).isoformat()
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO instances (id, name, created_at)
                VALUES (?, ?, ?)
            """, (instance_id, data['name'], created_at))
            conn.commit()
            conn.close()
            
            result = {"id": instance_id, "name": data['name'], "created_at": created_at}
            self.send_json_response(result)
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_delete_instance(self, instance_id):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM instances WHERE id = ?", (instance_id,))
            
            if cursor.rowcount == 0:
                conn.close()
                self.send_error(404, "Instance not found")
                return
            
            conn.commit()
            conn.close()
            
            self.send_json_response({"message": "Instance deleted successfully"})
        except Exception as e:
            self.send_error(500, str(e))
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # Disable default logging

# FastAPI version (if available)
if USE_FASTAPI:
    class InstanceCreate(BaseModel):
        name: str

    app = FastAPI(title="WhatsFlow Zero-Deps")

    @app.get("/", response_class=HTMLResponse)
    async def home():
        return HTML_CONTENT

    @app.get("/api/instances")
    async def get_instances():
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM instances ORDER BY created_at DESC")
        instances = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return instances

    @app.post("/api/instances")
    async def create_instance(instance: InstanceCreate):
        instance_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO instances (id, name, created_at)
            VALUES (?, ?, ?)
        """, (instance_id, instance.name, created_at))
        conn.commit()
        conn.close()
        
        return {"id": instance_id, "name": instance.name, "created_at": created_at}

    @app.delete("/api/instances/{instance_id}")
    async def delete_instance(instance_id: str):
        conn = sqlite3.connect(DB_FILE)
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
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM contacts")
        contacts_count = cursor.fetchone()[0]
        
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        cursor.execute("SELECT COUNT(*) FROM messages WHERE created_at >= ?", (today,))
        messages_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "contacts_count": contacts_count,
            "conversations_count": contacts_count,
            "messages_count": messages_count
        }

def main():
    print("🤖 WhatsFlow Zero-Deps - Versão SEM complicações")
    print("=" * 55)
    print()
    
    # Initialize database
    print("📁 Inicializando banco de dados SQLite...")
    init_db()
    add_demo_data()
    
    print("✅ WhatsFlow Zero-Deps configurado com sucesso!")
    print(f"🌐 Acesse: http://localhost:{PORT}")
    print(f"📁 Banco de dados: {os.path.abspath(DB_FILE)}")
    print()
    
    if USE_FASTAPI:
        print("🚀 Usando FastAPI (dependências instaladas)")
        print("   Para parar: Ctrl+C")
        print()
        try:
            uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
        except KeyboardInterrupt:
            print("\n👋 WhatsFlow Zero-Deps finalizado!")
    else:
        print("🚀 Usando servidor HTTP simples (sem dependências externas)")
        print("   Para parar: Ctrl+C")
        print()
        try:
            server = HTTPServer(('0.0.0.0', PORT), SimpleHandler)
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 WhatsFlow Zero-Deps finalizado!")

if __name__ == "__main__":
    main()