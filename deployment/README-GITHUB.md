# 🚀 WhatsFlow - Sistema de Automação WhatsApp

Sistema completo de automação WhatsApp com dashboard profissional, multidispositivos e sistema de macros/webhooks.

## ✨ Funcionalidades

- 📱 **Múltiplos Dispositivos WhatsApp** - Gerencie vários WhatsApp em um só lugar
- 🎯 **Sistema de Macros** - Botões para disparar webhooks instantaneamente  
- 💬 **Chat em Tempo Real** - Interface profissional tipo WhatsApp Web
- 📊 **Dashboard Completo** - Estatísticas e métricas em tempo real
- 🔗 **Webhooks Robustos** - Sistema completo de integração
- 🏷️ **Gestão de Etiquetas** - Organize e segmente contatos
- ⚡ **Editor de Fluxos** - Crie automações drag-and-drop

## 🛠️ Tecnologias

- **Backend**: Python + FastAPI + MongoDB
- **Frontend**: React + TailwindCSS + React Flow
- **WhatsApp**: Baileys (Node.js)
- **Infraestrutura**: Nginx + PM2 + Let's Encrypt

## 🚀 Instalação Rápida

### Pré-requisitos
- Ubuntu 20.04+ / Debian 10+
- Domínio apontando para seu servidor
- Acesso root/sudo

### Instalação Automática (1 comando!)

```bash
# Baixar instalador
wget https://raw.githubusercontent.com/jocilejr/testes/main/install-whatsflow.sh

# Executar
chmod +x install-whatsflow.sh
./install-whatsflow.sh
```

O instalador vai solicitar:
- 🌐 **Seu domínio** (ex: whatsflow.seusite.com)
- 📧 **Seu email** (para SSL)

### O que o instalador faz automaticamente:
- ✅ Instala Node.js, Python, MongoDB, Nginx
- ✅ Baixa o projeto do GitHub
- ✅ Configura SSL automático
- ✅ Inicia todos os serviços
- ✅ Deixa funcionando em produção

## 📋 Após a Instalação

1. **Acesse**: `https://seudominio.com`
2. **Conecte WhatsApp**: 
   - Escaneie o QR Code com seu WhatsApp
   - Ou use o modo demo para testes
3. **Crie Macros**: 
   - Vá em Mensagens
   - Selecione um contato  
   - Use a sidebar direita para criar macros
4. **Pronto!** Sistema funcionando

## 📱 Como Conectar WhatsApp Real

1. Acesse seu WhatsFlow
2. Vá na seção **Mensagens**
3. Clique em **"Conectar WhatsApp"**
4. **Escaneie o QR Code** que aparece na tela
5. ✅ **WhatsApp conectado!**

## 🎯 Sistema de Macros

### Criar Macro
1. Selecione uma conversa
2. Na sidebar direita, clique **"Nova Macro"**
3. Preencha:
   - **Nome**: Ex: "Entrega - Amuleto"
   - **URL**: Seu webhook
   - **Descrição**: Opcional
4. **Salvar**

### Usar Macro
1. Selecione o contato
2. Clique no botão da macro
3. ✅ **Webhook disparado** com dados do lead!

### Dados Enviados no Webhook
```json
{
  "contact_name": "João Silva",
  "phone_number": "5511999999999",
  "device_id": "whatsapp_1", 
  "device_name": "WhatsApp 1",
  "jid": "5511999999999@s.whatsapp.net",
  "timestamp": "2024-01-01T12:00:00Z",
  "macro_name": "Entrega - Amuleto",
  "tags": ["cliente", "premium"]
}
```

## 🔧 Gerenciamento

### Comandos PM2
```bash
pm2 status          # Ver status dos serviços
pm2 logs            # Ver logs em tempo real  
pm2 restart all     # Reiniciar todos os serviços
pm2 stop all        # Parar todos os serviços
```

### Logs dos Serviços
```bash
pm2 logs whatsflow-backend    # Backend Python
pm2 logs whatsflow-frontend   # Frontend React  
pm2 logs whatsapp-service     # WhatsApp Service
```

### Logs do Sistema
```bash
sudo tail -f /var/log/nginx/error.log    # Nginx
sudo journalctl -u mongod                # MongoDB
```

## 📊 Estrutura do Projeto

```
whatsflow/
├── backend/              # FastAPI + Python
│   ├── server.py        # API principal
│   ├── requirements.txt # Dependências Python
│   └── .env            # Variáveis de ambiente
├── frontend/            # React
│   ├── src/
│   │   ├── App.js      # Componente principal
│   │   ├── App.css     # Estilos
│   │   └── components/ # Componentes React
│   ├── package.json    # Dependências Node
│   └── .env           # Variáveis de ambiente
├── whatsapp-service/   # Baileys + Node.js
│   ├── server.js      # Serviço WhatsApp
│   └── package.json   # Dependências
└── ecosystem.config.js # Configuração PM2
```

## 🔄 Atualizações

```bash
cd /var/www/whatsflow

# Parar serviços
pm2 stop all

# Atualizar código
git pull origin main

# Reinstalar dependências se necessário
cd backend && source venv/bin/activate && pip install -r requirements.txt && deactivate
cd ../frontend && npm install
cd ../whatsapp-service && npm install

# Reiniciar serviços
pm2 restart all
```

## 🆘 Troubleshooting

### Serviços não iniciam
```bash
# Verificar logs
pm2 logs

# Verificar portas
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8001  
sudo netstat -tulpn | grep :3001
```

### WhatsApp não conecta
```bash
# Verificar logs do WhatsApp Service
pm2 logs whatsapp-service

# Reiniciar apenas o WhatsApp
pm2 restart whatsapp-service
```

### Problemas com SSL
```bash
# Renovar certificado
sudo certbot renew

# Verificar configuração Nginx
sudo nginx -t
```

## 📈 Monitoramento

### Status dos Serviços
```bash
pm2 monit               # Interface de monitoramento
pm2 status             # Status resumido
```

### Métricas do Sistema
```bash
htop                   # CPU e Memória
df -h                  # Espaço em disco
sudo systemctl status mongod  # Status MongoDB
```

## 🔐 Segurança

- ✅ **SSL/HTTPS** configurado automaticamente
- ✅ **Firewall** recomendado (portas 80, 443)
- ✅ **MongoDB** local (não exposto)
- ✅ **Proxy reverso** Nginx

## 📞 Suporte

### Problemas Comuns
1. **Porta já em uso**: Verifique se não há outros serviços rodando
2. **Domínio não resolve**: Verifique DNS do domínio
3. **SSL falha**: Verifique se domínio aponta para o servidor

### Logs para Diagnóstico
```bash
# Todos os logs importantes
pm2 logs --lines 50
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u mongod --since "1 hour ago"
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🎉 Resultado Final

Após a instalação você terá:
- 🌐 **https://seudominio.com** funcionando
- 📱 **WhatsApp conectável** (QR Code real)
- 🎯 **Sistema de macros** ativo
- 📊 **Dashboard profissional**
- 🔗 **Webhooks funcionais**
- ⚡ **Multidispositivos**

---

**🚀 WhatsFlow - Automação WhatsApp Profissional**