# 🚀 WhatsFlow - Guia de Instalação no Servidor

Sistema completo de automação WhatsApp com dashboard profissional, multidispositivos e sistema de macros/webhooks.

## 📋 Requisitos Mínimos

- **SO**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **RAM**: 2GB mínimo (4GB recomendado)
- **CPU**: 2 cores mínimo
- **Disco**: 10GB livres
- **Domínio**: Com acesso DNS
- **Portas**: 80, 443, 3000, 8001, 3001

## 🛠️ Instalação Rápida

### Passo 1: Download do Script
```bash
wget https://raw.githubusercontent.com/seu-repo/whatsflow/main/install.sh
chmod +x install.sh
```

### Passo 2: Executar Instalação
```bash
./install.sh
```

### Passo 3: Copiar Arquivos do Projeto
```bash
# Copie todos os arquivos do projeto para:
/var/www/whatsflow/

# Estrutura esperada:
/var/www/whatsflow/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── package.json
│   ├── src/
│   └── .env
├── whatsapp-service/
│   ├── server.js
│   └── package.json
└── setup-project.sh
```

### Passo 4: Configurar Projeto
```bash
cd /var/www/whatsflow
./setup-project.sh
```

## 🔧 Configuração Manual

### Backend (Python/FastAPI)
```bash
cd /var/www/whatsflow/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Criar .env
cat > .env <<EOF
MONGO_URL=mongodb://localhost:27017/whatsflow
DB_NAME=whatsflow
CORS_ORIGINS=https://seudominio.com
EOF
```

### Frontend (React)
```bash
cd /var/www/whatsflow/frontend
npm install

# Criar .env
cat > .env <<EOF
REACT_APP_BACKEND_URL=https://seudominio.com
EOF

npm run build
```

### WhatsApp Service (Node.js)
```bash
cd /var/www/whatsapp-service
npm install

# O serviço conectará automaticamente no FastAPI
```

## 🌐 Configuração Nginx

```nginx
server {
    listen 80;
    server_name seudominio.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔒 SSL com Let's Encrypt

```bash
sudo certbot --nginx -d seudominio.com
```

## ⚙️ Gerenciamento com PM2

```bash
# Instalar PM2
sudo npm install -g pm2

# Iniciar aplicações
pm2 start ecosystem.config.js

# Comandos úteis
pm2 status          # Ver status
pm2 logs            # Ver logs
pm2 restart all     # Reiniciar tudo
pm2 stop all        # Parar tudo
pm2 save            # Salvar configuração
pm2 startup         # Auto-start no boot
```

## 📱 Conectar WhatsApp

1. Acesse `https://seudominio.com`
2. Vá em **Mensagens**
3. Clique em **Conectar WhatsApp**
4. Escaneie o QR Code com seu WhatsApp
5. ✅ Pronto! WhatsApp conectado

## 🎯 Criar Macros

1. Selecione uma conversa
2. Na sidebar direita, clique **"Nova Macro"**
3. Preencha:
   - **Nome**: Ex: "Entrega - Amuleto"
   - **URL**: Seu webhook (ex: https://webhook.site/...)
   - **Descrição**: Opcional
4. Clique **Salvar**
5. ✅ Macro criada! Aparecerá como botão

## 🔧 Troubleshooting

### Logs
```bash
# Backend
pm2 logs whatsflow-backend

# Frontend  
pm2 logs whatsflow-frontend

# WhatsApp
pm2 logs whatsapp-service

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### Reiniciar Serviços
```bash
# Reiniciar tudo
pm2 restart all

# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar MongoDB
sudo systemctl restart mongod
```

### Verificar Portas
```bash
sudo netstat -tulpn | grep :3000  # Frontend
sudo netstat -tulpn | grep :8001  # Backend
sudo netstat -tulpn | grep :3001  # WhatsApp
```

## 📊 Monitoramento

```bash
# CPU e Memória
htop

# Espaço em disco
df -h

# Status dos serviços
pm2 monit
```

## 🔄 Atualizações

```bash
cd /var/www/whatsflow

# Parar aplicações
pm2 stop all

# Atualizar código
git pull origin main

# Reinstalar dependências se necessário
cd backend && pip install -r requirements.txt
cd ../frontend && npm install && npm run build
cd ../whatsapp-service && npm install

# Reiniciar
pm2 restart all
```

## 🆘 Suporte

- **Logs detalhados**: `pm2 logs`
- **Status sistema**: `pm2 status`
- **Testar APIs**: `curl http://localhost:8001/api/`
- **Verificar MongoDB**: `mongo whatsflow`

## 🎉 Sucesso!

Seu WhatsFlow está rodando em:
**https://seudominio.com**

Recursos disponíveis:
- ✅ Dashboard profissional
- ✅ Múltiplos dispositivos WhatsApp
- ✅ Sistema de macros/webhooks
- ✅ Chat em tempo real
- ✅ Gestão de contatos
- ✅ Interface responsiva