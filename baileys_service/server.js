const express = require('express');
const cors = require('cors');
const { DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const makeWASocket = require('@whiskeysockets/baileys').default;
const qrTerminal = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// Global state management
let instances = new Map(); // instanceId -> { sock, qr, connected, connecting, user }
let currentQR = null;
let qrUpdateInterval = null;

// QR Code auto-refresh every 20 seconds
const startQRRefresh = (instanceId) => {
    if (qrUpdateInterval) clearInterval(qrUpdateInterval);
    
    qrUpdateInterval = setInterval(() => {
        const instance = instances.get(instanceId);
        if (instance && !instance.connected && instance.connecting) {
            console.log('🔄 QR Code expirado, reconectando...');
            connectInstance(instanceId);
        }
    }, 20000); // 20 seconds
};

const stopQRRefresh = () => {
    if (qrUpdateInterval) {
        clearInterval(qrUpdateInterval);
        qrUpdateInterval = null;
    }
};

async function connectInstance(instanceId) {
    try {
        console.log(`🔄 Conectando instância: ${instanceId}`);
        
        // Create instance directory
        const authDir = `./auth_${instanceId}`;
        if (!fs.existsSync(authDir)) {
            fs.mkdirSync(authDir, { recursive: true });
        }
        
        const { state, saveCreds } = await useMultiFileAuthState(authDir);
        
        const sock = makeWASocket({
            auth: state,
            printQRInTerminal: true,
            browser: ['WhatsFlow', 'Chrome', '1.0.0'],
            connectTimeoutMs: 30000,
            defaultQueryTimeoutMs: 0,
            keepAliveIntervalMs: 10000,
            generateHighQualityLinkPreview: true
        });

        // Initialize instance
        instances.set(instanceId, {
            sock: sock,
            qr: null,
            connected: false,
            connecting: true,
            user: null
        });

        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            const instance = instances.get(instanceId);
            
            if (qr) {
                console.log(`📱 QR Code gerado para instância: ${instanceId}`);
                currentQR = qr;
                instance.qr = qr;
                qrTerminal.generate(qr, { small: true });
                startQRRefresh(instanceId);
            }
            
            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
                console.log(`🔌 Instância ${instanceId} desconectada. Reconectar?`, shouldReconnect);
                
                instance.connected = false;
                instance.connecting = false;
                instance.user = null;
                stopQRRefresh();
                
                if (shouldReconnect) {
                    setTimeout(() => connectInstance(instanceId), 5000);
                }
            } else if (connection === 'open') {
                console.log(`✅ Instância ${instanceId} conectada com sucesso!`);
                instance.connected = true;
                instance.connecting = false;
                instance.qr = null;
                currentQR = null;
                stopQRRefresh();
                
                // Get user info
                instance.user = {
                    id: sock.user.id,
                    name: sock.user.name || sock.user.id.split(':')[0],
                    profilePictureUrl: null
                };
                
                // Try to get profile picture
                try {
                    const profilePic = await sock.profilePictureUrl(sock.user.id, 'image');
                    instance.user.profilePictureUrl = profilePic;
                } catch (err) {
                    console.log('⚠️ Não foi possível obter foto do perfil');
                }
                
                // Import existing chats
                console.log('📥 Importando conversas existentes...');
                try {
                    const chats = await sock.getChats();
                    console.log(`📊 ${chats.length} conversas encontradas`);
                    
                    // Send chat data to Python backend
                    const fetch = (await import('node-fetch')).default;
                    await fetch('http://localhost:8889/api/chats/import', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            instanceId: instanceId,
                            chats: chats.slice(0, 50), // Limit to first 50 chats
                            user: instance.user
                        })
                    });
                } catch (err) {
                    console.log('⚠️ Erro ao importar conversas:', err.message);
                }
                
                // Send connected notification to Python backend
                setTimeout(async () => {
                    try {
                        const fetch = (await import('node-fetch')).default;
                        await fetch('http://localhost:8889/api/whatsapp/connected', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                instanceId: instanceId,
                                user: instance.user
                            })
                        });
                    } catch (err) {
                        console.log('⚠️ Não foi possível notificar backend:', err.message);
                    }
                }, 1000);
                
            } else if (connection === 'connecting') {
                console.log(`🔄 Conectando instância ${instanceId}...`);
                instance.connecting = true;
            }
        });

        sock.ev.on('creds.update', saveCreds);
        
        // Handle incoming messages
        sock.ev.on('messages.upsert', async (m) => {
            const messages = m.messages;
            
            for (const message of messages) {
                if (!message.key.fromMe && message.message) {
                    const from = message.key.remoteJid;
                    const messageText = message.message.conversation || 
                                      message.message.extendedTextMessage?.text || 
                                      'Mídia recebida';
                    
                    console.log(`📥 Nova mensagem na instância ${instanceId} de:`, from.split('@')[0], '- Texto:', messageText.substring(0, 50));
                    
                    // Send to Python backend
                    try {
                        const fetch = (await import('node-fetch')).default;
                        await fetch('http://localhost:8889/api/messages/receive', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                instanceId: instanceId,
                                from: from,
                                message: messageText,
                                timestamp: new Date().toISOString(),
                                messageId: message.key.id,
                                messageType: message.message.conversation ? 'text' : 'media'
                            })
                        });
                    } catch (err) {
                        console.log('❌ Erro ao enviar mensagem para backend:', err.message);
                    }
                }
            }
        });

    } catch (error) {
        console.error(`❌ Erro ao conectar instância ${instanceId}:`, error);
        const instance = instances.get(instanceId);
        if (instance) {
            instance.connecting = false;
            instance.connected = false;
        }
    }
}

