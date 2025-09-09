#!/bin/bash

# WhatsFlow Pure - Instalador DEFINITIVO
# 100% Python puro - SEM npm, SEM MongoDB, SEM complicações!

echo "🤖 WhatsFlow Pure - Instalador DEFINITIVO"
echo "=========================================="
echo ""
echo "✅ 100% Python puro (bibliotecas built-in)"
echo "✅ Zero npm/Node.js"
echo "✅ Zero MongoDB (usa SQLite)"
echo "✅ Zero sudo necessário"
echo "✅ Zero TailwindCSS (CSS puro)"
echo "✅ Zero dependências externas"
echo ""

# Verificar Python
echo "🔍 Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION encontrado"
else
    echo "❌ Python 3 não encontrado!"
    echo ""
    echo "📦 Para instalar Python:"
    echo "   Ubuntu/Debian: sudo apt install python3"
    echo "   CentOS/RHEL:   sudo yum install python3"
    echo "   macOS:         brew install python3"
    echo ""
    echo "🔧 Continuar mesmo assim? (s/n)"
    read -r continue_anyway
    if [[ ! "$continue_anyway" =~ ^[Ss]$ ]]; then
        echo "❌ Instalação cancelada"
        exit 1
    fi
fi

# Criar diretório
INSTALL_DIR="$HOME/whatsflow-pure"
echo ""
echo "📁 Criando diretório de instalação..."
echo "   Diretório: $INSTALL_DIR"

# Remover instalação anterior se existir
if [ -d "$INSTALL_DIR" ]; then
    echo "🗑️ Removendo instalação anterior..."
    rm -rf "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "⬇️ Criando WhatsFlow Pure..."

