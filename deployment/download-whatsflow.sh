#!/bin/bash

echo "📦 WhatsFlow - Download Completo do Projeto"
echo "==========================================="

# Criar diretório base
mkdir -p whatsflow-project
cd whatsflow-project

# Copiar arquivos principais do projeto
echo "📁 Criando estrutura de diretórios..."
mkdir -p backend frontend/src/components frontend/public whatsapp-service

echo "🐍 Criando Backend..."
# Backend - requirements.txt
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
motor==3.3.2
python-dotenv==1.0.0
pydantic==2.5.0
python-multipart==0.0.6
httpx==0.25.2
EOF

# Backend - .env
cat > backend/.env << 'EOF'
MONGO_URL=mongodb://localhost:27017/whatsflow
DB_NAME=whatsflow
CORS_ORIGINS=*
EOF

echo "📱 Criando WhatsApp Service..."
# WhatsApp Service - package.json
cat > whatsapp-service/package.json << 'EOF'
{
  "name": "whatsapp-service",
  "version": "1.0.0",
  "description": "WhatsApp service using Baileys",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "@whiskeysockets/baileys": "^6.5.0",
    "qrcode-terminal": "^0.12.0",
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "axios": "^1.6.0",
    "fs-extra": "^11.1.1"
  }
}
EOF

echo "⚛️ Criando Frontend..."
# Frontend - package.json
cat > frontend/package.json << 'EOF'
{
  "name": "whatsflow-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.4",
    "@testing-library/react": "^13.3.0",
    "@testing-library/user-event": "^13.5.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "reactflow": "^11.11.4",
    "@reactflow/controls": "^11.2.0",
    "@reactflow/background": "^11.3.0",
    "axios": "^1.6.0",
    "web-vitals": "^2.1.4"
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

# Frontend - .env
cat > frontend/.env << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
EOF

echo "✅ Estrutura básica criada!"
echo ""
echo "📋 Para instalar no servidor:"
echo "1. Copie a pasta 'whatsflow-project' para seu servidor"
echo "2. Siga o guia de instalação no README.md"
echo ""
echo "📁 Arquivos criados em: ./whatsflow-project/"