// API Routes
app.get('/status/:instanceId?', (req, res) => {
    const { instanceId } = req.params;
    
    if (instanceId) {
        const instance = instances.get(instanceId);
        if (instance) {
            res.json({
                connected: instance.connected,
                connecting: instance.connecting,
                user: instance.user,
                instanceId: instanceId
            });
        } else {
            res.json({
                connected: false,
                connecting: false,
                user: null,
                instanceId: instanceId
            });
        }
    } else {
        // Return all instances
        const allInstances = {};
        for (const [id, instance] of instances) {
            allInstances[id] = {
                connected: instance.connected,
                connecting: instance.connecting,
                user: instance.user
            };
        }
        res.json(allInstances);
    }
});

app.get('/qr/:instanceId', (req, res) => {
    const { instanceId } = req.params;
    const instance = instances.get(instanceId);
    
    if (instance && instance.qr) {
        res.json({
            qr: instance.qr,
            connected: instance.connected,
            instanceId: instanceId
        });
    } else {
        res.json({
            qr: null,
            connected: instance ? instance.connected : false,
            instanceId: instanceId
        });
    }
});

app.post('/connect/:instanceId', (req, res) => {
    const { instanceId } = req.params;
    
    if (!instances.has(instanceId) || !instances.get(instanceId).connected) {
        connectInstance(instanceId || 'default');
        res.json({ success: true, message: `Iniciando conexão para instância ${instanceId}...` });
    } else {
        res.json({ success: false, message: 'Instância já conectada' });
    }
});

app.post('/disconnect/:instanceId', (req, res) => {
    const { instanceId } = req.params;
    const instance = instances.get(instanceId);
    
    if (instance && instance.sock) {
        instance.sock.logout();
        instances.delete(instanceId);
        stopQRRefresh();
        res.json({ success: true, message: `Instância ${instanceId} desconectada` });
    } else {
        res.json({ success: false, message: 'Instância não encontrada' });
    }
});

app.post('/send/:instanceId', async (req, res) => {
    const { instanceId } = req.params;
    const { to, message, type = 'text' } = req.body;
    
    const instance = instances.get(instanceId);
    if (!instance || !instance.connected || !instance.sock) {
        return res.status(400).json({ error: 'Instância não conectada' });
    }
    
    try {
        const jid = to.includes('@') ? to : `${to}@s.whatsapp.net`;
        
        if (type === 'text') {
            await instance.sock.sendMessage(jid, { text: message });
        } else if (type === 'image' && req.body.imageData) {
            // Handle image sending (base64)
            const buffer = Buffer.from(req.body.imageData, 'base64');
            await instance.sock.sendMessage(jid, { 
                image: buffer,
                caption: message || ''
            });
        }
        
        res.json({ success: true, instanceId: instanceId });
    } catch (error) {
        res.status(500).json({ error: error.message, instanceId: instanceId });
    }
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
    console.log(`🚀 Baileys service rodando na porta ${PORT}`);
    console.log('⏳ Aguardando comandos para conectar instâncias...');
});