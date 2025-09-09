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