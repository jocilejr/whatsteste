const express = require('express');
const cors = require('cors');
const { DisconnectReason, useMultiFileAuthState, downloadMediaMessage, getAggregateVotesInPollMessage } = require('@whiskeysockets/baileys');
const makeWASocket = require('@whiskeysockets/baileys').default;
const qrTerminal = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

let instances = new Map();
let currentQR = null;
let qrUpdateInterval = null;

async function connectInstance(instanceId) {
    try {
        console.log(`🔄 Iniciando conexão para instância: ${instanceId}`);
        
        const authDir = `./auth_${instanceId}`;
        if (!fs.existsSync(authDir)) {
            fs.mkdirSync(authDir, { recursive: true });
        }
        
        const { state, saveCreds } = await useMultiFileAuthState(authDir);
        
        const sock = makeWASocket({
            auth: state,
            browser: ['WhatsFlow Professional', 'Desktop', '1.0.0'],
            connectTimeoutMs: 60000,
            defaultQueryTimeoutMs: 0,
            keepAliveIntervalMs: 30000,
            generateHighQualityLinkPreview: true,
            markOnlineOnConnect: true,
            syncFullHistory: true
        });

        instances.set(instanceId, {
            sock: sock,
            qr: null,
            connected: false,
            connecting: true,
            user: null,
            lastSeen: new Date()
        });

        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            const instance = instances.get(instanceId);
            
            if (qr) {
                console.log(`📱 Novo QR Code gerado para instância: ${instanceId}`);
                currentQR = qr;
                instance.qr = qr;
                
                try {
                    qrTerminal.generate(qr, { small: true });
                } catch (err) {
                    console.log('⚠️ QR Terminal não disponível:', err.message);
                }
            }
            
            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
                const reason = lastDisconnect?.error?.output?.statusCode || 'unknown';
                
                console.log(`🔌 Instância ${instanceId} desconectada. Razão: ${reason}`);
                
                instance.connected = false;
                instance.connecting = false;
                instance.user = null;
                
                if (shouldReconnect && reason !== DisconnectReason.loggedOut) {
                    console.log(`🔄 Reconectando ${instanceId} em 10 segundos`);
                    setTimeout(() => connectInstance(instanceId), 10000);
                }
                
            } else if (connection === 'open') {
                console.log(`✅ Instância ${instanceId} conectada com SUCESSO!`);
                instance.connected = true;
                instance.connecting = false;
                instance.qr = null;
                instance.lastSeen = new Date();
                currentQR = null;
                
                // Get user info
                instance.user = {
                    id: sock.user.id,
                    name: sock.user.name || sock.user.id.split(':')[0],
                    phone: sock.user.id.split(':')[0]
                };
                
                console.log(`👤 Usuário conectado: ${instance.user.name} (${instance.user.phone})`);
                
                // Wait and import chats with enhanced name extraction
                setTimeout(async () => {
                    try {
                        console.log('📥 Importando conversas com nomes reais...');
                        
                        const chats = await sock.getChats();
                        console.log(`📊 ${chats.length} conversas encontradas`);
                        
                        const enhancedChats = [];
                        
                        for (const chat of chats) {
                            if (chat.id && !chat.id.endsWith('@g.us')) { // Skip groups
                                let contactName = chat.name || chat.pushName || chat.notify;
                                let profilePicUrl = null;
                                
                                try {
                                    // Get contact from phone book
                                    const contactInfo = await sock.getContact(chat.id);
                                    if (contactInfo && contactInfo.name) {
                                        contactName = contactInfo.name;
                                    }
                                    
                                    // Try multiple methods to get the name
                                    if (!contactName || contactName.includes('@')) {
                                        // Try to get name from WhatsApp profile
                                        try {
                                            const profileInfo = await sock.getProfile(chat.id);
                                            if (profileInfo && profileInfo.name) {
                                                contactName = profileInfo.name;
                                            }
                                        } catch (e) {
                                            // Profile not accessible
                                        }
                                        
                                        // Try presence to get name
                                        if (!contactName || contactName.includes('@')) {
                                            const phone = chat.id.replace('@s.whatsapp.net', '').replace('@c.us', '');
                                            contactName = `+${phone}`;
                                        }
                                    }
                                    
                                    // Get profile picture
                                    try {
                                        profilePicUrl = await sock.profilePictureUrl(chat.id, 'image');
                                        console.log(`📸 Foto obtida para ${contactName}`);
                                    } catch (ppErr) {
                                        // No profile picture - that's ok
                                    }
                                    
                                } catch (err) {
                                    console.log(`⚠️ Erro ao processar contato ${chat.id}: ${err.message}`);
                                    const phone = chat.id.replace('@s.whatsapp.net', '').replace('@c.us', '');
                                    contactName = `+${phone}`;
                                }
                                
                                enhancedChats.push({
                                    ...chat,
                                    enhancedName: contactName,
                                    profilePicUrl: profilePicUrl
                                });
                                
                                console.log(`👤 Processado: ${contactName} - Foto: ${profilePicUrl ? '✅' : '❌'}`);
                            }
                        }
                        
                        console.log(`📊 ${enhancedChats.length} conversas processadas com nomes aprimorados`);
                        
                        // Send to backend in batches
                        const batchSize = 10;
                        for (let i = 0; i < enhancedChats.length; i += batchSize) {
                            const batch = enhancedChats.slice(i, i + batchSize);
                            
                            const fetch = (await import('node-fetch')).default;
                            await fetch('http://localhost:8889/api/chats/import', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    instanceId: instanceId,
                                    chats: batch,
                                    user: instance.user,
                                    batchNumber: Math.floor(i / batchSize) + 1,
                                    totalBatches: Math.ceil(enhancedChats.length / batchSize)
                                })
                            });
                            
                            console.log(`📦 Lote ${Math.floor(i / batchSize) + 1}/${Math.ceil(enhancedChats.length / batchSize)} enviado`);
                            await new Promise(resolve => setTimeout(resolve, 2000));
                        }
                        
                        console.log('✅ Importação de conversas com nomes reais concluída');
                        
                    } catch (err) {
                        console.log('⚠️ Erro ao importar conversas:', err.message);
                    }
                }, 3000);
                
                // Notify backend about connection
                setTimeout(async () => {
                    try {
                        const fetch = (await import('node-fetch')).default;
                        await fetch('http://localhost:8889/api/whatsapp/connected', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                instanceId: instanceId,
                                user: instance.user,
                                connectedAt: new Date().toISOString()
                            })
                        });
                        console.log('✅ Backend notificado sobre a conexão');
                    } catch (err) {
                        console.log('⚠️ Erro ao notificar backend:', err.message);
                    }
                }, 1000);
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
                    
                    console.log(`📥 Nova mensagem de: ${from.split('@')[0]} - ${messageText.substring(0, 50)}...`);
                    
                    // Send to backend
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
                        console.log(`❌ Erro ao enviar mensagem: ${err.message}`);
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
                instanceId: instanceId,
                lastSeen: instance.lastSeen
            });
        } else {
            res.json({
                connected: false,
                connecting: false,
                user: null,
                instanceId: instanceId,
                lastSeen: null
            });
        }
    } else {
        const allInstances = {};
        for (const [id, instance] of instances) {
            allInstances[id] = {
                connected: instance.connected,
                connecting: instance.connecting,
                user: instance.user,
                lastSeen: instance.lastSeen
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
            instanceId: instanceId,
            expiresIn: 60
        });
    } else {
        res.json({
            qr: null,
            connected: instance ? instance.connected : false,
            instanceId: instanceId,
            expiresIn: 0
        });
    }
});

