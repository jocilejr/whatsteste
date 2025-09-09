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
echo "⬇️ Baixando WhatsFlow Local..."
cat > whatsflow.py << 'WHATSFLOW_CODE'