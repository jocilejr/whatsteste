# 🤖 WhatsFlow Local - Ultra-Simples

**Sistema de Automação WhatsApp sem complicações!**

✅ **Sem MongoDB** - Usa SQLite (não precisa instalar nada)  
✅ **Sem sudo** - Não precisa de privilégios de administrador  
✅ **Apenas Python** - Que já vem no Ubuntu  
✅ **Ultra-rápido** - Funciona em segundos  

## 🚀 Instalação Ultra-Rápida

### Método 1: Arquivo único (Recomendado)

```bash
# Baixar e executar
wget https://raw.githubusercontent.com/seu-repo/whatsflow-simple.py
python3 whatsflow-simple.py
```

### Método 2: Instalador automático

```bash
# Baixar instalador
wget https://raw.githubusercontent.com/seu-repo/instalar-whatsflow.sh
chmod +x instalar-whatsflow.sh
./instalar-whatsflow.sh
```

### Método 3: Copiando o código

1. Baixe o arquivo `whatsflow-simple.py`
2. Execute: `python3 whatsflow-simple.py`
3. Acesse: `http://localhost:8080`

## 📱 Como Usar

1. **Abra seu navegador** em `http://localhost:8080`
2. **Crie uma instância** WhatsApp na aba "Instâncias"
3. **Conecte seu WhatsApp** escaneando o QR Code
4. **Pronto!** Seu sistema está funcionando

## 🎯 Recursos Incluídos

- ✅ **Dashboard** com estatísticas em tempo real
- ✅ **Múltiplas Instâncias** WhatsApp
- ✅ **Sistema de QR Code** para conexão
- ✅ **Banco SQLite** para armazenar dados
- ✅ **Interface responsiva** e moderna
- ✅ **API REST** completa
- ✅ **Dados de demonstração** incluídos

## 📁 Estrutura dos Arquivos

```
whatsflow-local/
├── whatsflow.py      # Aplicação principal (tudo em um arquivo!)
├── whatsflow.db      # Banco SQLite (criado automaticamente)
└── iniciar.sh        # Script para iniciar
```

## 🔧 Comandos Úteis

```bash
# Iniciar WhatsFlow
python3 whatsflow.py

# Ou usando o script
./iniciar.sh

# Parar: Ctrl+C no terminal
```

## 🌐 URLs Importantes

- **Interface Principal**: http://localhost:8080
- **API de Instâncias**: http://localhost:8080/api/instances
- **API de Estatísticas**: http://localhost:8080/api/stats

## ❓ Problemas Comuns

### Python não encontrado:
```bash
sudo apt install python3 python3-pip
```

### Porta 8080 ocupada:
- Edite o arquivo `whatsflow.py`
- Mude `PORT = 8080` para `PORT = 8081`

### Permissões negadas:
```bash
chmod +x whatsflow.py
```

## 💡 Próximos Passos

Este é o WhatsFlow **Local** - uma versão simplificada para teste e desenvolvimento. Para recursos avançados como:

- Integração real com WhatsApp (Baileys)
- Sistema de macros completo
- Central de mensagens avançada
- Automações complexas

Considere usar a versão completa do WhatsFlow.

## 🎉 Exemplo de Uso

```bash
# 1. Baixar
wget https://raw.githubusercontent.com/seu-repo/whatsflow-simple.py

# 2. Executar
python3 whatsflow-simple.py

# 3. Abrir navegador
# http://localhost:8080

# 4. Criar instância
# Clique em "Instâncias" → "Nova Instância"

# 5. Conectar WhatsApp
# Clique em "Conectar" → Escaneie QR Code
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se o Python está instalado
2. Certifique-se que a porta 8080 está livre
3. Execute com `python3 -v whatsflow.py` para debug

---

**WhatsFlow Local** - Automação WhatsApp simplificada! 🤖📱