app.post('/connect/:instanceId', (req, res) => {
    const { instanceId } = req.params;
    
    const instance = instances.get(instanceId);
    if (!instance || (!instance.connected && !instance.connecting)) {
        connectInstance(instanceId);
        res.json({ success: true, message: `Iniciando conexão para instância ${instanceId}...` });
    } else if (instance.connecting) {
        res.json({ success: true, message: `Instância ${instanceId} já está conectando...` });
    } else {
        res.json({ success: false, message: `Instância ${instanceId} já está conectada` });
    }
});

app.post('/disconnect/:instanceId', (req, res) => {
    const { instanceId } = req.params;
    const instance = instances.get(instanceId);
    
    if (instance && instance.sock) {
        try {
            instance.sock.logout();
            instances.delete(instanceId);
            res.json({ success: true, message: `Instância ${instanceId} desconectada` });
        } catch (err) {
            res.json({ success: false, message: `Erro ao desconectar ${instanceId}: ${err.message}` });
        }
    } else {
        res.json({ success: false, message: 'Instância não encontrada' });
    }
});

app.get('/health', (req, res) => {
    const connectedInstances = Array.from(instances.values()).filter(i => i.connected).length;
    const connectingInstances = Array.from(instances.values()).filter(i => i.connecting).length;
    
    res.json({
        status: 'running',
        instances: {
            total: instances.size,
            connected: connectedInstances,
            connecting: connectingInstances
        },
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});

const PORT = process.env.PORT || 3002;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Baileys Professional service rodando na porta ${PORT}`);
    console.log('⏳ Aguardando comandos para conectar instâncias...');
});