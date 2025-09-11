#!/usr/bin/env python3
"""
WhatsFlow Real - Versão com Baileys REAL
Sistema de Automação WhatsApp com conexão verdadeira

Requisitos: Python 3 + Node.js (para Baileys)
Instalação: python3 whatsflow-real.py
Acesso: http://localhost:8888
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
import os
import subprocess
import sys
import threading
import time
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import logging
from typing import Set, Dict, Any
from zoneinfo import ZoneInfo
from pathlib import Path
import mimetypes

import base64

import asyncio

# Try to import websockets, fallback gracefully if not available
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("⚠️ WebSocket não disponível - executando sem tempo real")

# Configurações
DB_FILE = "whatsflow.db"
PORT = 8889
BAILEYS_PORT = 3002

# Brazil timezone
BR_TZ = ZoneInfo("America/Sao_Paulo")
BAILEYS_URL = os.getenv("BAILEYS_URL", f"http://127.0.0.1:{BAILEYS_PORT}")
WEBSOCKET_PORT = 8890

# Path to React build for serving the frontend
FRONTEND_BUILD_DIR = Path(__file__).resolve().parent / "frontend" / "build"
# codex/redesign-grupos-tab-with-campaign-button-1n5c7l


# Brazil timezone for scheduling



def compute_next_run(schedule_type: str, weekday: int, time_str: str) -> datetime:
    """Compute next datetime for a campaign message based on schedule."""
    now = datetime.now(BR_TZ)
    hour, minute = map(int, time_str.split(":"))
    scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if schedule_type == "daily":
        if scheduled <= now:
            scheduled += timedelta(days=1)
    elif schedule_type == "weekly":
        days_ahead = (weekday - scheduled.weekday()) % 7
        scheduled = scheduled + timedelta(days=days_ahead)
        if scheduled <= now:
            scheduled += timedelta(days=7)
    return scheduled

# WebSocket clients management
if WEBSOCKETS_AVAILABLE:
    websocket_clients: Set[websockets.WebSocketServerProtocol] = set()

# codex/redesign-grupos-tab-with-campaign-button-1n5c7l
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Database setup (same as before but with WebSocket integration)
def init_db():
    """Initialize SQLite database with WAL mode for better concurrency"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Enable WAL mode for better concurrent access
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA cache_size = 1000")
    cursor.execute("PRAGMA temp_store = MEMORY")
    cursor.execute("PRAGMA mmap_size = 268435456")  # 256MB
    
    # Enhanced tables with better schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instances (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            connected INTEGER DEFAULT 0,
            user_name TEXT,
            user_id TEXT,
            contacts_count INTEGER DEFAULT 0,
            messages_today INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            instance_id TEXT DEFAULT 'default',
            avatar_url TEXT,
            created_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            contact_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            direction TEXT NOT NULL,
            instance_id TEXT DEFAULT 'default',
            message_type TEXT DEFAULT 'text',
            whatsapp_id TEXT,
            created_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            contact_phone TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            instance_id TEXT NOT NULL,
            last_message TEXT,
            last_message_time TEXT,
            unread_count INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            nodes TEXT NOT NULL,
            edges TEXT NOT NULL,
            active INTEGER DEFAULT 0,
            instance_id TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Campaign tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaign_groups (
            campaign_id INTEGER,
            instance_id TEXT,
            group_id TEXT,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaign_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER,
            schedule_type TEXT,
            weekday INTEGER,
            send_time TEXT,
            message TEXT,
            media_type TEXT,
            media_path TEXT,
            next_run TEXT,
            FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
        )
    """)


    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado com suporte WebSocket")


# Campaign scheduler
def campaign_scheduler_loop():
    while True:
        try:
            now = datetime.now(BR_TZ).isoformat()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, campaign_id, message, media_type, media_path, schedule_type, weekday, send_time FROM campaign_messages WHERE next_run <= ?",
                (now,)
            )
            rows = cursor.fetchall()
            for row in rows:
                msg_id, campaign_id, message, media_type, media_path, schedule_type, weekday, send_time = row
                cursor.execute(
                    "SELECT instance_id, group_id FROM campaign_groups WHERE campaign_id=?",
                    (campaign_id,)
                )
                targets = cursor.fetchall()
                for instance_id, group_id in targets:
                    data = {"to": group_id, "message": message, "type": media_type or "text"}
                    try:
                        import requests
                        requests.post(
                            f"http://127.0.0.1:{BAILEYS_PORT}/send/{instance_id}",
                            json=data,
                            timeout=10,
                        )
                    except Exception:
                        pass

                # compute next run
                next_dt = compute_next_run(schedule_type, weekday or 0, send_time)
                cursor.execute(
                    "UPDATE campaign_messages SET next_run=? WHERE id=?",
                    (next_dt.isoformat(), msg_id),
                )
            conn.commit()
            conn.close()
        except Exception:
            pass

        time.sleep(60)


def start_campaign_scheduler():
    thread = threading.Thread(target=campaign_scheduler_loop, daemon=True)
    thread.start()
    return thread


# WebSocket Server Functions
if WEBSOCKETS_AVAILABLE:
    async def websocket_handler(websocket, path):
        """Handle WebSocket connections"""
        websocket_clients.add(websocket)
        logger.info(f"📱 Cliente WebSocket conectado. Total: {len(websocket_clients)}")
        
        try:
            await websocket.wait_closed()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            websocket_clients.discard(websocket)
            logger.info(f"📱 Cliente WebSocket desconectado. Total: {len(websocket_clients)}")

    async def broadcast_message(message_data: Dict[str, Any]):
        """Broadcast message to all connected WebSocket clients"""
        if not websocket_clients:
            return
        
        message = json.dumps(message_data)
        disconnected_clients = set()
        
        for client in websocket_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"❌ Erro ao enviar mensagem WebSocket: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            websocket_clients.discard(client)

    async def _websocket_server():
        async with websockets.serve(
            websocket_handler,
            "0.0.0.0",
            WEBSOCKET_PORT,
            ping_interval=30,
            ping_timeout=10,
        ):
            logger.info(f"🔌 WebSocket server iniciado na porta {WEBSOCKET_PORT}")
            await asyncio.Future()  # run forever

    def start_websocket_server():
        """Start WebSocket server in a separate thread"""

        def run_websocket():
            try:
                asyncio.run(_websocket_server())
            except Exception as e:
                logger.error(f"❌ Erro no WebSocket server: {e}")

        websocket_thread = threading.Thread(target=run_websocket, daemon=True)
        websocket_thread.start()
        return websocket_thread
else:
    def start_websocket_server():
        print("⚠️ WebSocket não disponível - modo básico")
        return None


def add_sample_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM instances")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    current_time = datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()
    
    # Sample instance
    instance_id = str(uuid.uuid4())
    cursor.execute("INSERT INTO instances (id, name, contacts_count, messages_today, created_at) VALUES (?, ?, ?, ?, ?)",
                  (instance_id, "WhatsApp Principal", 0, 0, current_time))
    
    conn.commit()
    conn.close()

# Baileys Service Manager
class BaileysManager:
    def __init__(self):
        self.process = None
        self.is_running = False
        self.baileys_dir = "baileys_service"
        
    def start_baileys(self):
        """Start Baileys service"""
        if self.is_running:
            return True
            
        try:
            print("📦 Configurando serviço Baileys...")
            
            # Create Baileys service directory
            if not os.path.exists(self.baileys_dir):
                os.makedirs(self.baileys_dir)
                print(f"✅ Diretório {self.baileys_dir} criado")
            
            # Create package.json
            package_json = {
                "name": "whatsflow-baileys",
                "version": "1.0.0",
                "description": "WhatsApp Baileys Service for WhatsFlow",
                "main": "server.js",
                "dependencies": {
                    "@whiskeysockets/baileys": "^6.7.0",
                    "express": "^4.18.2",
                    "cors": "^2.8.5",
                    "qrcode-terminal": "^0.12.0"
                },
                "scripts": {
                    "start": "node server.js"
                }
            }
            
            package_path = f"{self.baileys_dir}/package.json"
            with open(package_path, 'w') as f:
                json.dump(package_json, f, indent=2)
            print("✅ package.json criado")
            
            # Create Baileys server
            baileys_server = '''const express = require('express');
const cors = require('cors');
const { DisconnectReason, useMultiFileAuthState, downloadMediaMessage } = require('@whiskeysockets/baileys');
const makeWASocket = require('@whiskeysockets/baileys').default;
const qrTerminal = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors({
    origin: ['http://localhost:8889', 'http://127.0.0.1:8889', 'http://localhost:3000', 'http://127.0.0.1:3000'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'Accept']
}));
app.use(express.json());

// Global state management
let instances = new Map(); // instanceId -> { sock, qr, connected, connecting, user }
let currentQR = null;
let qrUpdateInterval = null;

// QR Code auto-refresh every 30 seconds (WhatsApp QR expires after 60s)
const startQRRefresh = (instanceId) => {
    if (qrUpdateInterval) clearInterval(qrUpdateInterval);
    
    qrUpdateInterval = setInterval(() => {
        const instance = instances.get(instanceId);
        if (instance && !instance.connected && instance.connecting) {
            console.log('🔄 QR Code expirado, gerando novo...');
            // Don't reconnect immediately, let WhatsApp generate new QR
        }
    }, 30000); // 30 seconds
};

const stopQRRefresh = () => {
    if (qrUpdateInterval) {
        clearInterval(qrUpdateInterval);
        qrUpdateInterval = null;
    }
};

async function connectInstance(instanceId) {
    try {
        console.log(`🔄 Iniciando conexão para instância: ${instanceId}`);
        
        // Create instance directory
        const authDir = `./auth_${instanceId}`;
        if (!fs.existsSync(authDir)) {
            fs.mkdirSync(authDir, { recursive: true });
        }
        
        const { state, saveCreds } = await useMultiFileAuthState(authDir);
        
        const sock = makeWASocket({
            auth: state,
            browser: ['WhatsFlow', 'Desktop', '1.0.0'],
            connectTimeoutMs: 60000,
            defaultQueryTimeoutMs: 0,
            keepAliveIntervalMs: 30000,
            generateHighQualityLinkPreview: true,
            markOnlineOnConnect: true,
            syncFullHistory: true,
            retryRequestDelayMs: 5000,
            maxRetries: 5
        });

        // Initialize instance
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
                
                // Manual QR display in terminal (since printQRInTerminal is deprecated)
                try {
                    qrTerminal.generate(qr, { small: true });
                } catch (err) {
                    console.log('⚠️ QR Terminal não disponível:', err.message);
                }
                
                startQRRefresh(instanceId);
            }
            
            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
                const reason = lastDisconnect?.error?.output?.statusCode || 'unknown';
                
                console.log(`🔌 Instância ${instanceId} desconectada. Razão: ${reason}, Reconectar: ${shouldReconnect}`);
                
                instance.connected = false;
                instance.connecting = false;
                instance.user = null;
                stopQRRefresh();
                
                // Implement robust reconnection logic
                if (shouldReconnect) {
                    if (reason === DisconnectReason.restartRequired) {
                        console.log(`🔄 Restart requerido para ${instanceId}`);
                        setTimeout(() => connectInstance(instanceId), 5000);
                    } else if (reason === DisconnectReason.connectionClosed) {
                        console.log(`🔄 Conexão fechada, reconectando ${instanceId}`);
                        setTimeout(() => connectInstance(instanceId), 10000);
                    } else if (reason === DisconnectReason.connectionLost) {
                        console.log(`🔄 Conexão perdida, reconectando ${instanceId}`);
                        setTimeout(() => connectInstance(instanceId), 15000);
                    } else if (reason === DisconnectReason.timedOut) {
                        console.log(`⏱️ Timeout, reconectando ${instanceId}`);
                        setTimeout(() => connectInstance(instanceId), 20000);
                    } else {
                        console.log(`🔄 Reconectando ${instanceId} em 30 segundos`);
                        setTimeout(() => connectInstance(instanceId), 30000);
                    }
                } else {
                    console.log(`❌ Instância ${instanceId} deslogada permanentemente`);
                    // Clean auth files if logged out
                    try {
                        const authPath = path.join('./auth_' + instanceId);
                        if (fs.existsSync(authPath)) {
                            fs.rmSync(authPath, { recursive: true, force: true });
                            console.log(`🧹 Arquivos de auth removidos para ${instanceId}`);
                        }
                    } catch (err) {
                        console.log('⚠️ Erro ao limpar arquivos de auth:', err.message);
                    }
                }
                
                // Notify backend about disconnection
                try {
                    const fetch = (await import('node-fetch')).default;
                    await fetch('http://localhost:8889/api/whatsapp/disconnected', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            instanceId: instanceId,
                            reason: reason
                        })
                    });
                } catch (err) {
                    console.log('⚠️ Não foi possível notificar desconexão:', err.message);
                }
                
            } else if (connection === 'open') {
                console.log(`✅ Instância ${instanceId} conectada com SUCESSO!`);
                instance.connected = true;
                instance.connecting = false;
                instance.qr = null;
                instance.lastSeen = new Date();
                currentQR = null;
                stopQRRefresh();
                
                // Get user info
                instance.user = {
                    id: sock.user.id,
                    name: sock.user.name || sock.user.id.split(':')[0],
                    profilePictureUrl: null,
                    phone: sock.user.id.split(':')[0]
                };
                
                console.log(`👤 Usuário conectado: ${instance.user.name} (${instance.user.phone})`);
                
                // Try to get profile picture
                try {
                    const profilePic = await sock.profilePictureUrl(sock.user.id, 'image');
                    instance.user.profilePictureUrl = profilePic;
                    console.log('📸 Foto do perfil obtida');
                } catch (err) {
                    console.log('⚠️ Não foi possível obter foto do perfil');
                }
                
                // Wait a bit before importing chats to ensure connection is stable
                setTimeout(async () => {
                    try {
                        console.log('📥 Importando conversas existentes...');
                        
                        // Get all chats
                        const chats = await sock.getChats();
                        console.log(`📊 ${chats.length} conversas encontradas`);
                        
                        // Process chats in batches to avoid overwhelming the system
                        const batchSize = 20;
                        for (let i = 0; i < chats.length; i += batchSize) {
                            const batch = chats.slice(i, i + batchSize);
                            
                            // Send batch to Python backend
                            const fetch = (await import('node-fetch')).default;
                            await fetch('http://localhost:8889/api/chats/import', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    instanceId: instanceId,
                                    chats: batch,
                                    user: instance.user,
                                    batchNumber: Math.floor(i / batchSize) + 1,
                                    totalBatches: Math.ceil(chats.length / batchSize)
                                })
                            });
                            
                            console.log(`📦 Lote ${Math.floor(i / batchSize) + 1}/${Math.ceil(chats.length / batchSize)} enviado`);
                            
                            // Small delay between batches
                            await new Promise(resolve => setTimeout(resolve, 1000));
                        }
                        
                        console.log('✅ Importação de conversas concluída');
                        
                    } catch (err) {
                        console.log('⚠️ Erro ao importar conversas:', err.message);
                    }
                }, 5000); // Wait 5 seconds after connection
                
                // Send connected notification to Python backend
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
                }, 2000);
                
            } else if (connection === 'connecting') {
                console.log(`🔄 Conectando instância ${instanceId}...`);
                instance.connecting = true;
                instance.lastSeen = new Date();
            }
        });

        sock.ev.on('creds.update', saveCreds);
        
        // Handle incoming messages with better error handling
        sock.ev.on('messages.upsert', async (m) => {
            const messages = m.messages;
            
            for (const message of messages) {
                if (!message.key.fromMe && message.message) {
                    const from = message.key.remoteJid;
                    const messageText = message.message.conversation || 
                                      message.message.extendedTextMessage?.text || 
                                      'Mídia recebida';
                    
                    // Extract contact name from WhatsApp
                    const pushName = message.pushName || '';
                    const contact = await sock.onWhatsApp(from);
                    const contactName = pushName || contact[0]?.name || '';
                    
                    console.log(`📥 Nova mensagem na instância ${instanceId}`);
                    console.log(`👤 Contato: ${contactName || from.split('@')[0]} (${from.split('@')[0]})`);
                    console.log(`💬 Mensagem: ${messageText.substring(0, 50)}...`);
                    
                    // Send to Python backend with retry logic
                    let retries = 3;
                    while (retries > 0) {
                        try {
                            const fetch = (await import('node-fetch')).default;
                            const response = await fetch('http://localhost:8889/api/messages/receive', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    instanceId: instanceId,
                                    from: from,
                                    message: messageText,
                                    pushName: pushName,
                                    contactName: contactName,
                                    timestamp: new Date().toISOString(),
                                    messageId: message.key.id,
                                    messageType: message.message.conversation ? 'text' : 'media'
                                })
                            });
                            
                            if (response.ok) {
                                break; // Success, exit retry loop
                            } else {
                                throw new Error(`HTTP ${response.status}`);
                            }
                        } catch (err) {
                            retries--;
                            console.log(`❌ Erro ao enviar mensagem (tentativas restantes: ${retries}):`, err.message);
                            if (retries > 0) {
                                await new Promise(resolve => setTimeout(resolve, 2000));
                            }
                        }
                    }
                }
            }
        });

        // Keep connection alive with heartbeat
        setInterval(() => {
            const instance = instances.get(instanceId);
            if (instance && instance.connected && instance.sock) {
                instance.lastSeen = new Date();
                // Send heartbeat
                instance.sock.sendPresenceUpdate('available').catch(() => {});
            }
        }, 60000); // Every minute

    } catch (error) {
        console.error(`❌ Erro fatal ao conectar instância ${instanceId}:`, error);
        const instance = instances.get(instanceId);
        if (instance) {
            instance.connecting = false;
            instance.connected = false;
        }
    }
}

// API Routes with better error handling
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
        // Return all instances
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
            expiresIn: 60 // QR expires in 60 seconds
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
        connectInstance(instanceId || 'default');
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
            stopQRRefresh();
            res.json({ success: true, message: `Instância ${instanceId} desconectada` });
        } catch (err) {
            res.json({ success: false, message: `Erro ao desconectar ${instanceId}: ${err.message}` });
        }
    } else {
        res.json({ success: false, message: 'Instância não encontrada' });
    }
});

app.post('/send/:instanceId', async (req, res) => {
    const { instanceId } = req.params;
    const { to, message, type = 'text' } = req.body;
    
    const instance = instances.get(instanceId);
    if (!instance || !instance.connected || !instance.sock) {
        return res.status(400).json({ error: 'Instância não conectada', instanceId: instanceId });
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
        
        console.log(`📤 Mensagem enviada da instância ${instanceId} para ${to}`);
        res.json({ success: true, instanceId: instanceId });
    } catch (error) {
        console.error(`❌ Erro ao enviar mensagem da instância ${instanceId}:`, error);
        res.status(500).json({ error: error.message, instanceId: instanceId });
    }
});

// Groups endpoint with robust error handling  
app.get('/groups/:instanceId', async (req, res) => {
    const { instanceId } = req.params;
    
    try {
        const instance = instances.get(instanceId);
        if (!instance || !instance.connected || !instance.sock) {
            return res.status(400).json({ 
                success: false,
                error: `Instância ${instanceId} não está conectada`,
                instanceId: instanceId,
                groups: []
            });
        }
        
        console.log(`📥 Buscando grupos para instância: ${instanceId}`);
        
        // Multiple methods to get groups
        let groups = [];
        
        try {
            // Method 1: Get group metadata
            const groupIds = await instance.sock.groupFetchAllParticipating();
            console.log(`📊 Encontrados ${Object.keys(groupIds).length} grupos via groupFetchAllParticipating`);
            
            for (const [groupId, groupData] of Object.entries(groupIds)) {
                groups.push({
                    id: groupId,
                    name: groupData.subject || 'Grupo sem nome',
                    description: groupData.desc || '',
                    participants: groupData.participants ? groupData.participants.length : 0,
                    admin: groupData.participants ? 
                           groupData.participants.some(p => p.admin && p.id === instance.user?.id) : false,
                    created: groupData.creation || null
                });
            }
        } catch (error) {
            console.log(`⚠️ Método 1 falhou: ${error.message}`);
            
            try {
                // Method 2: Get chats and filter groups
                const chats = await instance.sock.getChats();
                const groupChats = chats.filter(chat => chat.id.endsWith('@g.us'));
                console.log(`📊 Encontrados ${groupChats.length} grupos via getChats`);
                
                groups = groupChats.map(chat => ({
                    id: chat.id,
                    name: chat.name || chat.subject || 'Grupo sem nome',
                    description: chat.description || '',
                    participants: chat.participantsCount || 0,
                    admin: false, // Cannot determine admin status from chat
                    created: chat.timestamp || null,
                    lastMessage: chat.lastMessage ? {
                        text: chat.lastMessage.message || '',
                        timestamp: chat.lastMessage.timestamp
                    } : null
                }));
            } catch (error2) {
                console.log(`⚠️ Método 2 falhou: ${error2.message}`);
                
                // Method 3: Simple fallback - return empty with proper structure
                groups = [];
            }
        }
        
        console.log(`✅ Retornando ${groups.length} grupos para instância ${instanceId}`);
        
        res.json({
            success: true,
            instanceId: instanceId,
            groups: groups,
            count: groups.length,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error(`❌ Erro ao buscar grupos para instância ${instanceId}:`, error);
        res.status(500).json({
            success: false,
            error: `Erro interno ao buscar grupos: ${error.message}`,
            instanceId: instanceId,
            groups: []
        });
    }
});

// Health check endpoint
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
const BASE_URL = process.env.BAILEYS_URL || `http://localhost:${PORT}`;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Baileys service rodando na porta ${PORT}`);
    console.log(`📊 Health check: ${BASE_URL}/health`);
    console.log('⏳ Aguardando comandos para conectar instâncias...');
});'''
            
            server_path = f"{self.baileys_dir}/server.js"
            with open(server_path, 'w') as f:
                f.write(baileys_server)
            print("✅ server.js criado")
            
            # Install dependencies
            print("📦 Iniciando instalação das dependências...")
            print("   Isso pode levar alguns minutos na primeira vez...")
            
            try:
                # Try npm first, then yarn
                result = subprocess.run(['npm', 'install'], cwd=self.baileys_dir, 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    print("⚠️ npm falhou, tentando yarn...")
                    result = subprocess.run(['yarn', 'install'], cwd=self.baileys_dir, 
                                          capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print("✅ Dependências instaladas com sucesso!")
                    # Install node-fetch specifically (required for backend communication)
                    print("📦 Instalando node-fetch...")
                    fetch_result = subprocess.run(['npm', 'install', 'node-fetch@2.6.7'], 
                                                cwd=self.baileys_dir, capture_output=True, text=True)
                    if fetch_result.returncode == 0:
                        print("✅ node-fetch instalado com sucesso!")
                    else:
                        print("⚠️ Aviso: node-fetch pode não ter sido instalado corretamente")
                else:
                    print(f"❌ Erro na instalação: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("⏰ Timeout na instalação - continuando mesmo assim...")
            except FileNotFoundError:
                print("❌ npm/yarn não encontrado. Por favor instale Node.js primeiro.")
                return False
            
            # Start the service
            print("🚀 Iniciando serviço Baileys...")
            try:
                self.process = subprocess.Popen(
                    ['node', 'server.js'],
                    cwd=self.baileys_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self.is_running = True
                
                # Wait a bit and check if it's still running
                time.sleep(3)
                if self.process.poll() is None:
                    print("✅ Baileys iniciado com sucesso!")
                    return True
                else:
                    stdout, stderr = self.process.communicate()
                    print(f"❌ Baileys falhou ao iniciar:")
                    print(f"stdout: {stdout}")
                    print(f"stderr: {stderr}")
                    return False
                    
            except FileNotFoundError:
                print("❌ Node.js não encontrado no sistema")
                return False
            
        except Exception as e:
            print(f"❌ Erro ao configurar Baileys: {e}")
            return False
    
    def stop_baileys(self):
        """Stop Baileys service"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                print("✅ Baileys parado com sucesso")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("⚠️ Baileys forçadamente terminado")
            
            self.is_running = False
            self.process = None

