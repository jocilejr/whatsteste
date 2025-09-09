#!/bin/bash

# WhatsFlow Real - Instalador Ultra-Simples
# Sistema de Automação WhatsApp com Baileys + Python
# Instalação: bash instalar-real.sh

set -e

echo "🤖 WhatsFlow Real - Instalação Ultra-Simples"
echo "================================================="
echo "✅ Python + Node.js para WhatsApp REAL"
echo "✅ Conexão via QR Code verdadeira"
echo "✅ Mensagens reais enviadas/recebidas"
echo "✅ Central de contatos automática"
echo "✅ Interface web completa"
echo

# Verificar Python
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "📦 Para instalar:"
    echo "   Ubuntu/Debian: sudo apt install python3"
    echo "   CentOS/RHEL: sudo yum install python3"
    echo "   macOS: brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION encontrado"

# Verificar Node.js
echo "🔍 Verificando Node.js..."
NODE_AVAILABLE=true
if ! command -v node &> /dev/null; then
    echo "⚠️ Node.js não encontrado!"
    echo "📦 Para instalar Node.js:"
    echo "   Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo "   CentOS/RHEL: curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - && sudo yum install nodejs npm"
    echo "   macOS: brew install node"
    echo
    echo "🔧 Continuar sem Node.js? (WhatsApp ficará em modo demo)"
    read -p "Digite 's' para continuar ou 'n' para sair: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
    NODE_AVAILABLE=false
else
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo "✅ Node.js $NODE_VERSION encontrado"
    echo "✅ NPM $NPM_VERSION encontrado"
fi

# Baixar WhatsFlow Real se não existe
if [ ! -f "whatsflow-real.py" ]; then
    echo "📥 Baixando WhatsFlow Real..."
    curl -L -o whatsflow-real.py https://raw.githubusercontent.com/user/repo/main/whatsflow-real.py || {
        echo "⚠️ Não foi possível baixar - usando versão local"
    }
fi

if [ ! -f "whatsflow-real.py" ]; then
    echo "❌ whatsflow-real.py não encontrado!"
    echo "   Coloque o arquivo na pasta atual e tente novamente."
    exit 1
fi

# Tornar executável
chmod +x whatsflow-real.py

echo "🚀 Iniciando WhatsFlow Real..."
echo "   Interface: http://localhost:8889"
if [ "$NODE_AVAILABLE" = true ]; then
    echo "   WhatsApp Service: Será iniciado automaticamente"
    echo "   Status: Conexão WhatsApp REAL ativada"
else
    echo "   Status: Modo demonstração (Node.js não disponível)"
fi

echo
echo "📋 Como usar:"
echo "   1. Abra http://localhost:8888 no navegador"
if [ "$NODE_AVAILABLE" = true ]; then
    echo "   2. Vá na aba 'Instâncias'"
    echo "   3. Crie uma instância e clique 'Conectar Real'"
    echo "   4. Escaneie o QR Code com seu WhatsApp"
    echo "   5. Use as abas 'Contatos' e 'Mensagens'"
else
    echo "   2. Interface funcionará em modo demonstração"
    echo "   3. Instale Node.js para ativar WhatsApp real"
fi

echo
echo "⏳ Iniciando servidor..."
echo "   Para parar: Ctrl+C"
echo

# Iniciar WhatsFlow Real
python3 whatsflow-real.py