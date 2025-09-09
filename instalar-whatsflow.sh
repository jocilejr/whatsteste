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
cat > whatsflow.py << 'WHATSFLOW_CODE'WHATSFLOW_CODE

# Tornar executável
chmod +x whatsflow.py

# Criar script de inicialização
cat > iniciar.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando WhatsFlow Local..."
python3 whatsflow.py
EOF

chmod +x iniciar.sh

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA!"
echo "========================"
echo "📁 Diretório: $INSTALL_DIR"
echo "🌐 Para iniciar:"
echo "   cd $INSTALL_DIR"
echo "   ./iniciar.sh"
echo ""
echo "📱 Acesse depois: http://localhost:8080"
echo ""
echo "✅ WhatsFlow Local pronto para uso!"
echo ""
echo "🚀 Quer iniciar agora? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "🚀 Iniciando WhatsFlow Local..."
    cd "$INSTALL_DIR"
    python3 whatsflow.py
fi