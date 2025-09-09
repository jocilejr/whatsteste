#!/bin/bash

# WhatsFlow Zero-Deps - Instalador ULTRA-SIMPLES
# SEM MongoDB, SEM TailwindCSS, SEM complicações!

echo "🤖 WhatsFlow Zero-Deps - Instalador ULTRA-SIMPLES"
echo "================================================="
echo ""
echo "✅ SEM MongoDB (usa SQLite)"
echo "✅ SEM sudo necessário"
echo "✅ SEM TailwindCSS (CSS puro)"
echo "✅ SEM dependências complexas"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "   Para instalar: sudo apt install python3 python3-pip"
    echo ""
    echo "🔧 Quer continuar mesmo assim? (s/n)"
    read -r continue_anyway
    if [[ ! "$continue_anyway" =~ ^[Ss]$ ]]; then
        exit 1
    fi
else
    echo "✅ Python encontrado: $(python3 --version)"
fi

# Criar diretório
INSTALL_DIR="$HOME/whatsflow-zero-deps"
echo "📁 Criando diretório: $INSTALL_DIR"
rm -rf "$INSTALL_DIR" 2>/dev/null
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Baixar WhatsFlow Zero-Deps (código embutido)
echo "⬇️ Criando WhatsFlow Zero-Deps..."