# HTTP Handler with Baileys integration
class WhatsFlowRealHandler(BaseHTTPRequestHandler):
    # codex/redesign-grupos-tab-with-campaign-button-1n5c7l
    def serve_frontend(self, *, head: bool = False) -> None:

        path = self.path.split('?', 1)[0]
        file_path = (FRONTEND_BUILD_DIR / path.lstrip('/')).resolve()
        if file_path.is_dir():
            file_path /= 'index.html'
        if not str(file_path).startswith(str(FRONTEND_BUILD_DIR)):
            self.send_error(404, "Not Found")
            return
        if not file_path.exists():
            # Only fallback to index.html for extensionless paths
            if Path(path).suffix:
                self.send_error(404, "Not Found")
                return
            file_path = FRONTEND_BUILD_DIR / 'index.html'
        try:
            with open(file_path, 'rb') as f:
                mime_type, _ = mimetypes.guess_type(str(file_path))
                self.send_response(200)
                self.send_header("Content-Type", mime_type or "application/octet-stream")
                self.end_headers()
                # codex/redesign-grupos-tab-with-campaign-button-1n5c7l
                if not head:
                    self.wfile.write(f.read())

        except FileNotFoundError:
            self.send_error(404, "Not Found")

    def do_GET(self):
        if not self.path.startswith('/api'):
            self.serve_frontend()
            return

        if self.path == '/api/instances':
            self.handle_get_instances()
        elif self.path == '/api/stats':
            self.handle_get_stats()
        elif self.path == '/api/messages':
            self.handle_get_messages()
        elif self.path == '/api/whatsapp/status':
            # Fallback for backward compatibility - use default instance
            self.handle_whatsapp_status('default')
        elif self.path == '/api/whatsapp/qr':
            # Fallback for backward compatibility - use default instance
            self.handle_whatsapp_qr('default')
        elif self.path == '/api/contacts':
            self.handle_get_contacts()
        elif self.path == '/api/chats':
            self.handle_get_chats()
        elif self.path == '/api/flows':
            self.handle_get_flows()
        elif self.path.startswith('/api/campaigns'):
            parts = self.path.strip('/').split('/')
            if len(parts) == 2:
                self.handle_get_campaigns()
            elif len(parts) >= 3:
                campaign_id = parts[2]
                if len(parts) == 3:
                    self.handle_get_campaign(campaign_id)
                elif len(parts) == 4 and parts[3] == 'groups':
                    self.handle_get_campaign_groups(campaign_id)
                elif len(parts) == 4 and parts[3] == 'messages':
                    self.handle_get_campaign_messages(campaign_id)
                else:
                    self.send_error(404, "Not Found")
            else:
                self.send_error(404, "Not Found")
        elif self.path.startswith('/api/groups/'):
            instance_id = self.path.split('/')[-1]
            self.handle_get_groups(instance_id)
        elif self.path == '/api/webhooks/send':
            self.handle_send_webhook()
        elif self.path.startswith('/api/whatsapp/status/'):
            instance_id = self.path.split('/')[-1]
            self.handle_whatsapp_status(instance_id)
        elif self.path.startswith('/api/whatsapp/qr/'):
            instance_id = self.path.split('/')[-1]
            self.handle_whatsapp_qr(instance_id)
        elif self.path.startswith('/api/messages?'):
            self.handle_get_messages_filtered()
        elif self.path == '/api/webhooks':
            self.handle_get_webhooks()
        elif self.path == '/api/messages/scheduled':
            self.handle_get_scheduled_messages()
        else:
            self.send_error(404, "Not Found")

    def do_HEAD(self):
        if not self.path.startswith('/api'):
            self.serve_frontend(head=True)
            return
        self.send_error(405, "Method Not Allowed")
    
    def do_POST(self):
        if self.path == '/api/instances':
            self.handle_create_instance()
        elif self.path.startswith('/api/instances/') and self.path.endswith('/connect'):
            instance_id = self.path.split('/')[-2]
            self.handle_connect_instance(instance_id)
        elif self.path.startswith('/api/instances/') and self.path.endswith('/disconnect'):
            instance_id = self.path.split('/')[-2]
            self.handle_disconnect_instance(instance_id)
        elif self.path == '/api/messages/receive':
            self.handle_receive_message()
        elif self.path == '/api/whatsapp/connected':
            self.handle_whatsapp_connected()
        elif self.path == '/api/whatsapp/disconnected':
            self.handle_whatsapp_disconnected()
        elif self.path == '/api/chats/import':
            self.handle_import_chats()
        elif self.path.startswith('/api/whatsapp/connect/'):
            instance_id = self.path.split('/')[-1]
            self.handle_connect_instance(instance_id)
        elif self.path.startswith('/api/whatsapp/disconnect/'):
            instance_id = self.path.split('/')[-1]
            self.handle_disconnect_instance(instance_id)
        elif self.path.startswith('/api/whatsapp/status/'):
            instance_id = self.path.split('/')[-1]
            self.handle_whatsapp_status(instance_id)
        elif self.path.startswith('/api/whatsapp/qr/'):
            instance_id = self.path.split('/')[-1]
            self.handle_whatsapp_qr(instance_id)
        elif self.path.startswith('/api/messages/send/'):
            instance_id = self.path.split('/')[-1]
            self.handle_send_message(instance_id)
        elif self.path.startswith('/api/send/'):
            instance_id = self.path.split('/')[-1]
            self.handle_send_message(instance_id)

        elif self.path == '/api/flows':
            self.handle_create_flow()
        elif self.path == '/api/campaigns':
            self.handle_create_campaign()
        elif self.path.startswith('/api/campaigns/') and self.path.endswith('/groups'):
            campaign_id = int(self.path.split('/')[-2])
            self.handle_set_campaign_groups(campaign_id)
        elif self.path.startswith('/api/campaigns/') and self.path.endswith('/messages'):
            campaign_id = int(self.path.split('/')[-2])
            self.handle_add_campaign_message(campaign_id)

        elif self.path == '/api/webhooks/send':
            self.handle_send_webhook()
        else:
            self.send_error(404, "Not Found")
    
    def do_PUT(self):
        if self.path.startswith('/api/flows/'):
            flow_id = self.path.split('/')[-1]
            self.handle_update_flow(flow_id)
        elif self.path.startswith('/api/campaigns/'):
            campaign_id = self.path.split('/')[-1]
            self.handle_update_campaign(campaign_id)
        else:
            self.send_error(404, "Not Found")
    
    def do_DELETE(self):
        if self.path.startswith('/api/instances/'):
            instance_id = self.path.split('/')[-1]
            self.handle_delete_instance(instance_id)
        elif self.path.startswith('/api/flows/'):
            flow_id = self.path.split('/')[-1]
            self.handle_delete_flow(flow_id)
        elif self.path.startswith('/api/campaigns/'):
            campaign_id = self.path.split('/')[-1]
            self.handle_delete_campaign(campaign_id)
        elif self.path.startswith('/api/messages/scheduled/'):
            schedule_id = self.path.split('/')[-1]
            self.handle_delete_campaign_message(schedule_id)
        else:
            self.send_error(404, "Not Found")
    
    def send_html_response(self, html_content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def handle_get_instances(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM instances ORDER BY created_at DESC")
            instances = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(instances)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_get_stats(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM contacts")
            contacts_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM messages")
            messages_count = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                "contacts_count": contacts_count,
                "conversations_count": contacts_count,
                "messages_count": messages_count
            }
            
            self.send_json_response(stats)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_get_messages(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY created_at DESC LIMIT 50")
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(messages)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_schedule_message(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8')) if length else {}
            campaign_id = data.get('campaign_id') or data.get('campaignId')
            content = data.get('content') or data.get('message', '')
            media_type = data.get('media_type') or data.get('mediaType', 'text')
            media_path = data.get('media_path')
            groups = data.get('groups', [])

            if not campaign_id:
                self.send_json_response({"error": "Dados inválidos"}, 400)
                return

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT recurrence, send_time, weekday, timezone FROM campaigns WHERE id = ?",
                (campaign_id,),
            )
            row = cursor.fetchone()
            if not row:
                conn.close()
                self.send_json_response({"error": "Campanha não encontrada"}, 404)
                return
            recurrence, send_time, weekday, timezone = row
            next_run = calculate_next_run(
                recurrence or 'once', send_time or '00:00', weekday, timezone
            )

            schedule_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO scheduled_messages (id, campaign_id, content, media_type, media_path, next_run, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    schedule_id,
                    campaign_id,
                    content,
                    media_type,
                    media_path,
                    next_run,
                ),
            )

            for gid in groups:
                cursor.execute(
                    "INSERT OR IGNORE INTO campaign_groups (campaign_id, group_id) VALUES (?, ?)",
                    (campaign_id, gid),
                )

            conn.commit()
            conn.close()
            self.send_json_response({"success": True, "id": schedule_id})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_get_scheduled_messages(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT cm.id, cm.campaign_id, c.name as campaign_name, cm.content, cm.media_type, cm.media_path,
                       cm.recurrence, cm.send_time, cm.weekday, cm.timezone, cm.next_run, cm.status
                FROM campaign_messages cm
                JOIN campaigns c ON c.id = cm.campaign_id
                ORDER BY cm.next_run ASC
                """,
            )
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(messages)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_schedule_campaign_message(self, campaign_id: str) -> None:
        """Schedule a message for a specific campaign."""
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8')) if length else {}
            content = data.get('content') or data.get('message', '')
            media_type = data.get('media_type') or data.get('mediaType', 'text')
            media_path = data.get('media_path')
            groups = data.get('groups')

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT recurrence, send_time, weekday, timezone FROM campaigns WHERE id = ?",
                (campaign_id,),
            )
            row = cursor.fetchone()
            if not row:
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)
                return

            cursor.execute(
                "SELECT group_id FROM campaign_groups WHERE campaign_id = ?",
                (campaign_id,),
            )
            allowed_groups = {g[0] for g in cursor.fetchall()}
            if not allowed_groups:
                conn.close()
                self.send_json_response({'error': 'Nenhum grupo associado à campanha'}, 400)
                return

            if groups:
                if not set(groups).issubset(allowed_groups):
                    conn.close()
                    self.send_json_response({'error': 'Grupos inválidos para esta campanha'}, 400)
                    return

            recurrence, send_time, weekday, timezone = row
            next_run = calculate_next_run(
                recurrence or 'once', send_time or '00:00', weekday, timezone
            )

            schedule_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO campaign_messages (id, campaign_id, content, media_type, media_path, recurrence, send_time, weekday, timezone, next_run, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    schedule_id,
                    campaign_id,
                    content,
                    media_type,
                    media_path,
                    recurrence,
                    send_time,
                    weekday,
                    timezone,
                    next_run,
                ),
            )

            conn.commit()
            conn.close()
            self.send_json_response({'success': True, 'id': schedule_id}, 201)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_get_campaign_messages(self, campaign_id: str) -> None:
        """List scheduled messages for a campaign."""
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM campaigns WHERE id = ?", (campaign_id,))
            if not cursor.fetchone():
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)
                return

            cursor.execute(
                "SELECT group_id FROM campaign_groups WHERE campaign_id = ?",
                (campaign_id,),
            )
            groups = [g[0] for g in cursor.fetchall()]
            if not groups:
                conn.close()
                self.send_json_response({'error': 'Nenhum grupo associado à campanha'}, 400)
                return

            cursor.execute(
                """
                SELECT id, content, media_type, media_path, recurrence, send_time, weekday, timezone, next_run, status
                FROM campaign_messages
                WHERE campaign_id = ?
                ORDER BY next_run ASC
                """,
                (campaign_id,),
            )
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response({'campaign_id': campaign_id, 'groups': groups, 'messages': messages})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_delete_campaign_message(self, message_id: str):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM campaign_messages WHERE id = ?", (message_id,))
            conn.commit()
            conn.close()
            self.send_json_response({"success": True})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_create_instance(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json_response({"error": "No data provided"}, 400)
                return
                
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if 'name' not in data or not data['name'].strip():
                self.send_json_response({"error": "Name is required"}, 400)
                return
            
            instance_id = str(uuid.uuid4())
            created_at = datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO instances (id, name, created_at)
                VALUES (?, ?, ?)
            """, (instance_id, data['name'].strip(), created_at))
            conn.commit()
            conn.close()
            
            result = {
                "id": instance_id,
                "name": data['name'].strip(),
                "connected": 0,
                "contacts_count": 0,
                "messages_today": 0,
                "created_at": created_at
            }
            
            self.send_json_response(result, 201)
        except json.JSONDecodeError:
            self.send_json_response({"error": "Invalid JSON"}, 400)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_connect_instance(self, instance_id):
        try:
            # Start Baileys connection
            try:
                import requests
                response = requests.post(f'{BAILEYS_URL}/connect', timeout=5)
                
                if response.status_code == 200:
                    self.send_json_response({"success": True, "message": "Conexão iniciada"})
                else:
                    self.send_json_response({"error": "Erro ao iniciar conexão"}, 500)
            except ImportError:
                # Fallback usando urllib se requests não estiver disponível
                import urllib.request
                import urllib.error

                try:
                    data = json.dumps({}).encode('utf-8')
                    req = urllib.request.Request(
                        'http://127.0.0.1:3002/connect',
                        data=data,
                        headers={'Content-Type': 'application/json'},
                    )

                    req.get_method = lambda: 'POST'

                    with urllib.request.urlopen(req, timeout=5) as response:
                        if response.status == 200:
                            self.send_json_response({"success": True, "message": "Conexão iniciada"})
                        else:
                            self.send_json_response({"error": "Erro ao iniciar conexão"}, 500)
                except urllib.error.URLError as e:
                    self.send_json_response({"error": f"Serviço WhatsApp indisponível: {str(e)}"}, 500)
                
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_whatsapp_status(self):
        try:
            try:
                import requests
                response = requests.get(f'{BAILEYS_URL}/status', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"connected": False, "connecting": False})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen(f'{BAILEYS_URL}/status', timeout=5) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            self.send_json_response(data)
                        else:
                            self.send_json_response({"connected": False, "connecting": False})
                except:
                    self.send_json_response({"connected": False, "connecting": False})
                
        except Exception as e:
            self.send_json_response({"connected": False, "connecting": False, "error": str(e)})
    
    def handle_whatsapp_qr(self):
        try:
            try:
                import requests
                response = requests.get(f'{BAILEYS_URL}/qr', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"qr": None, "connected": False})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen(f'{BAILEYS_URL}/qr', timeout=5) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            self.send_json_response(data)
                        else:
                            self.send_json_response({"qr": None, "connected": False})
                except:
                    self.send_json_response({"qr": None, "connected": False})
                
        except Exception as e:
            self.send_json_response({"qr": None, "connected": False, "error": str(e)})
    
    def handle_whatsapp_disconnected(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = data.get('instanceId', 'default')
            reason = data.get('reason', 'unknown')
            
            # Update instance connection status
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE instances SET connected = 0, user_name = NULL, user_id = NULL
                WHERE id = ?
            """, (instance_id,))
            
            conn.commit()
            conn.close()
            
            print(f"❌ WhatsApp desconectado na instância {instance_id} - Razão: {reason}")
            self.send_json_response({"success": True, "instanceId": instance_id})
            
        except Exception as e:
            print(f"❌ Erro ao processar desconexão: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_import_chats(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = data.get('instanceId', 'default')
            chats = data.get('chats', [])
            user = data.get('user', {})
            batch_number = data.get('batchNumber', 1)
            total_batches = data.get('totalBatches', 1)
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Update instance with user info on first batch
            if batch_number == 1:
                cursor.execute("""
                    UPDATE instances SET connected = 1, user_name = ?, user_id = ? 
                    WHERE id = ?
                """, (user.get('name', ''), user.get('id', ''), instance_id))
                print(f"👤 Usuário atualizado: {user.get('name', '')} ({user.get('phone', '')})")
            
            # Import contacts and chats from this batch
            imported_contacts = 0
            imported_chats = 0
            
            for chat in chats:
                if chat.get('id') and not chat['id'].endswith('@g.us'):  # Skip groups for now
                    phone = chat['id'].replace('@s.whatsapp.net', '').replace('@c.us', '')
                    contact_name = chat.get('name') or f"Contato {phone[-4:]}"
                    
                    # Check if contact exists
                    cursor.execute("SELECT id FROM contacts WHERE phone = ? AND instance_id = ?", (phone, instance_id))
                    if not cursor.fetchone():
                        contact_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO contacts (id, name, phone, instance_id, created_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (contact_id, contact_name, phone, instance_id, datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()))
                        imported_contacts += 1
                    
                    # Create/update chat entry
                    last_message = None
                    last_message_time = None
                    unread_count = chat.get('unreadCount', 0)
                    
                    # Try to get last message from chat
                    if chat.get('messages') and len(chat['messages']) > 0:
                        last_msg = chat['messages'][-1]
                        if last_msg.get('message'):
                            last_message = last_msg['message'].get('conversation') or 'Mídia'
                            last_message_time = datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()
                    
                    # Insert or update chat
                    cursor.execute("SELECT id FROM chats WHERE contact_phone = ? AND instance_id = ?", (phone, instance_id))
                    if cursor.fetchone():
                        cursor.execute("""
                            UPDATE chats SET contact_name = ?, last_message = ?, last_message_time = ?, unread_count = ?
                            WHERE contact_phone = ? AND instance_id = ?
                        """, (contact_name, last_message, last_message_time, unread_count, phone, instance_id))
                    else:
                        chat_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO chats (id, contact_phone, contact_name, instance_id, last_message, last_message_time, unread_count, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (chat_id, phone, contact_name, instance_id, last_message, last_message_time, unread_count, datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()))
                        imported_chats += 1
            
            conn.commit()
            conn.close()
            
            print(f"📦 Lote {batch_number}/{total_batches} processado: {imported_contacts} contatos, {imported_chats} chats - Instância: {instance_id}")
            
            # If this is the last batch, log completion
            if batch_number == total_batches:
                print(f"✅ Importação completa para instância {instance_id}!")
            
            self.send_json_response({
                "success": True, 
                "imported_contacts": imported_contacts,
                "imported_chats": imported_chats,
                "batch": batch_number,
                "total_batches": total_batches
            })
            
        except Exception as e:
            print(f"❌ Erro ao importar chats: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_connect_instance(self, instance_id):
        try:
            # Start Baileys connection for specific instance
            try:
                import requests
                response = requests.post(f'{BAILEYS_URL}/connect/{instance_id}', timeout=5)
                
                if response.status_code == 200:
                    self.send_json_response({"success": True, "message": f"Conexão da instância {instance_id} iniciada"})
                else:
                    self.send_json_response({"error": "Erro ao iniciar conexão"}, 500)
            except ImportError:
                # Fallback usando urllib se requests não estiver disponível
                import urllib.request
                import urllib.error

                try:
                    data = json.dumps({}).encode('utf-8')
                    req = urllib.request.Request(
                        f'http://127.0.0.1:3002/connect/{instance_id}',
                        data=data,
                        headers={'Content-Type': 'application/json'},
                    )

                    req.get_method = lambda: 'POST'

                    with urllib.request.urlopen(req, timeout=5) as response:
                        if response.status == 200:
                            self.send_json_response({"success": True, "message": f"Conexão da instância {instance_id} iniciada"})
                        else:
                            self.send_json_response({"error": "Erro ao iniciar conexão"}, 500)
                except urllib.error.URLError as e:
                    self.send_json_response({"error": f"Serviço WhatsApp indisponível: {str(e)}"}, 500)
                
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_disconnect_instance(self, instance_id):
        try:
            try:
                import requests
                response = requests.post(f'{BAILEYS_URL}/disconnect/{instance_id}', timeout=5)
                
                if response.status_code == 200:
                    # Update database
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE instances SET connected = 0 WHERE id = ?", (instance_id,))
                    conn.commit()
                    conn.close()
                    
                    self.send_json_response({"success": True, "message": f"Instância {instance_id} desconectada"})
                else:
                    self.send_json_response({"error": "Erro ao desconectar"}, 500)
            except ImportError:
                # Fallback usando urllib
                import urllib.request
                data = json.dumps({}).encode('utf-8')
                req = urllib.request.Request(
                    f'http://127.0.0.1:3002/disconnect/{instance_id}',
                    data=data,
                    headers={'Content-Type': 'application/json'},
                )

                req.get_method = lambda: 'POST'
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE instances SET connected = 0 WHERE id = ?", (instance_id,))
                        conn.commit()
                        conn.close()
                        self.send_json_response({"success": True, "message": f"Instância {instance_id} desconectada"})
                    else:
                        self.send_json_response({"error": "Erro ao desconectar"}, 500)
                        
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_whatsapp_status(self, instance_id):
        try:
            try:
                import requests
                response = requests.get(f'{BAILEYS_URL}/status/{instance_id}', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"connected": False, "connecting": False, "instanceId": instance_id})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen(f'{BAILEYS_URL}/status/{instance_id}', timeout=5) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            self.send_json_response(data)
                        else:
                            self.send_json_response({"connected": False, "connecting": False, "instanceId": instance_id})
                except:
                    self.send_json_response({"connected": False, "connecting": False, "instanceId": instance_id})
                
        except Exception as e:
            self.send_json_response({"connected": False, "connecting": False, "error": str(e), "instanceId": instance_id})

    def handle_whatsapp_qr(self, instance_id):
        try:
            try:
                import requests
                response = requests.get(f'{BAILEYS_URL}/qr/{instance_id}', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"qr": None, "connected": False, "instanceId": instance_id})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen(f'{BAILEYS_URL}/qr/{instance_id}', timeout=5) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            self.send_json_response(data)
                        else:
                            self.send_json_response({"qr": None, "connected": False, "instanceId": instance_id})
                except:
                    self.send_json_response({"qr": None, "connected": False, "instanceId": instance_id})
                
        except Exception as e:
            self.send_json_response({"qr": None, "connected": False, "error": str(e), "instanceId": instance_id})

    def handle_get_groups(self, instance_id):
        try:
            try:
                import requests
                try:
                    response = requests.post(
                        f'http://127.0.0.1:3002/send/{instance_id}',
                        json=data, timeout=10
                    )
                except requests.exceptions.RequestException as e:
                    self.send_json_response({"error": "Serviço Baileys indisponível na porta 3002"}, 503)
                    return
                

                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"error": "Erro ao obter grupos"}, response.status_code)
            except ImportError:
                import urllib.request
                req_data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(
                    f'http://127.0.0.1:3002/send/{instance_id}',
                    data=req_data,
                    headers={'Content-Type': 'application/json'},
                )
                req.get_method = lambda: 'POST'
                try:
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.status == 200:
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()

                            message_id = str(uuid.uuid4())
                            phone = to.replace('@s.whatsapp.net', '').replace('@c.us', '')

                            cursor.execute("""
                                INSERT INTO messages (id, contact_name, phone, message, direction, instance_id, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (message_id, f"Para {phone[-4:]}", phone, message, 'outgoing', instance_id,
                                  datetime.now(timezone.utc).isoformat()))

                            conn.commit()
                            conn.close()

                            self.send_json_response({"success": True, "instanceId": instance_id})
                        else:
                            self.send_json_response({"error": "Erro ao enviar mensagem"}, 500)
                except Exception:
                    self.send_json_response({"error": "Serviço Baileys indisponível na porta 3002"}, 503)
                    return
                

        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_whatsapp_connected(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = data.get('instanceId', 'default')
            user = data.get('user', {})
            
            # Update instance connection status
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE instances SET connected = 1, user_name = ?, user_id = ?
                WHERE id = ?
            """, (user.get('name', ''), user.get('id', ''), instance_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ WhatsApp conectado na instância {instance_id}: {user.get('name', user.get('id', 'Unknown'))}")
            self.send_json_response({"success": True, "instanceId": instance_id})
            
        except Exception as e:
            print(f"❌ Erro ao processar conexão: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_receive_message(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract message info
            instance_id = data.get('instanceId', 'default')
            from_jid = data.get('from', '')
            message = data.get('message', '')
            timestamp = data.get('timestamp', datetime.now(BR_TZ).astimezone(timezone.utc).isoformat())
            message_id = data.get('messageId', str(uuid.uuid4()))
            message_type = data.get('messageType', 'text')
            
            # Extract real contact name from WhatsApp data
            contact_name = data.get('pushName', data.get('contactName', ''))
            
            # Clean phone number
            phone = from_jid.replace('@s.whatsapp.net', '').replace('@c.us', '')
            
            # If no name provided, use formatted phone number
            if not contact_name or contact_name == phone:
                formatted_phone = self.format_phone_number(phone)
                contact_name = formatted_phone
            
            # Save message and create/update contact
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Create or update contact with real name
            contact_id = f"{phone}_{instance_id}"
            cursor.execute("""
                INSERT OR REPLACE INTO contacts (id, name, phone, instance_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (contact_id, contact_name, phone, instance_id, timestamp))
            
            # Save message
            msg_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO messages (id, contact_name, phone, message, direction, instance_id, message_type, whatsapp_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (msg_id, contact_name, phone, message, 'incoming', instance_id, message_type, message_id, timestamp))
            
            # Create or update chat conversation
            chat_id = f"{phone}_{instance_id}"
            cursor.execute("""
                INSERT OR REPLACE INTO chats (id, contact_phone, contact_name, instance_id, last_message, last_message_time, unread_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT unread_count FROM chats WHERE id = ?), 0) + 1, ?)
            """, (chat_id, phone, contact_name, instance_id, message[:100], timestamp, chat_id, timestamp))
            
            conn.commit()
            conn.close()
            
            print(f"📥 Mensagem recebida na instância {instance_id}")
            print(f"👤 Contato: {contact_name} ({phone})")
            print(f"💬 Mensagem: {message[:50]}...")
            
            # Broadcast via WebSocket if available
            if WEBSOCKETS_AVAILABLE and websocket_clients:
                asyncio.create_task(broadcast_message({
                    'type': 'new_message',
                    'message': {
                        'id': msg_id,
                        'contact_name': contact_name,
                        'phone': phone,
                        'message': message,
                        'direction': 'incoming',
                        'instance_id': instance_id,
                        'created_at': timestamp
                    }
                }))
            
            self.send_json_response({"success": True, "instanceId": instance_id})
            
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
    def format_phone_number(self, phone):
        """Format phone number for Brazilian display"""
        cleaned = phone.replace('+', '').replace('-', '').replace(' ', '')
        
        if len(cleaned) == 13 and cleaned.startswith('55'):
            # Brazilian format: +55 (11) 99999-9999
            return f"+55 ({cleaned[2:4]}) {cleaned[4:9]}-{cleaned[9:]}"
        elif len(cleaned) == 11:
            # Local format: (11) 99999-9999
            return f"({cleaned[0:2]}) {cleaned[2:7]}-{cleaned[7:]}"
        else:
            # Return as is if format not recognized
            return phone
    
    def handle_get_contacts(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
            contacts = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(contacts)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_get_groups(self, instance_id):
        try:
            import requests
            try:
                response = requests.get(
                    f"http://127.0.0.1:{BAILEYS_PORT}/groups/{instance_id}", timeout=5
                )
            except requests.exceptions.RequestException:
                self.send_json_response({"error": "Serviço Baileys indisponível na porta 3002"}, 503)
                return

            if response.status_code == 200:
                self.send_json_response({"success": True, "groups": response.json()})
            else:
                self.send_json_response({"success": False, "groups": []})
        except ImportError:
            # Fallback to urllib
            import urllib.request
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{BAILEYS_PORT}/groups/{instance_id}", timeout=5
                ) as resp:
                    if resp.status == 200:
                        groups = json.loads(resp.read().decode("utf-8"))
                        self.send_json_response({"success": True, "groups": groups})
                    else:
                        self.send_json_response({"success": False, "groups": []})
            except Exception:
                self.send_json_response({"error": "Serviço Baileys indisponível na porta 3002"}, 503)
    
    def handle_get_chats(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get chats with latest message info
            cursor.execute("""
                SELECT DISTINCT
                    c.phone as contact_phone,
                    c.name as contact_name, 
                    c.instance_id,
                    (SELECT message FROM messages m WHERE m.phone = c.phone ORDER BY m.created_at DESC LIMIT 1) as last_message,
                    (SELECT created_at FROM messages m WHERE m.phone = c.phone ORDER BY m.created_at DESC LIMIT 1) as last_message_time,
                    (SELECT COUNT(*) FROM messages m WHERE m.phone = c.phone AND m.direction = 'incoming') as unread_count
                FROM contacts c
                WHERE EXISTS (SELECT 1 FROM messages m WHERE m.phone = c.phone)
                ORDER BY last_message_time DESC
            """)
            
            chats = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(chats)
            
        except Exception as e:
            print(f"❌ Erro ao buscar chats: {e}")
            self.send_json_response({"error": str(e)}, 500)

    # Campaign handlers
    def handle_get_campaigns(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM campaigns ORDER BY id DESC")
            campaigns = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response({"campaigns": campaigns})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_create_campaign(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length))
            name = data.get('name', 'Campanha')
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO campaigns (name, created_at) VALUES (?, ?)",
                (name, datetime.now(BR_TZ).isoformat()),
            )
            campaign_id = cursor.lastrowid
            conn.commit()
            conn.close()
            self.send_json_response({"id": campaign_id, "name": name})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_set_campaign_groups(self, campaign_id):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length))
            groups = data.get('groups', [])

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM campaign_groups WHERE campaign_id=?", (campaign_id,))
            for item in groups:
                cursor.execute(
                    "INSERT INTO campaign_groups (campaign_id, instance_id, group_id) VALUES (?, ?, ?)",
                    (campaign_id, item.get('instance_id'), item.get('group_id')),
                )
            conn.commit()
            conn.close()
            self.send_json_response({"success": True})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_get_campaign_groups(self, campaign_id):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT instance_id, group_id FROM campaign_groups WHERE campaign_id=?",
                (campaign_id,),
            )
            groups = [dict(instance_id=row[0], group_id=row[1]) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response({"groups": groups})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_add_campaign_message(self, campaign_id):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length))
            schedule_type = data.get('schedule_type', 'daily')
            weekday = data.get('weekday')
            send_time = data.get('send_time')
            message = data.get('message', '')
            media_type = data.get('media_type')
            media_data = data.get('media_data')
            media_path = None
            if media_type and media_data:
                os.makedirs('uploads', exist_ok=True)
                file_name = f"uploads/{uuid.uuid4().hex}"
                with open(file_name, 'wb') as f:
                    f.write(base64.b64decode(media_data))
                media_path = file_name

            next_run = compute_next_run(schedule_type, weekday or 0, send_time)

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO campaign_messages (campaign_id, schedule_type, weekday, send_time, message, media_type, media_path, next_run)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (campaign_id, schedule_type, weekday, send_time, message, media_type, media_path, next_run.isoformat()),
            )
            conn.commit()
            conn.close()
            self.send_json_response({"success": True})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_get_campaign_messages(self, campaign_id):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM campaign_messages WHERE campaign_id=? ORDER BY id DESC",
                (campaign_id,),
            )
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response({"messages": messages})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def handle_get_messages_filtered(self):
        try:
            # Parse query parameters
            query_components = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(query_components.query)
            
            phone = query_params.get('phone', [None])[0]
            instance_id = query_params.get('instance_id', [None])[0]
            
            if not phone:
                self.send_json_response({"error": "Phone parameter required"}, 400)
                return
            
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if instance_id:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE phone = ? AND instance_id = ? 
                    ORDER BY created_at ASC
                """, (phone, instance_id))
            else:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE phone = ? 
                    ORDER BY created_at ASC
                """, (phone,))
            
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            self.send_json_response(messages)
            
        except Exception as e:
            print(f"❌ Erro ao buscar mensagens filtradas: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_send_webhook(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            webhook_url = data.get('url', '')
            webhook_data = data.get('data', {})
            
            if not webhook_url:
                self.send_json_response({"error": "URL do webhook é obrigatória"}, 400)
                return
            
            # Send webhook using urllib (no external dependencies)
            import urllib.request
            import urllib.error
            
            try:
                payload = json.dumps(webhook_data).encode('utf-8')
                req = urllib.request.Request(
                    webhook_url, 
                    data=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'WhatsFlow-Real/1.0'
                    }
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        print(f"✅ Webhook enviado para: {webhook_url}")
                        self.send_json_response({"success": True, "message": "Webhook enviado com sucesso"})
                    else:
                        print(f"⚠️ Webhook retornou status: {response.status}")
                        self.send_json_response({"success": True, "message": f"Webhook enviado (status: {response.status})"})
                        
            except urllib.error.URLError as e:
                print(f"❌ Erro ao enviar webhook: {e}")
                self.send_json_response({"error": f"Erro ao enviar webhook: {str(e)}"}, 500)
                
        except Exception as e:
            print(f"❌ Erro no processamento do webhook: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_get_webhooks(self):
        try:
            # Return a list of configured webhooks
            # For now, return an empty list as this is a placeholder implementation
            webhooks = []
            self.send_json_response(webhooks)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_delete_instance(self, instance_id):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM instances WHERE id = ?", (instance_id,))
            
            if cursor.rowcount == 0:
                conn.close()
                self.send_json_response({"error": "Instance not found"}, 404)
                return
            
            conn.commit()
            conn.close()
            
            self.send_json_response({"message": "Instance deleted successfully"})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    # Flow Management Functions
    def handle_get_flows(self):
        """Get all flows"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM flows 
                ORDER BY created_at DESC
            """)
            
            flows = []
            for row in cursor.fetchall():
                flows.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'nodes': json.loads(row[3]) if row[3] else [],
                    'edges': json.loads(row[4]) if row[4] else [],
                    'active': bool(row[5]),
                    'instance_id': row[6],
                    'created_at': row[7],
                    'updated_at': row[8]
                })
            
            conn.close()
            self.send_json_response(flows)
            
        except Exception as e:
            print(f"❌ Erro ao obter fluxos: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_create_flow(self):
        """Create new flow"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            flow_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO flows (id, name, description, nodes, edges, active, instance_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (flow_id, data['name'], data.get('description', ''), 
                  json.dumps(data.get('nodes', [])), json.dumps(data.get('edges', [])),
                  data.get('active', False), data.get('instance_id'),
                  datetime.now(BR_TZ).astimezone(timezone.utc).isoformat(), datetime.now(BR_TZ).astimezone(timezone.utc).isoformat()))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Fluxo '{data['name']}' criado com ID: {flow_id}")
            self.send_json_response({
                'success': True,
                'flow_id': flow_id,
                'message': f'Fluxo "{data["name"]}" criado com sucesso'
            })
            
        except Exception as e:
            print(f"❌ Erro ao criar fluxo: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_update_flow(self, flow_id):
        """Update flow"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Update only the provided fields
            update_fields = []
            values = []
            
            if 'name' in data:
                update_fields.append('name = ?')
                values.append(data['name'])
                
            if 'description' in data:
                update_fields.append('description = ?')
                values.append(data['description'])
                
            if 'nodes' in data:
                update_fields.append('nodes = ?')
                values.append(json.dumps(data['nodes']))
                
            if 'edges' in data:
                update_fields.append('edges = ?')
                values.append(json.dumps(data['edges']))
                
            if 'active' in data:
                update_fields.append('active = ?')
                values.append(data['active'])
                
            if 'instance_id' in data:
                update_fields.append('instance_id = ?')
                values.append(data['instance_id'])
            
            update_fields.append('updated_at = ?')
            values.append(datetime.now(BR_TZ).astimezone(timezone.utc).isoformat())
            
            values.append(flow_id)
            
            cursor.execute(f"""
                UPDATE flows 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, values)
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                print(f"✅ Fluxo {flow_id} atualizado")
                self.send_json_response({'success': True, 'message': 'Fluxo atualizado com sucesso'})
            else:
                conn.close()
                self.send_json_response({'error': 'Fluxo não encontrado'}, 404)
            
        except Exception as e:
            print(f"❌ Erro ao atualizar fluxo: {e}")
            self.send_json_response({"error": str(e)}, 500)

    def handle_delete_flow(self, flow_id):
        """Delete flow"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM flows WHERE id = ?", (flow_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                print(f"✅ Fluxo {flow_id} excluído")
                self.send_json_response({'success': True, 'message': 'Fluxo excluído com sucesso'})
            else:
                conn.close()
                self.send_json_response({'error': 'Fluxo não encontrado'}, 404)
            
        except Exception as e:
            print(f"❌ Erro ao excluir fluxo: {e}")
            self.send_json_response({"error": str(e)}, 500)

    # Campaign Management Functions
    def handle_get_campaigns(self):
        """Get all campaigns"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, description, recurrence, send_time, weekday, timezone FROM campaigns"
            )
            campaigns = []
            for row in cursor.fetchall():
                campaign_id = row[0]
                cursor.execute(
                    "SELECT group_id FROM campaign_groups WHERE campaign_id = ?",
                    (campaign_id,),
                )
                groups = [g[0] for g in cursor.fetchall()]
                campaigns.append({
                    'id': campaign_id,
                    'name': row[1],
                    'description': row[2],
                    'recurrence': row[3],
                    'send_time': row[4],
                    'weekday': row[5],
                    'timezone': row[6],
                    'groups': groups,
                })
            conn.close()
            self.send_json_response(campaigns)

        except Exception as e:
            print(f"❌ Erro ao obter campanhas: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def handle_get_campaign(self, campaign_id):
        """Get a single campaign"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, name, description, recurrence, send_time, weekday, timezone FROM campaigns WHERE id = ?",
                (campaign_id,),
            )
            row = cursor.fetchone()
            if not row:
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)
                return

            cursor.execute(
                "SELECT group_id FROM campaign_groups WHERE campaign_id = ?",
                (campaign_id,),
            )
            groups = [g[0] for g in cursor.fetchall()]

            campaign = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'recurrence': row[3],
                'send_time': row[4],
                'weekday': row[5],
                'timezone': row[6],
                'groups': groups,
            }

            conn.close()
            self.send_json_response(campaign)

        except Exception as e:
            print(f"❌ Erro ao obter campanha: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def handle_create_campaign(self):
        """Create new campaign"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            campaign_id = str(uuid.uuid4())

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            groups = data.get('groups', [])
            if not isinstance(groups, list):
                conn.close()
                self.send_json_response({'error': 'Grupos inválidos'}, 400)
                return

            send_time = data.get('send_time')
            if send_time:
                try:
                    dt = datetime.fromisoformat(send_time)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=BR_TZ)
                    send_time = dt.astimezone(timezone.utc).isoformat()
                except ValueError:
                    pass
            cursor.execute(
                """
                INSERT INTO campaigns (id, name, description, recurrence, send_time, weekday, timezone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    campaign_id,
                    data['name'],
                    data.get('description'),
                    data.get('recurrence'),
                    data.get('send_time'),
                    data.get('weekday'),
                    data.get('timezone', 'America/Sao_Paulo'),

                ),
            )

            for group_id in groups:
                cursor.execute(
                    "INSERT OR IGNORE INTO campaign_groups (campaign_id, group_id) VALUES (?, ?)",
                    (campaign_id, group_id),
                )

            conn.commit()
            conn.close()

            self.send_json_response({'success': True, 'campaign_id': campaign_id})

        except Exception as e:
            print(f"❌ Erro ao criar campanha: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def handle_update_campaign(self, campaign_id):
        """Update campaign"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            update_fields = []
            values = []

            if 'name' in data:
                update_fields.append('name = ?')
                values.append(data['name'])

            if 'description' in data:
                update_fields.append('description = ?')
                values.append(data['description'])

            if 'recurrence' in data:
                update_fields.append('recurrence = ?')
                values.append(data['recurrence'])

            if 'send_time' in data:
                st = data['send_time']
                try:
                    dt = datetime.fromisoformat(st)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=BR_TZ)
                    st = dt.astimezone(timezone.utc).isoformat()
                except ValueError:
                    pass
                update_fields.append('send_time = ?')
                values.append(st)

            if 'weekday' in data:
                update_fields.append('weekday = ?')
                values.append(data['weekday'])

            if 'timezone' in data:
                update_fields.append('timezone = ?')
                values.append(data['timezone'])

            values.append(campaign_id)
            cursor.execute(
                f"UPDATE campaigns SET {', '.join(update_fields)} WHERE id = ?",
                values,
            )

            if cursor.rowcount == 0:
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)
                return

            if 'groups' in data:
                groups = data['groups']
                if not isinstance(groups, list):
                    conn.close()
                    self.send_json_response({'error': 'Grupos inválidos'}, 400)
                    return
                cursor.execute("DELETE FROM campaign_groups WHERE campaign_id = ?", (campaign_id,))
                for group_id in groups:
                    cursor.execute(
                        "INSERT OR IGNORE INTO campaign_groups (campaign_id, group_id) VALUES (?, ?)",
                        (campaign_id, group_id),
                    )

            conn.commit()
            conn.close()

            self.send_json_response({'success': True})

        except Exception as e:
            print(f"❌ Erro ao atualizar campanha: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def handle_delete_campaign(self, campaign_id):
        """Delete campaign"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM campaign_groups WHERE campaign_id = ?", (campaign_id,))
            cursor.execute("DELETE FROM campaign_messages WHERE campaign_id = ?", (campaign_id,))
            cursor.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))

            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                self.send_json_response({'success': True})
            else:
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)

        except Exception as e:
            print(f"❌ Erro ao excluir campanha: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def handle_get_campaign_groups(self, campaign_id: str) -> None:
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT group_id FROM campaign_groups WHERE campaign_id = ?",
                (campaign_id,),
            )
            groups = [row[0] for row in cursor.fetchall()]
            conn.close()
            self.send_json_response({'campaign_id': campaign_id, 'groups': groups})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_add_campaign_groups(self, campaign_id: str) -> None:
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8')) if length else {}
            groups = data.get('groups', [])
            if not isinstance(groups, list) or not groups:
                self.send_json_response({'error': 'Grupos inválidos'}, 400)
                return
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM campaigns WHERE id = ?", (campaign_id,))
            if not cursor.fetchone():
                conn.close()
                self.send_json_response({'error': 'Campanha não encontrada'}, 404)
                return
            for gid in groups:
                cursor.execute(
                    "INSERT OR IGNORE INTO campaign_groups (campaign_id, group_id) VALUES (?, ?)",
                    (campaign_id, gid),
                )
            conn.commit()
            conn.close()
            self.send_json_response({'success': True})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_send_webhook(self):
        """Send webhook"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            import urllib.request
            
            webhook_data = json.dumps(data['data']).encode()
            req = urllib.request.Request(
                data['url'],
                data=webhook_data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req) as response:
                self.send_json_response({'success': True, 'message': 'Webhook enviado com sucesso'})
                
        except Exception as e:
            print(f"❌ Erro ao enviar webhook: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def check_node_installed():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def main():
    print("🚀 WhatsFlow Professional - Sistema Avançado")
    print("=" * 50)
    print("✅ Python backend com WebSocket")
    print("✅ Node.js + Baileys para WhatsApp real")
    print("✅ Interface profissional moderna")
    print("✅ Tempo real + Design refinado")
    print()
    
    # Check Node.js
    if not check_node_installed():
        print("❌ Node.js não encontrado!")
        print("📦 Para instalar Node.js:")
        print("   Ubuntu: sudo apt install nodejs npm")
        print("   macOS:  brew install node")
        print()
        print("🔧 Continuar mesmo assim? (s/n)")
        if input().lower() != 's':
            return
    else:
        print("✅ Node.js encontrado")
    
    # Initialize database
    print("📁 Inicializando banco de dados...")
    init_db()
    add_sample_data()
    
    # Start WebSocket server
    print("🔌 Iniciando servidor WebSocket...")
    websocket_thread = start_websocket_server()
    
    # Start Baileys service
    print("📱 Iniciando serviço WhatsApp (Baileys)...")
    baileys_manager = BaileysManager()
    
    def signal_handler(sig, frame):
        print("\n🛑 Parando serviços...")
        baileys_manager.stop_baileys()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start Baileys in background
    baileys_thread = threading.Thread(target=baileys_manager.start_baileys)
    baileys_thread.daemon = True
    baileys_thread.start()

    # Start campaign scheduler
    start_campaign_scheduler()
    
    # Start HTTP server in background thread
    server = HTTPServer(('0.0.0.0', PORT), WhatsFlowRealHandler)
    print(f"✅ Servidor rodando na porta {PORT}")
    print("🔗 Pronto para conectar WhatsApp REAL!")
    print(f"🌐 Acesse: http://localhost:{PORT}")
    print("🎉 Sistema profissional pronto para uso!")
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print("✅ WhatsFlow Professional configurado!")
    print(f"🌐 Interface: http://localhost:{PORT}")
    print(f"🔌 WebSocket: ws://localhost:{WEBSOCKET_PORT}")
    print(f"📱 WhatsApp Service: http://localhost:{BAILEYS_PORT}")
    print("🚀 Servidor iniciando...")
    print("   Para parar: Ctrl+C")
    print()

    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\n👋 WhatsFlow Professional finalizado!")
        baileys_manager.stop_baileys()
        server.shutdown()

if __name__ == "__main__":
    main()
