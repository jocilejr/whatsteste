#!/bin/bash

echo "🔍 VERIFICAÇÃO DA INSTALAÇÃO WHATSFLOW REAL"
echo "=============================================="

# Verificar se existe o arquivo principal
if [ ! -f "whatsflow-real.py" ]; then
    echo "❌ whatsflow-real.py não encontrado!"
    echo "   Baixe a versão mais recente do GitHub"
    exit 1
fi

echo "✅ whatsflow-real.py encontrado"

# Verificar hash do arquivo
HASH_ATUAL=$(md5sum whatsflow-real.py | cut -d' ' -f1)
HASH_ESPERADO="541a316de2da68a6cd3dd3d0934a44b4"

echo "📋 Hash do arquivo: $HASH_ATUAL"
echo "📋 Hash esperado:   $HASH_ESPERADO"

if [ "$HASH_ATUAL" = "$HASH_ESPERADO" ]; then
    echo "✅ Arquivo está atualizado com todas as correções"
    VERSAO_OK=true
else
    echo "❌ Arquivo está desatualizado ou diferente"
    echo "   Você precisa baixar a versão mais recente"
    VERSAO_OK=false
fi

# Verificar correções específicas
echo
echo "🔍 Verificando correções específicas:"

# 1. CSS Modal
if grep -q "z-index: 1001" whatsflow-real.py; then
    echo "✅ CSS Modal corrigido"
else
    echo "❌ CSS Modal não corrigido"
    VERSAO_OK=false
fi

# 2. Database queries
QUERIES_COUNT=$(grep -c "ORDER BY created_at" whatsflow-real.py)
if [ "$QUERIES_COUNT" -eq 5 ]; then
    echo "✅ Database queries corrigidas ($QUERIES_COUNT/5)"
else
    echo "❌ Database queries não corrigidas ($QUERIES_COUNT/5)"
    VERSAO_OK=false
fi

# 3. WAL mode
if grep -q "WAL mode" whatsflow-real.py; then
    echo "✅ WAL mode implementado"
else
    echo "❌ WAL mode não implementado"
    VERSAO_OK=false
fi

# Verificar database
echo
echo "🗄️ Verificando database:"
if [ -f "whatsflow.db" ]; then
    echo "✅ Database existe"
    
    # Verificar se precisa de migração
    if [ -f "migrate_database.py" ]; then
        echo "📦 Script de migração disponível"
        echo "   Execute: python3 migrate_database.py"
    fi
else
    echo "⚠️ Database não encontrado (será criado na primeira execução)"
fi

echo
if [ "$VERSAO_OK" = true ]; then
    echo "🎉 SUA INSTALAÇÃO ESTÁ CORRETA!"
    echo "   Todas as correções estão aplicadas"
    echo "   Execute: python3 whatsflow-real.py"
else
    echo "❌ SUA INSTALAÇÃO PRECISA SER ATUALIZADA"
    echo
    echo "🔧 Para corrigir:"
    echo "   1. Faça backup: cp whatsflow-real.py whatsflow-backup.py"
    echo "   2. Baixe a versão mais recente do GitHub"
    echo "   3. Execute a migração: python3 migrate_database.py"  
    echo "   4. Inicie o sistema: python3 whatsflow-real.py"
fi

echo
echo "📊 Informações do sistema:"
echo "   Arquivo: $(ls -lh whatsflow-real.py | awk '{print $5 " " $6 " " $7 " " $8}')"
echo "   Hash: $HASH_ATUAL"
echo "   Python: $(python3 --version 2>/dev/null || echo 'Não encontrado')"
echo "   Node.js: $(node --version 2>/dev/null || echo 'Não encontrado')"