cat > whatsflow.py << 'EOF'
#!/usr/bin/env python3
"""
WhatsFlow Zero-Deps - Versão SEM dependências externas
Sistema de Automação WhatsApp com ZERO complicações

Requisitos: APENAS Python 3 (nada mais!)
Instalação: python3 whatsflow.py
Acesso: http://localhost:8090
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
import subprocess
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            min-height: 100vh;
            color: #1f2937;
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        
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
        }
        .nav-btn:hover { background: white; transform: translateY(-2px); }
        .nav-btn.active { background: white; color: #6366f1; }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 500;
        }
        .status-connected { background: #d1fae5; color: #065f46; }
        .status-disconnected { background: #fef2f2; color: #991b1b; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; }
        .status-connected .status-dot { background: #10b981; }
        .status-disconnected .status-dot { background: #ef4444; }
        
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
        }
        .stat-number { font-size: 2rem; font-weight: bold; color: #6366f1; }
        .stat-label { color: #6b7280; margin-top: 5px; }
        
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
        .btn-primary { background: #6366f1; color: white; }
        .btn-success { background: #10b981; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .btn:hover { transform: translateY(-1px); opacity: 0.9; }
        
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
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .close-btn { background: none; border: none; font-size: 24px; cursor: pointer; }
        
        .form-group { margin-bottom: 20px; }
        .form-label { display: block; margin-bottom: 8px; font-weight: 500; }
        .form-input {
            width: 100%;
            padding: 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 16px;
        }
        .form-input:focus { outline: none; border-color: #6366f1; }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6b7280;
        }
        .empty-icon { font-size: 4rem; margin-bottom: 20px; }
        .empty-title { font-size: 1.5rem; font-weight: 600; color: #1f2937; margin-bottom: 10px; }
        
        .section { display: none; }
        .section.active { display: block; }
        
        .loading { text-align: center; padding: 40px; }
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
        </nav>
        
        <div id="dashboard" class="section active">
            <div class="card">
                <h2>🔗 Status da Conexão</h2>
                <div class="status-indicator status-disconnected">
                    <div class="status-dot"></div>
                    <span>WhatsApp não conectado</span>
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
        
        <div id="instances" class="section">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>📱 Instâncias WhatsApp</h2>
                    <button class="btn btn-primary" onclick="showCreateModal()">➕ Nova Instância</button>
                </div>
                <div id="instances-container" class="instances-grid">
                    <div class="loading">Carregando instâncias...</div>
                </div>
            </div>
        </div>
        
        <div id="messages" class="section">
            <div class="card">
                <h2>💬 Central de Mensagens</h2>
                <div class="empty-state">
                    <div class="empty-icon">💬</div>
                    <div class="empty-title">Central de Mensagens</div>
                    <p>Esta funcionalidade será implementada em breve.</p>
                </div>
            </div>
        </div>
    </div>
    
    <div id="createModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>➕ Nova Instância WhatsApp</h3>
                <button class="close-btn" onclick="hideCreateModal()">&times;</button>
            </div>
            <form onsubmit="createInstance(event)">
                <div class="form-group">
                    <label class="form-label">Nome da Instância</label>
                    <input type="text" id="instanceName" class="form-input" 
                           placeholder="Ex: WhatsApp Vendas" required>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="button" class="btn" onclick="hideCreateModal()">Cancelar</button>
                    <button type="submit" class="btn btn-success" style="flex: 1;">Criar</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let instances = [];

        function showSection(sectionName) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(sectionName).classList.add('active');
            event.target.classList.add('active');
            
            if (sectionName === 'instances') loadInstances();
            if (sectionName === 'dashboard') loadStats();
        }

        function showCreateModal() {
            document.getElementById('createModal').classList.add('show');
        }

        function hideCreateModal() {
            document.getElementById('createModal').classList.remove('show');
            document.getElementById('instanceName').value = '';
        }

        async function loadInstances() {
            try {
                const response = await fetch('/api/instances');
                instances = await response.json();
                renderInstances();
            } catch (error) {
                document.getElementById('instances-container').innerHTML = 
                    '<div class="empty-state"><h3>Erro ao carregar</h3></div>';
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
                    alert('✅ Instância criada com sucesso!');
                }
            } catch (error) {
                alert('❌ Erro ao criar instância');
            }
        }

        async function deleteInstance(instanceId) {
            if (!confirm('Excluir instância?')) return;
            
            try {
                const response = await fetch(`/api/instances/${instanceId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    loadInstances();
                    alert('✅ Instância excluída!');
                }
            } catch (error) {
                alert('❌ Erro ao excluir');
            }
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('contacts-count').textContent = stats.contacts_count || 0;
                document.getElementById('conversations-count').textContent = stats.conversations_count || 0;
                document.getElementById('messages-count').textContent = stats.messages_count || 0;
            } catch (error) {
                console.error('Error loading stats');
            }
        }

        function renderInstances() {
            const container = document.getElementById('instances-container');
            
            if (!instances || instances.length === 0) {
                container.innerHTML = `
                    <div class="empty-state" style="grid-column: 1 / -1;">
                        <div class="empty-icon">📱</div>
                        <div class="empty-title">Nenhuma instância WhatsApp</div>
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
                            <div class="status-dot"></div>
                            <span>${instance.connected ? 'Conectado' : 'Desconectado'}</span>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                        <div style="text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #6366f1;">${instance.contacts_count || 0}</div>
                            <div style="font-size: 12px; color: #6b7280;">Contatos</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #6366f1;">${instance.messages_today || 0}</div>
                            <div style="font-size: 12px; color: #6b7280;">Mensagens hoje</div>
                        </div>
                    </div>
                    
                    <div class="instance-actions">
                        <button class="btn btn-success" style="flex: 1;">🔗 Conectar</button>
                        <button class="btn btn-danger" onclick="deleteInstance('${instance.id}')">🗑️ Excluir</button>
                    </div>
                </div>
            `).join('');
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            setInterval(loadStats, 30000);
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
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_demo_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM instances")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
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
    
    for i in range(10):
        cursor.execute("""
            INSERT INTO contacts (id, name, phone, created_at)
            VALUES (?, ?, ?, ?)
        """, (str(uuid.uuid4()), f"Contato {i+1}", f"+5511999{i:06d}", current_time))
        
        cursor.execute("""
            INSERT INTO messages (id, message, created_at)
            VALUES (?, ?, ?)
        """, (str(uuid.uuid4()), f"Mensagem exemplo {i+1}", current_time))
    
    conn.commit()
    conn.close()

# Simple HTTP Server
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
            
            cursor.execute("SELECT COUNT(*) FROM messages")
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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

def main():
    print("🤖 WhatsFlow Zero-Deps - SEM complicações")
    print("=" * 45)
    
    init_db()
    add_demo_data()
    
    print("✅ WhatsFlow Zero-Deps pronto!")
    print(f"🌐 Acesse: http://localhost:{PORT}")
    print("🚀 Iniciando servidor HTTP simples...")
    print("   Para parar: Ctrl+C")
    print()
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), SimpleHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 WhatsFlow Zero-Deps finalizado!")

if __name__ == "__main__":
    main()
EOF

chmod +x whatsflow.py

# Criar script de inicialização
cat > iniciar.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando WhatsFlow Zero-Deps..."
echo "🌐 Acesse: http://localhost:8090"
echo ""
python3 whatsflow.py
EOF

chmod +x iniciar.sh

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "===================================="
echo ""
echo "📁 Diretório: $INSTALL_DIR"
echo "🌐 Para acessar: http://localhost:8090"
echo ""
echo "🚀 Como iniciar:"
echo "   cd $INSTALL_DIR"
echo "   ./iniciar.sh"
echo ""
echo "   OU diretamente:"
echo "   python3 whatsflow.py"
echo ""
echo "✅ Características da instalação:"
echo "   ✅ SEM sudo necessário"
echo "   ✅ SEM MongoDB (usa SQLite)"
echo "   ✅ SEM TailwindCSS (CSS puro)"
echo "   ✅ SEM dependências complexas"
echo "   ✅ Servidor HTTP simples integrado"
echo ""
echo "🚀 Quer iniciar agora? (s/n)"
read -r start_now

if [[ "$start_now" =~ ^[Ss]$ ]]; then
    echo ""
    echo "🚀 Iniciando WhatsFlow Zero-Deps..."
    echo "🌐 Acesse: http://localhost:8090"
    echo ""
    cd "$INSTALL_DIR"
    python3 whatsflow.py
else
    echo ""
    echo "✅ WhatsFlow Zero-Deps instalado com sucesso!"
    echo "📁 Para usar: cd $INSTALL_DIR && ./iniciar.sh"
fi