#!/bin/bash

echo "🚀 WhatsFlow - Configuração do Projeto"
echo "====================================="

# Verificar se estamos no diretório correto
if [ ! -d "/var/www/whatsflow" ]; then
    echo "❌ Execute este script em /var/www/whatsflow/"
    exit 1
fi

cd /var/www/whatsflow

# Configurar Backend
echo "🐍 Configurando Backend Python..."
cd backend

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cat > .env <<EOF
MONGO_URL=mongodb://localhost:27017/whatsflow
DB_NAME=whatsflow
CORS_ORIGINS=https://$(hostname -f),http://localhost:3000
EOF

echo "✅ Backend configurado!"

# Configurar Frontend
echo "⚛️ Configurando Frontend React..."
cd ../frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cat > .env <<EOF
REACT_APP_BACKEND_URL=https://$(hostname -f)
EOF

# Build do projeto
npm run build

echo "✅ Frontend configurado!"

# Configurar WhatsApp Service
echo "📱 Configurando WhatsApp Service..."
cd ../whatsapp-service

# Instalar dependências
npm install

echo "✅ WhatsApp Service configurado!"

# Configurar PM2 para produção
echo "⚙️ Instalando PM2..."
sudo npm install -g pm2

# Criar configuração PM2
cd /var/www/whatsflow
cat > ecosystem.config.js <<EOF
module.exports = {
  apps: [
    {
      name: 'whatsflow-backend',
      cwd: '/var/www/whatsflow/backend',
      script: 'venv/bin/python',
      args: '-m uvicorn server:app --host 0.0.0.0 --port 8001',
      env: {
        NODE_ENV: 'production',
        MONGO_URL: 'mongodb://localhost:27017/whatsflow',
        DB_NAME: 'whatsflow'
      }
    },
    {
      name: 'whatsflow-frontend',
      cwd: '/var/www/whatsflow/frontend',
      script: 'npm',
      args: 'start',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    },
    {
      name: 'whatsapp-service',
      cwd: '/var/www/whatsflow/whatsapp-service',
      script: 'server.js',
      env: {
        NODE_ENV: 'production',
        FASTAPI_URL: 'http://localhost:8001',
        PORT: 3001
      }
    }
  ]
};
EOF

# Iniciar aplicações
echo "🚀 Iniciando aplicações..."
pm2 start ecosystem.config.js
pm2 save
pm2 startup

echo ""
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo ""
echo "🌐 Acesse seu WhatsFlow em: https://$(hostname -f)"
echo ""
echo "🔧 Comandos úteis:"
echo "- Ver status: pm2 status"
echo "- Ver logs: pm2 logs"
echo "- Reiniciar: pm2 restart all"
echo "- Parar: pm2 stop all"
echo ""
echo "📱 Para conectar WhatsApp:"
echo "1. Acesse a seção Mensagens"
echo "2. Clique em 'Conectar WhatsApp'"
echo "3. Escaneie o QR Code com seu WhatsApp"