# Criar arquivo Python completo
cat > whatsflow.py << 'EOF'
#!/usr/bin/env python3
"""
WhatsFlow Pure - Sistema de Automação WhatsApp
100% Python puro - apenas bibliotecas built-in
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configurações
DB_FILE = "whatsflow.db"
PORT = 8888

# HTML da aplicação completa
HTML_APP = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsFlow Pure</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            min-height: 100vh; color: #1f2937;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .subtitle { background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; 
                   display: inline-block; margin-top: 10px; font-size: 0.9rem; }
        
        .nav { display: flex; gap: 10px; margin-bottom: 30px; flex-wrap: wrap; justify-content: center; }
        .nav-btn { background: rgba(255,255,255,0.9); border: none; padding: 12px 20px; 
                  border-radius: 8px; cursor: pointer; font-weight: 500; transition: all 0.3s ease; }
        .nav-btn:hover { background: white; transform: translateY(-2px); }
        .nav-btn.active { background: white; color: #4f46e5; }
        
        .card { background: white; border-radius: 16px; padding: 25px; 
               box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px; }
        
        .status-indicator { display: inline-flex; align-items: center; gap: 8px; 
                           padding: 8px 16px; border-radius: 20px; font-weight: 500; }
        .status-disconnected { background: #fef2f2; color: #991b1b; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #ef4444; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                     gap: 20px; margin: 20px 0; }
        .stat-card { text-align: center; padding: 20px; background: #f8fafc; 
                    border-radius: 12px; border: 1px solid #e2e8f0; }
        .stat-number { font-size: 2rem; font-weight: bold; color: #4f46e5; margin-bottom: 5px; }
        .stat-label { color: #6b7280; font-size: 14px; }
        
        .instances-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .instance-card { border: 2px solid #e5e7eb; border-radius: 12px; padding: 20px; 
                        background: white; transition: all 0.3s ease; }
        .instance-card:hover { transform: translateY(-2px); border-color: #4f46e5; }
        
        .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; 
              font-weight: 500; transition: all 0.3s ease; }
        .btn-primary { background: #4f46e5; color: white; }
        .btn-success { background: #10b981; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .btn:hover { transform: translateY(-1px); opacity: 0.9; }
        
        .modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                background: rgba(0,0,0,0.5); z-index: 1000; align-items: center; justify-content: center; }
        .modal.show { display: flex; }
        .modal-content { background: white; padding: 30px; border-radius: 16px; 
                        width: 90%; max-width: 500px; }
        
        .form-input { width: 100%; padding: 12px; border: 2px solid #d1d5db; 
                     border-radius: 6px; font-size: 16px; }
        .form-input:focus { outline: none; border-color: #4f46e5; }
        
        .empty-state { text-align: center; padding: 60px 20px; color: #6b7280; }
        .empty-icon { font-size: 4rem; margin-bottom: 20px; opacity: 0.5; }
        .empty-title { font-size: 1.5rem; font-weight: 600; color: #1f2937; margin-bottom: 10px; }
        
        .section { display: none; }
        .section.active { display: block; }
        
        .success-message { background: #d1fae5; color: #065f46; padding: 15px; 
                          border-radius: 8px; margin: 20px 0; text-align: center; font-weight: 500; }
        
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .header h1 { font-size: 2rem; }
            .stats-grid, .instances-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 WhatsFlow Pure</h1>
            <p>Sistema de Automação WhatsApp - 100% Python Puro</p>
            <div class="subtitle">✅ Zero dependências • Zero npm • Zero complicações</div>
        </div>
        
        <nav class="nav">
            <button class="nav-btn active" onclick="showSection('dashboard')">📊 Dashboard</button>
            <button class="nav-btn" onclick="showSection('instances')">📱 Instâncias</button>
            <button class="nav-btn" onclick="showSection('info')">ℹ️ Info</button>
        </nav>
        
        <div id="dashboard" class="section active">
            <div class="card">
                <h2>🔗 Status do Sistema</h2>
                <div class="status-indicator status-disconnected">
                    <div class="status-dot"></div>
                    <span>WhatsApp em modo demonstração</span>
                </div>
                <div class="success-message">
                    ✅ WhatsFlow Pure funcionando sem dependências externas!
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Estatísticas</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="contacts-count">0</div>
                        <div class="stat-label">Contatos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="conversations-count">0</div>
                        <div class="stat-label">Conversas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="messages-count">0</div>
                        <div class="stat-label">Mensagens</div>
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
                    <div style="text-align: center; padding: 40px;">Carregando...</div>
                </div>
            </div>
        </div>
        
        <div id="info" class="section">
            <div class="card">
                <h2>ℹ️ WhatsFlow Pure</h2>
                <p><strong>🐍 Tecnologia:</strong> Python puro (bibliotecas built-in)</p>
                <p><strong>🗄️ Banco:</strong> SQLite local</p>
                <p><strong>🌐 Servidor:</strong> HTTP simples</p>
                <p><strong>🎨 Interface:</strong> HTML + CSS puro</p>
                <p><strong>📡 API:</strong> REST endpoints</p>
                <p><strong>🔧 Requisitos:</strong> Apenas Python 3</p>
            </div>
        </div>
    </div>
    
    <div id="createModal" class="modal">
        <div class="modal-content">
            <h3>➕ Nova Instância</h3>
            <form onsubmit="createInstance(event)">
                <div style="margin: 20px 0;">
                    <input type="text" id="instanceName" class="form-input" 
                           placeholder="Nome da instância" required>
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

        function showSection(name) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            event.target.classList.add('active');
            
            if (name === 'instances') loadInstances();
            if (name === 'dashboard') loadStats();
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
                    '<div class="empty-state"><div class="empty-icon">❌</div><div class="empty-title">Erro ao carregar</div></div>';
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
                    alert(`✅ Instância "${name}" criada!`);
                }
            } catch (error) {
                alert('❌ Erro ao criar instância');
            }
        }

        async function deleteInstance(id, name) {
            if (!confirm(`Excluir "${name}"?`)) return;
            
            try {
                const response = await fetch(`/api/instances/${id}`, { method: 'DELETE' });
                if (response.ok) {
                    loadInstances();
                    alert(`✅ "${name}" excluída!`);
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
                        <div class="empty-title">Nenhuma instância</div>
                        <p>Crie sua primeira instância WhatsApp</p>
                        <br>
                        <button class="btn btn-primary" onclick="showCreateModal()">🚀 Criar Primeira Instância</button>
                    </div>
                `;
                return;
            }

            container.innerHTML = instances.map(instance => `
                <div class="instance-card">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                        <div>
                            <h3>${instance.name}</h3>
                            <small>ID: ${instance.id.substring(0, 8)}...</small>
                        </div>
                        <div class="status-indicator status-disconnected">
                            <div class="status-dot"></div>
                            <span>Desconectado</span>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                        <div style="text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #4f46e5;">${instance.contacts_count || 0}</div>
                            <div style="font-size: 12px; color: #6b7280;">Contatos</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #4f46e5;">${instance.messages_today || 0}</div>
                            <div style="font-size: 12px; color: #6b7280;">Mensagens</div>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-success" style="flex: 1;">🔗 Conectar</button>
                        <button class="btn btn-danger" onclick="deleteInstance('${instance.id}', '${instance.name}')">🗑️ Excluir</button>
                    </div>
                </div>
            `).join('');
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            setInterval(loadStats, 30000);
            
            document.getElementById('createModal').addEventListener('click', function(e) {
                if (e.target === this) this.classList.remove('show');
            });
        });
    </script>
</body>
</html>'''

# Database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS instances (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, connected INTEGER DEFAULT 0,
        contacts_count INTEGER DEFAULT 0, messages_today INTEGER DEFAULT 0,
        created_at TEXT NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT NOT NULL,
        created_at TEXT NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY, message TEXT NOT NULL, created_at TEXT NOT NULL)''')
    
    conn.commit()
    conn.close()

def add_sample_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM instances")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Sample instances
    samples = [
        {"id": str(uuid.uuid4()), "name": "WhatsApp Vendas", "contacts_count": 5, "messages_today": 12},
        {"id": str(uuid.uuid4()), "name": "WhatsApp Suporte", "contacts_count": 8, "messages_today": 25}
    ]
    
    for sample in samples:
        cursor.execute("INSERT INTO instances (id, name, contacts_count, messages_today, created_at) VALUES (?, ?, ?, ?, ?)",
                      (sample["id"], sample["name"], sample["contacts_count"], sample["messages_today"], current_time))
    
    # Sample contacts and messages
    for i in range(13):
        cursor.execute("INSERT INTO contacts (id, name, phone, created_at) VALUES (?, ?, ?, ?)",
                      (str(uuid.uuid4()), f"Contato {i+1}", f"+5511{i:09d}", current_time))
        cursor.execute("INSERT INTO messages (id, message, created_at) VALUES (?, ?, ?)",
                      (str(uuid.uuid4()), f"Mensagem {i+1}", current_time))
    
    conn.commit()
    conn.close()

# HTTP Handler
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_APP.encode('utf-8'))
        elif self.path == '/api/instances':
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM instances ORDER BY created_at DESC")
            instances = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json(instances)
        elif self.path == '/api/stats':
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            contacts = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM messages")
            messages = cursor.fetchone()[0]
            conn.close()
            self.send_json({"contacts_count": contacts, "conversations_count": contacts, "messages_count": messages})
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/instances':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = str(uuid.uuid4())
            created_at = datetime.now(timezone.utc).isoformat()
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO instances (id, name, created_at) VALUES (?, ?, ?)",
                          (instance_id, data['name'], created_at))
            conn.commit()
            conn.close()
            
            self.send_json({"id": instance_id, "name": data['name'], "created_at": created_at})
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        if self.path.startswith('/api/instances/'):
            instance_id = self.path.split('/')[-1]
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM instances WHERE id = ?", (instance_id,))
            conn.commit()
            conn.close()
            self.send_json({"message": "Deleted"})
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

def main():
    print("🤖 WhatsFlow Pure - 100% Python")
    print("================================")
    print("📁 Inicializando...")
    init_db()
    add_sample_data()
    
    print(f"✅ Pronto! Acesse: http://localhost:{PORT}")
    print("🚀 Iniciando servidor...")
    print("   Para parar: Ctrl+C")
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), Handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Finalizado!")

if __name__ == "__main__":
    main()
EOF

chmod +x whatsflow.py

# Criar script de inicialização
cat > iniciar.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando WhatsFlow Pure..."
echo "🌐 Acesse: http://localhost:8888"
echo "   Para parar: Ctrl+C"
echo ""
python3 whatsflow.py
EOF

chmod +x iniciar.sh

# Criar README
cat > README.md << 'EOF'
# 🤖 WhatsFlow Pure

Sistema de Automação WhatsApp - 100% Python Puro

## ⚡ Iniciar

```bash
python3 whatsflow.py
```

**OU**

```bash
./iniciar.sh
```

## 🌐 Acessar

http://localhost:8888

## ✅ Características

- ✅ Zero dependências externas
- ✅ Zero npm/Node.js  
- ✅ Zero MongoDB
- ✅ Zero sudo
- ✅ Apenas Python 3

## 📱 Funcionalidades

- Dashboard com estatísticas
- Sistema de instâncias WhatsApp
- Interface moderna e responsiva
- API REST completa
- Banco SQLite automático

---
WhatsFlow Pure - Automação WhatsApp sem complicações! 🤖
EOF

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "===================================="
echo ""
echo "📁 Diretório: $INSTALL_DIR"
echo "🔧 Arquivos criados:"
echo "   ├── whatsflow.py    (aplicação completa)"
echo "   ├── iniciar.sh      (script para iniciar)"
echo "   └── README.md       (documentação)"
echo ""
echo "🚀 Como iniciar:"
echo "   cd $INSTALL_DIR"
echo "   python3 whatsflow.py"
echo ""
echo "   OU usando o script:"
echo "   ./iniciar.sh"
echo ""
echo "🌐 Depois acesse: http://localhost:8888"
echo ""
echo "✅ Características da instalação:"
echo "   ✅ 100% Python puro (bibliotecas built-in)"
echo "   ✅ Zero npm/Node.js"
echo "   ✅ Zero MongoDB (usa SQLite)"
echo "   ✅ Zero sudo necessário"
echo "   ✅ Zero TailwindCSS (CSS puro)"
echo "   ✅ Zero dependências externas"
echo "   ✅ Interface completa embutida"
echo "   ✅ API REST funcional"
echo "   ✅ Dados de exemplo incluídos"
echo ""
echo "🚀 Quer iniciar agora? (s/n)"
read -r start_now

if [[ "$start_now" =~ ^[Ss]$ ]]; then
    echo ""
    echo "🚀 Iniciando WhatsFlow Pure..."
    echo "🌐 Acesse: http://localhost:8888 no seu navegador"
    echo "   Para parar: Ctrl+C"
    echo ""
    cd "$INSTALL_DIR"
    python3 whatsflow.py
else
    echo ""
    echo "✅ WhatsFlow Pure instalado com sucesso!"
    echo "📋 Para usar:"
    echo "   cd $INSTALL_DIR"
    echo "   python3 whatsflow.py"
    echo ""
    echo "🌐 Depois acesse: http://localhost:8888"
fi