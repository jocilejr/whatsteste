#!/bin/bash

# WhatsFlow Real - Instalador para Conexão WhatsApp REAL
# Python + Node.js + Baileys = WhatsApp verdadeiro

echo "🤖 WhatsFlow Real - Instalador para WhatsApp VERDADEIRO"
echo "======================================================="
echo ""
echo "🚀 Este instalador criará um sistema que conecta"
echo "   REALMENTE com seu WhatsApp via Baileys!"
echo ""
echo "✅ Python: Interface web e banco de dados"
echo "✅ Node.js: Serviço WhatsApp com Baileys"
echo "✅ QR Code: Real para conectar seu número"
echo "✅ Mensagens: Envio e recebimento reais"
echo ""

# Verificar Python
echo "🔍 Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION encontrado"
else
    echo "❌ Python 3 não encontrado!"
    echo "   Ubuntu: sudo apt install python3"
    exit 1
fi

# Verificar Node.js
echo "🔍 Verificando Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION encontrado"
else
    echo "❌ Node.js não encontrado!"
    echo ""
    echo "📦 Instalando Node.js..."
    if command -v apt-get &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    else
        echo "   Ubuntu: sudo apt install nodejs npm"
        echo "   macOS:  brew install node"
        exit 1
    fi
fi

# Verificar npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm $NPM_VERSION encontrado"
else
    echo "❌ npm não encontrado!"
    exit 1
fi

# Criar diretório
INSTALL_DIR="$HOME/whatsflow-real"
echo ""
echo "📁 Criando diretório de instalação..."
echo "   Diretório: $INSTALL_DIR"

if [ -d "$INSTALL_DIR" ]; then
    echo "🗑️ Removendo instalação anterior..."
    rm -rf "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo "⬇️ Criando WhatsFlow Real..."

# Copiar arquivo principal
cp /app/whatsflow-real.py ./whatsflow.py
chmod +x whatsflow.py

# Criar script de inicialização
cat > iniciar.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando WhatsFlow Real..."
echo "🌐 Interface: http://localhost:8888"
echo "📱 WhatsApp: Conexão real via Baileys"
echo "   Para parar: Ctrl+C"
echo ""
python3 whatsflow.py
EOF

chmod +x iniciar.sh

# Criar README
cat > README.md << 'EOF'
# 🤖 WhatsFlow Real

Sistema de Automação WhatsApp com conexão REAL

## 🚀 Iniciar

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

- ✅ Conexão WhatsApp REAL via Baileys
- ✅ QR Code real para conectar seu número
- ✅ Envio e recebimento de mensagens reais
- ✅ Interface web completa
- ✅ Banco SQLite local
- ✅ Python + Node.js

## 📱 Como usar

1. Execute `python3 whatsflow.py`
2. Acesse http://localhost:8888
3. Crie uma instância WhatsApp
4. Clique em "Conectar Real"
5. Escaneie o QR Code com seu WhatsApp
6. Pronto! WhatsApp conectado de verdade

## 🔧 Requisitos

- Python 3
- Node.js + npm
- Conexão com internet

---
WhatsFlow Real - WhatsApp verdadeiro! 🤖📱
EOF

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "===================================="
echo ""
echo "📁 Diretório: $INSTALL_DIR"
echo "🔧 Arquivos criados:"
echo "   ├── whatsflow.py    (aplicação principal)"
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
echo "   ✅ Conexão WhatsApp REAL via Baileys"
echo "   ✅ QR Code real para seu número"
echo "   ✅ Mensagens reais enviadas/recebidas"
echo "   ✅ Interface web completa"
echo "   ✅ Python backend + Node.js WhatsApp service"
echo "   ✅ Banco SQLite automático"
echo ""
echo "📱 Como conectar:"
echo "   1. Execute o sistema"
echo "   2. Crie uma instância"
echo "   3. Clique em 'Conectar Real'"
echo "   4. Escaneie QR Code com WhatsApp"
echo "   5. Pronto! Conectado de verdade"
echo ""
echo "🚀 Quer iniciar agora? (s/n)"
read -r start_now

if [[ "$start_now" =~ ^[Ss]$ ]]; then
    echo ""
    echo "🚀 Iniciando WhatsFlow Real..."
    echo "🌐 Acesse: http://localhost:8888"
    echo "📱 Prepare seu WhatsApp para escanear o QR Code!"
    echo ""
    cd "$INSTALL_DIR"
    python3 whatsflow.py
else
    echo ""
    echo "✅ WhatsFlow Real instalado com sucesso!"
    echo "📋 Para usar:"
    echo "   cd $INSTALL_DIR"
    echo "   python3 whatsflow.py"
    echo ""
    echo "🌐 Depois acesse: http://localhost:8888"
    echo "📱 E conecte seu WhatsApp REAL!"
fi