#!/bin/bash

# WhatsFlow - Instalação Ultra-Simples
# Sistema de Automação WhatsApp com Baileys
# Suporte para instalação LOCAL e PÚBLICA

set -e

echo "🤖 WHATSFLOW - Instalação Ultra-Simples"
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

# Perguntar tipo de instalação
echo ""
echo "🚀 Tipo de instalação:"
echo "1) LOCAL (sem domínio público)"
echo "2) PÚBLICA (com domínio e SSL)"
echo ""
read -p "Escolha (1 ou 2): " install_type

if [[ "$install_type" == "2" ]]; then
    # Instalação pública
    read -p "📝 Digite seu domínio (ex: meusite.com): " domain
    read -p "📧 Digite seu email para SSL: " email
    
    # Instalar Nginx
    if ! command_exists nginx; then
        echo "📦 Instalando Nginx..."
        if command_exists apt-get; then
            sudo apt-get install -y nginx
        elif command_exists yum; then
            sudo yum install -y nginx
        elif command_exists brew; then
            brew install nginx
        fi
    fi
    
    # Instalar Certbot
    if ! command_exists certbot; then
        echo "📦 Instalando Certbot..."
        if command_exists apt-get; then
            sudo apt-get install -y certbot python3-certbot-nginx
        elif command_exists yum; then
            sudo yum install -y certbot python3-certbot-nginx
        elif command_exists brew; then
            brew install certbot
        fi
    fi
fi

# Instalar PM2 globalmente
if ! command_exists pm2; then
    echo "📦 Instalando PM2..."
    sudo npm install -g pm2 yarn
else
    echo "✅ PM2 já instalado"
fi

# Criar diretório de trabalho
INSTALL_DIR="$HOME/whatsflow"
echo "📁 Criando diretório: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Baixar arquivos do WhatsFlow (simulando download)
echo "⬇️ Baixando WhatsFlow..."
cat > package.json << 'EOF'
{
  "name": "whatsflow",
  "version": "1.0.0",
  "description": "Sistema de Automação WhatsApp",
  "scripts": {
    "install:all": "cd backend && pip install -r requirements.txt && cd ../frontend && yarn install && cd ../whatsapp-service && yarn install",
    "start": "pm2 start ecosystem.config.js",
    "stop": "pm2 stop ecosystem.config.js",
    "restart": "pm2 restart ecosystem.config.js",
    "logs": "pm2 logs"
  }
}
EOF

# Criar configuração PM2
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'whatsflow-backend',
      script: 'python',
      args: 'backend/server.py',
      cwd: '$INSTALL_DIR',
      env: {
        PORT: 8001,
        MONGO_URL: 'mongodb://localhost:27017',
        DB_NAME: 'whatsflow'
      }
    },
    {
      name: 'whatsflow-frontend',
      script: 'yarn',
      args: 'start',
      cwd: '$INSTALL_DIR/frontend',
      env: {
        PORT: 3000,
        REACT_APP_BACKEND_URL: '${install_type == "2" ? "https://$domain" : "http://localhost:8001"}'
      }
    },
    {
      name: 'whatsflow-whatsapp',
      script: 'node',
      args: 'server.js',
      cwd: '$INSTALL_DIR/whatsapp-service',
      env: {
        PORT: 3001
      }
    }
  ]
};
EOF

# Criar estrutura de diretórios
mkdir -p backend frontend whatsapp-service

# Backend básico
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
motor==3.3.2
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.25.2
EOF

cat > backend/server.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="WhatsFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "WhatsFlow API funcionando!"}

@app.get("/api/status")
async def status():
    return {"status": "ok", "message": "WhatsFlow rodando!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
EOF

# Frontend básico
cat > frontend/package.json << 'EOF'
{
  "name": "whatsflow-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF

mkdir -p frontend/src frontend/public

cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>WhatsFlow</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>
EOF

cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
EOF

cat > frontend/src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [status, setStatus] = useState('Carregando...');

  useEffect(() => {
    axios.get('/api/status')
      .then(response => setStatus(response.data.message))
      .catch(() => setStatus('Erro ao conectar'));
  }, []);

  return (
    <div style={{ 
      padding: '50px', 
      textAlign: 'center', 
      fontFamily: 'Arial',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
      color: 'white'
    }}>
      <h1>🤖 WhatsFlow</h1>
      <h2>Sistema de Automação WhatsApp</h2>
      <p>Status: {status}</p>
      <p>✅ Instalação concluída com sucesso!</p>
    </div>
  );
}

export default App;
EOF

# WhatsApp Service básico
cat > whatsapp-service/package.json << 'EOF'
{
  "name": "whatsflow-whatsapp",
  "version": "1.0.0",
  "dependencies": {
    "@whiskeysockets/baileys": "^6.5.0",
    "express": "^4.18.2",
    "qrcode-terminal": "^0.12.0"
  },
  "scripts": {
    "start": "node server.js"
  }
}
EOF

cat > whatsapp-service/server.js << 'EOF'
const express = require('express');
const app = express();

app.use(express.json());

app.get('/status', (req, res) => {
    res.json({ 
        status: 'ok', 
        message: 'WhatsApp Service funcionando!',
        connected: false,
        demo: true
    });
});

app.listen(3001, () => {
    console.log('🚀 WhatsApp Service rodando na porta 3001');
});
EOF

# Instalar dependências
echo "📦 Instalando dependências..."
npm run install:all

# Iniciar MongoDB
echo "🗄️ Iniciando MongoDB..."
if command_exists systemctl; then
    sudo systemctl start mongod
    sudo systemctl enable mongod
elif command_exists brew; then
    brew services start mongodb/brew/mongodb-community
fi

if [[ "$install_type" == "2" ]]; then
    # Configurar Nginx para instalação pública
    echo "🌐 Configurando Nginx..."
    sudo tee /etc/nginx/sites-available/whatsflow << EOF
server {
    listen 80;
    server_name $domain;

    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/whatsflow /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx

    # Configurar SSL
    echo "🔒 Configurando SSL..."
    sudo certbot --nginx -d "$domain" --email "$email" --agree-tos --non-interactive
fi

# Iniciar aplicação
echo "🚀 Iniciando WhatsFlow..."
npm start

# Configurar PM2 para iniciar automaticamente
pm2 save
pm2 startup

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA!"
echo "==============================================="
if [[ "$install_type" == "2" ]]; then
    echo "🌐 Acesse: https://$domain"
else
    echo "🏠 Acesse: http://localhost:3000"
fi
echo ""
echo "📋 Comandos úteis:"
echo "  npm start     - Iniciar aplicação"
echo "  npm stop      - Parar aplicação"
echo "  npm restart   - Reiniciar aplicação"
echo "  npm run logs  - Ver logs"
echo ""
echo "📁 Diretório: $INSTALL_DIR"
echo "✅ WhatsFlow está rodando!"