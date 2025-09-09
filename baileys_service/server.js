const express = require('express');
const cors = require('cors');
const { DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const makeWASocket = require('@whiskeysockets/baileys').default;
const qrTerminal = require('qrcode-terminal');

const app = express();
app.use(cors());
app.use(express.json());

let sock = null;
let qrString = null;
let isConnected = false;
let connectedUser = null;
let isConnecting = false;

async function connectToWhatsApp() {
    try {
        console.log('🔄 Iniciando conexão com WhatsApp...');
        const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
        
        sock = makeWASocket({
            auth: state,
            printQRInTerminal: true,
            browser: ['WhatsFlow', 'Chrome', '1.0.0']
        });

        sock.ev.on('connection.update', (update) => {
            const { connection, lastDisconnect, qr } = update;
            
            if (qr) {
                qrString = qr;
                console.log('📱 QR Code gerado para WhatsApp');
                qrTerminal.generate(qr, { small: true });
            }
            
            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
                console.log('🔌 Conexão fechada. Reconectar?', shouldReconnect);
                
                if (shouldReconnect) {
                    setTimeout(connectToWhatsApp, 5000);
                }
                isConnected = false;
                connectedUser = null;
                isConnecting = false;
            } else if (connection === 'open') {
                console.log('✅ WhatsApp conectado com sucesso!');
                isConnected = true;
                isConnecting = false;
                qrString = null;
                
                // Get user info
                connectedUser = {
                    id: sock.user.id,
                    name: sock.user.name || sock.user.id.split(':')[0]
                };
                
                // Send connected notification to Python backend
                setTimeout(async () => {
                    try {
                        const fetch = (await import('node-fetch')).default;
                        await fetch('http://localhost:8888/api/whatsapp/connected', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(connectedUser)
                        });
                    } catch (err) {
                        console.log('⚠️ Não foi possível notificar backend:', err.message);
                    }
                }, 1000);
                
            } else if (connection === 'connecting') {
                console.log('🔄 Conectando ao WhatsApp...');
                isConnecting = true;
            }
        });

        sock.ev.on('creds.update', saveCreds);
        
        sock.ev.on('messages.upsert', async (m) => {
            const messages = m.messages;
            
            for (const message of messages) {
                if (!message.key.fromMe && message.message) {
                    const from = message.key.remoteJid;
                    const text = message.message.conversation || 
                                message.message.extendedTextMessage?.text || 
                                'Mídia recebida';
                    
                    console.log('📥 Nova mensagem de:', from, '- Texto:', text);
                    
                    // Send to Python backend
                    try {
                        const fetch = (await import('node-fetch')).default;
                        await fetch('http://localhost:8888/api/messages/receive', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                from: from,
                                message: text,
                                timestamp: new Date().toISOString()
                            })
                        });
                    } catch (err) {
                        console.log('❌ Erro ao enviar mensagem para backend:', err.message);
                    }
                }
            }
        });

    } catch (error) {
        console.error('❌ Erro ao conectar WhatsApp:', error);
        isConnecting = false;
    }
}

// API Routes
app.get('/status', (req, res) => {
    res.json({
        connected: isConnected,
        connecting: isConnecting,
        user: connectedUser
    });
});

app.get('/qr', (req, res) => {
    res.json({
        qr: qrString,
        connected: isConnected
    });
});

app.post('/connect', (req, res) => {
    if (!isConnected && !isConnecting) {
        connectToWhatsApp();
        res.json({ success: true, message: 'Iniciando conexão...' });
    } else {
        res.json({ success: false, message: 'Já conectado ou conectando' });
    }
});

app.post('/send', async (req, res) => {
    if (!isConnected || !sock) {
        return res.status(400).json({ error: 'WhatsApp não conectado' });
    }
    
    const { to, message } = req.body;
    
    try {
        const jid = to.includes('@') ? to : `${to}@s.whatsapp.net`;
        await sock.sendMessage(jid, { text: message });
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`🚀 Baileys service rodando na porta ${PORT}`);
    console.log('⏳ Aguardando comando para conectar...');
});