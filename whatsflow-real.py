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
from datetime import datetime, timezone
import os
import subprocess
import sys
import threading
import time
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Configurações
DB_FILE = "whatsflow.db"
PORT = 8889
BAILEYS_PORT = 3002

# HTML da aplicação (mesmo do Pure, mas com conexão real)
HTML_APP = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsFlow Real - Conexão Verdadeira</title>
    <style>
        /* Professional WhatsFlow Design - Improved */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --primary: #128c7e;
            --primary-dark: #075e54;
            --primary-light: #25d366;
            --bg-primary: #f0f2f5;
            --bg-secondary: #ffffff;
            --bg-chat: #e5ddd5;
            --text-primary: #111b21;
            --text-secondary: #667781;
            --border: #e9edef;
            --shadow: 0 1px 3px rgba(11,20,26,.13);
            --shadow-lg: 0 2px 10px rgba(11,20,26,.2);
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }
        
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 2rem; 
        }
        
        /* Header Design */
        .header { 
            text-align: center; 
            color: white; 
            margin-bottom: 3rem;
            padding: 2rem 0;
        }
        .header h1 { 
            font-size: 3rem; 
            font-weight: 800;
            margin-bottom: 1rem; 
            background: linear-gradient(45deg, #ffffff, var(--primary-light));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .header p { 
            font-size: 1.2rem; 
            opacity: 0.9; 
            font-weight: 300;
        }
        .subtitle { 
            background: rgba(37, 211, 102, 0.2); 
            border: 1px solid rgba(37, 211, 102, 0.3);
            padding: 0.75rem 1.5rem; 
            border-radius: 2rem; 
            display: inline-block; 
            margin-top: 1rem; 
            font-size: 0.9rem;
            backdrop-filter: blur(10px);
        }
        
        /* Navigation */
        .nav { 
            display: flex; 
            gap: 0.5rem; 
            margin-bottom: 2rem; 
            flex-wrap: wrap; 
            justify-content: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 1rem;
            backdrop-filter: blur(10px);
        }
        .nav-btn { 
            background: rgba(255, 255, 255, 0.1); 
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 0.75rem 1.5rem; 
            border-radius: 0.75rem; 
            cursor: pointer; 
            font-weight: 500; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: white;
            font-size: 0.9rem;
        }
        .nav-btn:hover { 
            background: rgba(255, 255, 255, 0.2); 
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        .nav-btn.active { 
            background: var(--primary-light); 
            color: white;
            box-shadow: var(--shadow-lg);
        }
        
        /* Cards with better styling */
        .card { 
            background: white; 
            border-radius: 1rem; 
            padding: 2rem; 
            box-shadow: var(--shadow-lg);
            margin-bottom: 2rem;
            border: 1px solid var(--border);
        }
        
        /* Enhanced Conversation/Chat Styles */
        .chat-item {
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .chat-item:hover {
            background: var(--bg-primary);
            transform: translateX(4px);
        }
        .chat-item:last-child {
            border-bottom: none;
        }
        
        .contact-avatar {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1rem;
            flex-shrink: 0;
            box-shadow: var(--shadow);
        }
        .contact-avatar img {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
        }
        
        .chat-info {
            flex: 1;
            min-width: 0;
        }
        .chat-name {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }
        .chat-message {
            color: var(--text-secondary);
            font-size: 0.9rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .chat-time {
            color: var(--text-secondary);
            font-size: 0.8rem;
            flex-shrink: 0;
        }
        
        /* Status Indicators */
        .status-indicator { 
            display: inline-flex; 
            align-items: center; 
            gap: 0.5rem; 
            padding: 0.5rem 1rem; 
            border-radius: 2rem; 
            font-weight: 500;
            font-size: 0.9rem;
        }
        .status-connected { 
            background: rgba(37, 211, 102, 0.1); 
            color: var(--primary-light);
            border: 1px solid rgba(37, 211, 102, 0.2);
        }
        .status-disconnected { 
            background: rgba(239, 68, 68, 0.1); 
            color: #dc2626;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
        .status-connecting { 
            background: rgba(245, 158, 11, 0.1); 
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
        .status-dot { 
            width: 8px; 
            height: 8px; 
            border-radius: 50%; 
        }
        .status-connected .status-dot { background: var(--primary-light); }
        .status-disconnected .status-dot { background: #dc2626; }
        .status-connecting .status-dot { 
            background: #f59e0b; 
            animation: pulse 2s infinite; 
        }
        
        /* Stats Grid */
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 1.5rem; 
            margin: 2rem 0; 
        }
        .stat-card { 
            text-align: center; 
            padding: 2rem; 
            background: linear-gradient(135deg, var(--bg-primary) 0%, white 100%);
            border-radius: 1rem; 
            border: 1px solid var(--border);
            transition: all 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }
        .stat-number { 
            font-size: 2.5rem; 
            font-weight: 800; 
            color: var(--primary); 
            margin-bottom: 0.5rem; 
        }
        .stat-label { 
            color: var(--text-secondary); 
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        /* Instance Cards */
        .instances-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 1.5rem; 
        }
        .instance-card { 
            border: 2px solid var(--border); 
            border-radius: 1rem; 
            padding: 1.5rem; 
            background: white; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .instance-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--border);
            transition: all 0.3s ease;
        }
        .instance-card:hover { 
            transform: translateY(-4px); 
            box-shadow: var(--shadow-lg);
            border-color: var(--primary);
        }
        .instance-card:hover::before {
            background: var(--primary);
        }
        .instance-card.connected { 
            border-color: var(--primary-light); 
            background: linear-gradient(135deg, rgba(37, 211, 102, 0.02) 0%, white 100%);
        }
        .instance-card.connected::before {
            background: var(--primary-light);
        }
        
        /* Buttons */
        .btn { 
            padding: 0.75rem 1.5rem; 
            border: none; 
            border-radius: 0.75rem; 
            cursor: pointer; 
            font-weight: 600; 
            font-size: 0.9rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        .btn-primary { 
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); 
            color: white;
            box-shadow: var(--shadow);
        }
        .btn-success { 
            background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%); 
            color: white;
            box-shadow: var(--shadow);
        }
        .btn-danger { 
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); 
            color: white;
            box-shadow: var(--shadow);
        }
        .btn-secondary {
            background: var(--bg-primary);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: var(--shadow-lg);
        }
        .btn:disabled { 
            opacity: 0.5; 
            cursor: not-allowed; 
            transform: none;
        }
        
        /* Modal */
        .modal { 
            display: none; 
            position: fixed; 
            top: 0; 
            left: 0; 
            right: 0; 
            bottom: 0; 
            background: rgba(17, 24, 39, 0.75); 
            backdrop-filter: blur(4px);
            z-index: 1000; 
            align-items: center; 
            justify-content: center; 
        }
        .modal.show { display: flex; }
        .modal-content { 
            background: white; 
            padding: 2rem; 
            border-radius: 1.5rem; 
            width: 90%; 
            max-width: 500px; 
            position: relative; 
            z-index: 1002;
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--border);
        }
        .modal-content * { position: relative; z-index: 1003; }
        .modal-content input, .modal-content button { pointer-events: all; }
        .modal { pointer-events: all; }
        .modal-content { pointer-events: all; }
        
        /* Forms */
        .form-input { 
            width: 100%; 
            padding: 1rem; 
            border: 2px solid var(--border); 
            border-radius: 0.75rem; 
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        .form-input:focus { 
            outline: none; 
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(18, 140, 126, 0.1);
        }
        
        /* Empty State */
        .empty-state { 
            text-align: center; 
            padding: 4rem 2rem; 
            color: var(--text-secondary); 
        }
        .empty-icon { 
            font-size: 4rem; 
            margin-bottom: 1.5rem; 
            opacity: 0.5; 
        }
        .empty-title { 
            font-size: 1.5rem; 
            font-weight: 600; 
            color: var(--text-primary); 
            margin-bottom: 0.5rem; 
        }
        
        /* Section Management */
        .section { display: none; }
        .section.active { display: block; }
        
        /* Messages */
        .success-message { 
            background: rgba(37, 211, 102, 0.1); 
            color: var(--primary-light); 
            padding: 1rem; 
            border-radius: 0.75rem; 
            margin: 1.5rem 0; 
            text-align: center; 
            font-weight: 500;
            border: 1px solid rgba(37, 211, 102, 0.2);
        }
        
        /* QR Code Container */
        .qr-container { 
            text-align: center; 
            margin: 2rem 0; 
        }
        .qr-code { 
            background: white; 
            padding: 2rem; 
            border-radius: 1rem; 
            box-shadow: var(--shadow-lg);
            display: inline-block;
            border: 1px solid var(--border);
        }
        
        /* Additional styles for existing elements */
        .real-connection-badge { 
            background: var(--primary-light); 
            color: white; 
            padding: 1rem 1.5rem; 
            border-radius: 0.75rem; 
            margin: 1.5rem 0; 
            text-align: center; 
            font-weight: 600;
            box-shadow: var(--shadow);
        }
        
        .qr-instructions { 
            background: var(--bg-primary); 
            padding: 1.5rem; 
            border-radius: 0.75rem; 
            margin-bottom: 1.5rem; 
            text-align: left;
            border: 1px solid var(--border);
        }
        
        .connected-user { 
            background: rgba(37, 211, 102, 0.1); 
            padding: 1rem; 
            border-radius: 0.75rem; 
            margin: 1rem 0; 
            border: 2px solid var(--primary-light);
        }
        
        .loading { 
            text-align: center; 
            padding: 2.5rem; 
            color: var(--text-secondary); 
        }
        .loading-spinner { 
            font-size: 2rem; 
            margin-bottom: 1rem; 
            animation: pulse 1s infinite; 
        }
        
        /* Animations */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .header h1 { font-size: 2rem; }
            .nav { padding: 0.5rem; }
            .stats-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
            .instances-grid { grid-template-columns: 1fr; }
            .modal-content { margin: 1rem; width: calc(100% - 2rem); }
        }
        
        /* Loading States */
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            color: var(--text-secondary);
        }
        
        .loading-spinner {
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 WhatsFlow Real</h1>
            <p>Sistema de Automação WhatsApp - Conexão Verdadeira</p>
            <div class="subtitle">✅ Baileys integrado • WhatsApp real • Mensagens reais</div>
        </div>
        
        <nav class="nav">
            <button class="nav-btn active" onclick="showSection('dashboard')">📊 Dashboard</button>
            <button class="nav-btn" onclick="showSection('instances')">📱 Instâncias</button>
            <button class="nav-btn" onclick="showSection('contacts')">👥 Contatos</button>
            <button class="nav-btn" onclick="showSection('messages')">💬 Mensagens</button>
            <button class="nav-btn" onclick="showSection('info')">ℹ️ Info</button>
        </nav>
        
        <div id="dashboard" class="section active">
            <div class="card">
                <h2>🔗 Status da Conexão WhatsApp</h2>
                <div id="connection-status" class="status-indicator status-disconnected">
                    <div class="status-dot"></div>
                    <span>Verificando conexão...</span>
                </div>
                <div class="real-connection-badge">
                    🚀 Conexão REAL com WhatsApp via Baileys
                </div>
                <div id="connected-user-info" style="display: none;"></div>
            </div>
            
            <div class="card">
                <h2>📊 Estatísticas do Sistema</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="contacts-count">0</div>
                        <div class="stat-label">Contatos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="conversations-count">0</div>
                        <div class="stat-label">Conversas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="messages-count">0</div>
                        <div class="stat-label">Mensagens</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="instances" class="section">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>📱 Instâncias WhatsApp</h2>
                    <button class="btn btn-primary" onclick="showCreateModal()">➕ Nova Instância</button>
                </div>
                <div id="instances-container" class="instances-grid">
                    <div style="text-align: center; padding: 40px;">Carregando...</div>
                </div>
            </div>
        </div>
        
        <!-- Contacts Section -->
        <div id="contacts" class="section">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>👥 Central de Contatos</h2>
                    <button class="btn btn-primary" onclick="loadContacts()">🔄 Atualizar</button>
                </div>
                <div id="contacts-container">
                    <div class="loading">
                        <div class="loading-spinner">🔄</div>
                        <p>Carregando contatos...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Messages Section -->
        <div id="messages" class="section">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>💬 Central de Mensagens</h2>
                    <button class="btn btn-primary" onclick="loadMessages()">🔄 Atualizar</button>
                </div>
                
                <div style="display: grid; grid-template-columns: 300px 1fr; gap: 20px; height: 500px;">
                    <!-- Chat List -->
                    <div style="border-right: 1px solid #eee; padding-right: 15px;">
                        <h3>Conversas Ativas</h3>
                        <div id="chat-list" style="height: 450px; overflow-y: auto;">
                            <div class="loading">
                                <div class="loading-spinner">🔄</div>
                                <p>Carregando conversas...</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Chat Window -->
                    <div id="chat-window" style="display: flex; flex-direction: column;">
                        <div id="chat-header" style="padding: 10px; border-bottom: 1px solid #eee; display: none;">
                            <h4 id="chat-contact-name">Selecione uma conversa</h4>
                            <p id="chat-contact-phone" style="color: #666; margin: 0;"></p>
                        </div>
                        
                        <div id="messages-container" style="flex: 1; padding: 15px; overflow-y: auto; background: #f9f9f9;">
                            <div style="text-align: center; color: #666; margin-top: 100px;">
                                <p>📱 Selecione uma conversa para ver as mensagens</p>
                            </div>
                        </div>
                        
                        <div id="message-input-area" style="padding: 15px; border-top: 1px solid #eee; display: none;">
                            <div style="display: flex; gap: 10px;">
                                <input type="text" id="message-input" placeholder="Digite sua mensagem..." 
                                       style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"
                                       onkeypress="if(event.key==='Enter') sendMessage()">
                                <button class="btn btn-primary" onclick="sendMessage()">📤 Enviar</button>
                                <button class="btn btn-secondary" onclick="sendWebhook()" title="Enviar Webhook">
                                    🔗 Webhook
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="info" class="section">
            <div class="card">
                <h2>ℹ️ WhatsFlow Real</h2>
                <p><strong>🐍 Backend:</strong> Python puro (servidor HTTP)</p>
                <p><strong>📱 WhatsApp:</strong> Baileys (Node.js) - conexão real</p>
                <p><strong>🗄️ Banco:</strong> SQLite local</p>
                <p><strong>🌐 Interface:</strong> HTML + CSS + JS</p>
                <p><strong>🔧 Requisitos:</strong> Python 3 + Node.js</p>
                
                <h3 style="margin: 20px 0 10px 0;">🔗 Como funciona:</h3>
                <p>1. <strong>Python</strong> roda a interface web e banco de dados</p>
                <p>2. <strong>Node.js + Baileys</strong> conecta com WhatsApp real</p>
                <p>3. <strong>Comunicação</strong> entre os dois via HTTP</p>
                <p>4. <strong>QR Code real</strong> para conectar seu WhatsApp</p>
                <p>5. <strong>Mensagens reais</strong> enviadas e recebidas</p>
            </div>
        </div>
    </div>
    
    <div id="createModal" class="modal">
        <div class="modal-content">
            <h3>➕ Nova Instância WhatsApp</h3>
            <form onsubmit="createInstance(event)">
                <div style="margin: 20px 0;">
                    <input type="text" id="instanceName" class="form-input" 
                           placeholder="Nome da instância" required>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="button" class="btn" onclick="hideCreateModal()">Cancelar</button>
                    <button type="submit" class="btn btn-success" style="flex: 1;">Criar</button>
                </div>
            </form>
        </div>
    </div>
    
    <div id="qrModal" class="modal">
        <div class="modal-content">
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <h3>📱 Conectar WhatsApp Real - <span id="qr-instance-name">Instância</span></h3>
                <button onclick="closeQRModal()" style="background: none; border: none; font-size: 20px; cursor: pointer;">&times;</button>
            </div>
            
            <div id="connection-status" style="text-align: center; margin-bottom: 15px; font-weight: bold;">
                ⏳ Preparando conexão...
            </div>
            
            <div class="qr-instructions">
                <h4>📲 Como conectar seu WhatsApp:</h4>
                <ol>
                    <li>Abra o <strong>WhatsApp</strong> no seu celular</li>
                    <li>Toque em <strong>Configurações ⚙️</strong></li>
                    <li>Toque em <strong>Aparelhos conectados</strong></li>
                    <li>Toque em <strong>Conectar um aparelho</strong></li>
                    <li><strong>Escaneie o QR Code</strong> abaixo</li>
                </ol>
            </div>
            
            <div id="qr-code-container" class="qr-container">
                <div id="qr-loading" style="text-align: center; padding: 40px;">
                    <div style="font-size: 2rem; margin-bottom: 15px;">⏳</div>
                    <p>Gerando QR Code real...</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <button class="btn btn-danger" onclick="closeQRModal()">🚫 Fechar</button>
            </div>
        </div>
    </div>

    <script>
        let instances = [];
        let currentInstanceId = null;
        let qrPollingInterval = null;
        let statusPollingInterval = null;

        function showSection(name) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            event.target.classList.add('active');
            
            if (name === 'instances') loadInstances();
            if (name === 'dashboard') loadStats();
            if (name === 'contacts') loadContacts();
            if (name === 'messages') loadMessages();
        }

        function showCreateModal() {
            document.getElementById('createModal').classList.add('show');
        }

        function hideCreateModal() {
            document.getElementById('createModal').classList.remove('show');
            document.getElementById('instanceName').value = '';
        }

        let qrInterval = null;
        let currentQRInstance = null;

        async function showQRModal(instanceId) {
            console.log('🔄 Showing QR modal for instance:', instanceId);
            currentQRInstance = instanceId;
            
            // Check if elements exist before setting text
            const instanceNameEl = document.getElementById('qr-instance-name');
            if (instanceNameEl) {
                instanceNameEl.textContent = instanceId;
                console.log('✅ Instance name set');
            } else {
                console.error('❌ qr-instance-name element not found');
            }
            
            const modalEl = document.getElementById('qrModal');
            if (modalEl) {
                modalEl.classList.add('show');
                console.log('✅ Modal shown');
            } else {
                console.error('❌ qrModal element not found');
            }
            
            // Start QR polling
            loadQRCode();
            qrInterval = setInterval(loadQRCode, 3000); // Check every 3 seconds
        }

        async function loadQRCode() {
            if (!currentQRInstance) return;
            
            try {
                const [statusResponse, qrResponse] = await Promise.all([
                    fetch(`/api/whatsapp/status/${currentQRInstance}`),
                    fetch(`/api/whatsapp/qr/${currentQRInstance}`)
                ]);
                
                const status = await statusResponse.json();
                const qrData = await qrResponse.json();
                
                const qrContainer = document.getElementById('qr-code-container');
                const statusElement = document.getElementById('connection-status');
                
                if (status.connected && status.user) {
                    // Connected - show success
                    qrContainer.innerHTML = `
                        <div style="text-align: center; padding: 40px;">
                            <div style="font-size: 4em; margin-bottom: 20px;">✅</div>
                            <h3 style="color: #28a745; margin-bottom: 10px;">WhatsApp Conectado!</h3>
                            <p style="color: #666; margin-bottom: 10px;">Usuário: <strong>${status.user.name}</strong></p>
                            <p style="color: #666; margin-bottom: 20px;">Telefone: <strong>${status.user.phone || status.user.id.split(':')[0]}</strong></p>
                            <div style="margin-bottom: 20px;">
                                <button class="btn btn-success" onclick="closeQRModal()">🎉 Continuar</button>
                            </div>
                            <p style="font-size: 0.9em; color: #999;">Suas conversas serão importadas automaticamente</p>
                        </div>
                    `;
                    statusElement.textContent = '✅ Conectado e sincronizando conversas...';
                    statusElement.style.color = '#28a745';
                    
                    // Stop polling and reload conversations after 5 seconds
                    if (qrInterval) {
                        clearInterval(qrInterval);
                        qrInterval = null;
                    }
                    
                    // Auto-close modal and refresh data after showing success
                    setTimeout(() => {
                        closeQRModal();
                        // Refresh instance list and load conversations
                        if (document.getElementById('instances').style.display !== 'none') {
                            loadInstances();
                        }
                        // Load messages if on messages tab
                        if (document.getElementById('messages').style.display !== 'none') {
                            loadMessages();
                        }
                        // Load contacts if on contacts tab
                        if (document.getElementById('contacts').style.display !== 'none') {
                            loadContacts();
                        }
                    }, 3000);
                    
                } else if (status.connecting && qrData.qr) {
                    // Show QR code with expiration timer
                    const expiresIn = qrData.expiresIn || 60;
                    qrContainer.innerHTML = `
                        <div style="text-align: center;">
                            <img src="https://api.qrserver.com/v1/create-qr-code/?size=280x280&data=${encodeURIComponent(qrData.qr)}" 
                                 alt="QR Code" style="max-width: 280px; max-height: 280px; border: 2px solid #28a745; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                            <p style="margin-top: 15px; color: #666; font-weight: bold;">Escaneie o QR Code com seu WhatsApp</p>
                            <p style="font-size: 0.9em; color: #999; margin-bottom: 15px;">QR Code válido por ${expiresIn} segundos</p>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px;">
                                <p style="margin: 0; font-size: 0.9em; color: #666;">
                                    💡 <strong>Dica:</strong> Abra WhatsApp → Configurações → Aparelhos conectados → Conectar aparelho
                                </p>
                            </div>
                        </div>
                    `;
                    statusElement.textContent = '📱 Aguardando escaneamento do QR Code...';
                    statusElement.style.color = '#007bff';
                    
                } else if (status.connecting) {
                    // Connecting but no QR yet
                    qrContainer.innerHTML = `
                        <div style="text-align: center; padding: 40px;">
                            <div class="loading-spinner" style="font-size: 3em; margin-bottom: 20px;">🔄</div>
                            <p style="color: #666;">Preparando conexão WhatsApp...</p>
                            <p style="font-size: 0.9em; color: #999;">QR Code será gerado em instantes</p>
                        </div>
                    `;
                    statusElement.textContent = '⏳ Preparando conexão...';
                    statusElement.style.color = '#ffc107';
                    
                } else {
                    // Not connected, not connecting
                    qrContainer.innerHTML = `
                        <div style="text-align: center; padding: 40px;">
                            <div style="font-size: 3em; margin-bottom: 20px;">📱</div>
                            <p style="color: #666; margin-bottom: 20px;">Instância não conectada</p>
                            <button class="btn btn-primary" onclick="connectInstance('${currentQRInstance}')">
                                🔗 Iniciar Conexão
                            </button>
                            <p style="font-size: 0.9em; color: #999; margin-top: 15px;">Clique para gerar um novo QR Code</p>
                        </div>
                    `;
                    statusElement.textContent = '❌ Desconectado';
                    statusElement.style.color = '#dc3545';
                }
                
            } catch (error) {
                console.error('Erro ao carregar QR code:', error);
                document.getElementById('qr-code-container').innerHTML = `
                    <div style="text-align: center; padding: 40px; color: red;">
                        <div style="font-size: 3em; margin-bottom: 20px;">❌</div>
                        <p>Erro ao carregar status da conexão</p>
                        <button class="btn btn-primary" onclick="loadQRCode()" style="margin-top: 15px;">🔄 Tentar Novamente</button>
                    </div>
                `;
                document.getElementById('connection-status').textContent = '❌ Erro de comunicação';
                document.getElementById('connection-status').style.color = '#dc3545';
            }
        }

        function closeQRModal() {
            document.getElementById('qrModal').classList.remove('show');
            currentQRInstance = null;
            
            // Stop QR polling
            if (qrInterval) {
                clearInterval(qrInterval);
                qrInterval = null;
            }
            
            // Reload instances to update status
            if (document.getElementById('instances').style.display !== 'none') {
                loadInstances();
            }
        }

        async function loadInstances() {
            try {
                const response = await fetch('/api/instances');
                instances = await response.json();
                renderInstances();
            } catch (error) {
                document.getElementById('instances-container').innerHTML = 
                    '<div class="empty-state"><div class="empty-icon">❌</div><div class="empty-title">Erro ao carregar</div></div>';
            }
        }

        async function createInstance(event) {
            event.preventDefault();
            const name = document.getElementById('instanceName').value;
            
            try {
                const response = await fetch('/api/instances', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name })
                });
                
                if (response.ok) {
                    hideCreateModal();
                    loadInstances();
                    // Show both alert and console log for debugging
                    console.log(`✅ Instância "${name}" criada com sucesso!`);
                    alert(`✅ Instância "${name}" criada!`);
                } else {
                    console.error('❌ Response not OK:', response.status);
                    alert('❌ Erro: Resposta inválida do servidor');
                }
            } catch (error) {
                console.error('❌ Erro ao criar instância:', error);
                alert('❌ Erro ao criar instância: ' + error.message);
            }
        }

        async function connectInstance(instanceId) {
            console.log('🔄 Connecting instance:', instanceId);
            try {
                const response = await fetch(`/api/instances/${instanceId}/connect`, {
                    method: 'POST'
                });
                
                console.log('Response status:', response.status);
                
                if (response.ok) {
                    console.log('✅ Connection started, opening QR modal');
                    showQRModal(instanceId);
                } else {
                    console.error('❌ Connection failed:', response.status);
                    alert('❌ Erro ao iniciar conexão');
                }
            } catch (error) {
                console.error('❌ Connection error:', error);
                alert('❌ Erro de conexão');
            }
        }

        async function deleteInstance(id, name) {
            if (!confirm(`Excluir "${name}"?`)) return;
            
            try {
                const response = await fetch(`/api/instances/${id}`, { method: 'DELETE' });
                if (response.ok) {
                    loadInstances();
                    alert(`✅ "${name}" excluída!`);
                }
            } catch (error) {
                alert('❌ Erro ao excluir');
            }
        }

        async function showQRCode(instanceId) {
            showQRModal(instanceId);
        }

        async function disconnectInstance(instanceId) {
            if (!confirm('Desconectar esta instância?')) return;
            
            try {
                const response = await fetch(`/api/instances/${instanceId}/disconnect`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    loadInstances();
                    alert('✅ Instância desconectada!');
                } else {
                    alert('❌ Erro ao desconectar');
                }
            } catch (error) {
                alert('❌ Erro de conexão');
            }
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('contacts-count').textContent = stats.contacts_count || 0;
                document.getElementById('conversations-count').textContent = stats.conversations_count || 0;
                document.getElementById('messages-count').textContent = stats.messages_count || 0;
            } catch (error) {
                console.error('Error loading stats');
            }
        }

        async function loadMessages() {
            try {
                // Load chat list
                const chatsResponse = await fetch('/api/chats');
                const chats = await chatsResponse.json();
                
                const chatList = document.getElementById('chat-list');
                if (chats.length === 0) {
                    chatList.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-icon">💬</div>
                            <div class="empty-title">Nenhuma conversa</div>
                            <p>As conversas aparecerão aqui quando receber mensagens</p>
                        </div>
                    `;
                } else {
                    chatList.innerHTML = chats.map(chat => `
                        <div class="chat-item" onclick="openChat('${chat.contact_phone}', '${chat.contact_name}', '${chat.instance_id}')"
                             style="padding: 12px; border-bottom: 1px solid #eee; cursor: pointer; hover: background: #f5f5f5;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div class="contact-avatar" style="width: 40px; height: 40px; border-radius: 50%; background: #007bff; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                                    ${chat.contact_name.charAt(0).toUpperCase()}
                                </div>
                                <div style="flex: 1;">
                                    <div style="font-weight: bold; margin-bottom: 2px;">${chat.contact_name}</div>
                                    <div style="color: #666; font-size: 0.9em; truncate: ellipsis;">${chat.last_message || 'Nova conversa'}</div>
                                </div>
                                ${chat.unread_count > 0 ? `<div class="unread-badge" style="background: #007bff; color: white; border-radius: 50%; padding: 2px 6px; font-size: 0.8em;">${chat.unread_count}</div>` : ''}
                            </div>
                        </div>
                    `).join('');
                }
                
            } catch (error) {
                console.error('Erro ao carregar mensagens:', error);
                document.getElementById('chat-list').innerHTML = `
                    <div class="error-state">
                        <p>❌ Erro ao carregar conversas</p>
                        <button class="btn btn-sm btn-primary" onclick="loadMessages()">Tentar novamente</button>
                    </div>
                `;
            }
        }

        let currentChat = null;

        async function openChat(phone, contactName, instanceId) {
            currentChat = { phone, contactName, instanceId };
            
            // Update chat header
            document.getElementById('chat-contact-name').textContent = contactName;
            document.getElementById('chat-contact-phone').textContent = phone;
            document.getElementById('chat-header').style.display = 'block';
            document.getElementById('message-input-area').style.display = 'block';
            
            // Load messages for this chat
            try {
                const response = await fetch(`/api/messages?phone=${phone}&instance_id=${instanceId}`);
                const messages = await response.json();
                
                const messagesContainer = document.getElementById('messages-container');
                if (messages.length === 0) {
                    messagesContainer.innerHTML = `
                        <div style="text-align: center; color: #666; margin-top: 100px;">
                            <p>💬 Nenhuma mensagem ainda</p>
                            <p>Comece uma conversa!</p>
                        </div>
                    `;
                } else {
                    messagesContainer.innerHTML = messages.map(msg => `
                        <div class="message ${msg.direction}" style="margin-bottom: 15px; display: flex; ${msg.direction === 'outgoing' ? 'justify-content: flex-end' : 'justify-content: flex-start'};">
                            <div class="message-bubble" style="max-width: 70%; padding: 10px 15px; border-radius: 15px; ${msg.direction === 'outgoing' ? 'background: #007bff; color: white; border-bottom-right-radius: 5px;' : 'background: white; border: 1px solid #ddd; border-bottom-left-radius: 5px;'}">
                                <div class="message-text">${msg.message}</div>
                                <div class="message-time" style="font-size: 0.8em; margin-top: 5px; opacity: 0.7;">
                                    ${new Date(msg.created_at).toLocaleTimeString()}
                                </div>
                            </div>
                        </div>
                    `).join('');
                    
                    // Scroll to bottom
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
                
            } catch (error) {
                console.error('Erro ao carregar mensagens:', error);
                document.getElementById('messages-container').innerHTML = `
                    <div style="text-align: center; color: red; margin-top: 100px;">
                        <p>❌ Erro ao carregar mensagens</p>
                    </div>
                `;
            }
        }

        async function sendMessage() {
            if (!currentChat) return;
            
            const messageInput = document.getElementById('message-input');
            const message = messageInput.value.trim();
            
            if (!message) return;
            
            try {
                const response = await fetch(`/api/messages/send/${currentChat.instanceId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        to: currentChat.phone,
                        message: message
                    })
                });
                
                if (response.ok) {
                    messageInput.value = '';
                    
                    // Add message to UI immediately
                    const messagesContainer = document.getElementById('messages-container');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message outgoing';
                    messageDiv.style.cssText = 'margin-bottom: 15px; display: flex; justify-content: flex-end;';
                    messageDiv.innerHTML = `
                        <div class="message-bubble" style="max-width: 70%; padding: 10px 15px; border-radius: 15px; background: #007bff; color: white; border-bottom-right-radius: 5px;">
                            <div class="message-text">${message}</div>
                            <div class="message-time" style="font-size: 0.8em; margin-top: 5px; opacity: 0.7;">
                                ${new Date().toLocaleTimeString()}
                            </div>
                        </div>
                    `;
                    messagesContainer.appendChild(messageDiv);
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    
                } else {
                    alert('❌ Erro ao enviar mensagem');
                }
                
            } catch (error) {
                console.error('Erro ao enviar mensagem:', error);
                alert('❌ Erro de conexão');
            }
        }

        async function sendWebhook() {
            if (!currentChat) {
                alert('❌ Selecione uma conversa primeiro');
                return;
            }
            
            const webhookUrl = prompt('URL do Webhook:', 'https://webhook.site/your-webhook-url');
            if (!webhookUrl) return;
            
            try {
                const chatData = {
                    contact_name: currentChat.contactName,
                    contact_phone: currentChat.phone,
                    instance_id: currentChat.instanceId,
                    timestamp: new Date().toISOString()
                };
                
                const response = await fetch('/api/webhooks/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        url: webhookUrl,
                        data: chatData
                    })
                });
                
                if (response.ok) {
                    alert('✅ Webhook enviado com sucesso!');
                } else {
                    alert('❌ Erro ao enviar webhook');
                }
                
            } catch (error) {
                console.error('Erro ao enviar webhook:', error);
                alert('❌ Erro de conexão');
            }
        }

        async function loadContacts() {
            try {
                const response = await fetch('/api/contacts');
                const contacts = await response.json();
                renderContacts(contacts);
            } catch (error) {
                console.error('Error loading contacts');
                document.getElementById('contacts-container').innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">❌</div>
                        <div class="empty-title">Erro ao carregar contatos</div>
                        <p>Tente novamente em alguns instantes</p>
                    </div>
                `;
            }
        }

        function renderMessages(messages) {
            const container = document.getElementById('messages-container');
            if (!messages || messages.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">💬</div>
                        <div class="empty-title">Nenhuma mensagem ainda</div>
                        <p>As mensagens do WhatsApp aparecerão aqui quando começar a receber</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = messages.map(msg => `
                <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin: 10px 0;">
                    <div style="font-weight: 600;">${msg.from}</div>
                    <div style="color: #6b7280; font-size: 12px; margin: 5px 0;">${new Date(msg.timestamp).toLocaleString()}</div>
                    <div>${msg.message}</div>
                </div>
            `).join('');
        }

        function renderContacts(contacts) {
            const container = document.getElementById('contacts-container');
            if (!contacts || contacts.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">👥</div>
                        <div class="empty-title">Nenhum contato ainda</div>
                        <p>Os contatos aparecerão aqui quando começar a receber mensagens</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = contacts.map(contact => `
                <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin: 10px 0; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #1f2937;">${contact.name}</div>
                        <div style="color: #6b7280; font-size: 14px;">📱 ${contact.phone}</div>
                        <div style="color: #9ca3af; font-size: 12px;">Adicionado: ${new Date(contact.created_at).toLocaleDateString()}</div>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-primary" onclick="startChat('${contact.phone}', '${contact.name}')" style="padding: 8px 12px; font-size: 12px;">💬 Conversar</button>
                    </div>
                </div>
            `).join('');
        }

        function startChat(phone, name) {
            const message = prompt(`💬 Enviar mensagem para ${name} (${phone}):`);
            if (message && message.trim()) {
                sendMessage(phone, message.trim());
            }
        }

        async function sendMessage(phone, message) {
            try {
                const response = await fetch('http://localhost:3002/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ to: phone, message: message })
                });
                
                if (response.ok) {
                    alert('✅ Mensagem enviada com sucesso!');
                } else {
                    const error = await response.json();
                    alert(`❌ Erro ao enviar: ${error.error || 'Erro desconhecido'}`);
                }
            } catch (error) {
                alert('❌ Erro de conexão ao enviar mensagem');
                console.error('Send error:', error);
            }
        }

        async function checkConnectionStatus() {
            try {
                const response = await fetch('/api/whatsapp/status');
                const status = await response.json();
                
                const statusEl = document.getElementById('connection-status');
                const userInfoEl = document.getElementById('connected-user-info');
                
                if (status.connected) {
                    statusEl.className = 'status-indicator status-connected';
                    statusEl.innerHTML = '<div class="status-dot"></div><span>WhatsApp conectado</span>';
                    
                    if (status.user) {
                        userInfoEl.style.display = 'block';
                        userInfoEl.innerHTML = `
                            <div class="connected-user">
                                <strong>👤 Usuário conectado:</strong><br>
                                📱 ${status.user.name || status.user.id}<br>
                                📞 ${status.user.id}
                            </div>
                        `;
                    }
                } else if (status.connecting) {
                    statusEl.className = 'status-indicator status-connecting';
                    statusEl.innerHTML = '<div class="status-dot"></div><span>Conectando WhatsApp...</span>';
                    userInfoEl.style.display = 'none';
                } else {
                    statusEl.className = 'status-indicator status-disconnected';
                    statusEl.innerHTML = '<div class="status-dot"></div><span>WhatsApp desconectado</span>';
                    userInfoEl.style.display = 'none';
                }
                
                // Update instances with connection status
                loadInstances();
                
            } catch (error) {
                console.error('Error checking status:', error);
            }
        }

        async function startQRPolling() {
            const container = document.getElementById('qr-container');
            
            qrPollingInterval = setInterval(async () => {
                try {
                    const response = await fetch('/api/whatsapp/qr');
                    const data = await response.json();
                    
                    if (data.qr) {
                        container.innerHTML = `
                            <div class="qr-code">
                                <img src="https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodeURIComponent(data.qr)}" 
                                     alt="QR Code WhatsApp" style="border-radius: 8px;">
                            </div>
                            <p style="margin-top: 15px; color: #10b981; font-weight: 500;">✅ QR Code real gerado! Escaneie com seu WhatsApp</p>
                        `;
                    } else if (data.connected) {
                        hideQRModal();
                        alert('🎉 WhatsApp conectado com sucesso!');
                        checkConnectionStatus();
                    } else {
                        container.innerHTML = `
                            <div style="text-align: center; padding: 40px;">
                                <div style="font-size: 2rem; margin-bottom: 15px;">⏳</div>
                                <p>Aguardando QR Code...</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    console.error('Error polling QR:', error);
                }
            }, 2000);
        }

        function renderInstances() {
            const container = document.getElementById('instances-container');
            
            if (!instances || instances.length === 0) {
                container.innerHTML = `
                    <div class="empty-state" style="grid-column: 1 / -1;">
                        <div class="empty-icon">📱</div>
                        <div class="empty-title">Nenhuma instância</div>
                        <p>Crie sua primeira instância WhatsApp para começar</p>
                        <br>
                        <button class="btn btn-primary" onclick="showCreateModal()">🚀 Criar Primeira Instância</button>
                    </div>
                `;
                return;
            }

            container.innerHTML = instances.map(instance => `
                <div class="instance-card ${instance.connected ? 'connected' : ''}">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                        <div>
                            <h3>${instance.name}</h3>
                            <small>ID: ${instance.id.substring(0, 8)}...</small>
                        </div>
                        <div class="status-indicator ${instance.connected ? 'status-connected' : 'status-disconnected'}">
                            <div class="status-dot"></div>
                            <span>${instance.connected ? 'Conectado' : 'Desconectado'}</span>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                        <div style="text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #4f46e5;">${instance.contacts_count || 0}</div>
                            <div style="font-size: 12px; color: #6b7280;">Contatos</div>
                        </div>
                        <div style="text-align: center; padding: 15px; background: #f9fafb; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #4f46e5;">${instance.messages_today || 0}</div>
                            <div style="font-size: 12px; color: #6b7280;">Mensagens</div>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 10px;">
                        ${!instance.connected ? 
                            `<button class="btn btn-success" onclick="connectInstance('${instance.id}')" style="flex: 1;">🔗 Conectar Real</button>` :
                            `<button class="btn btn-secondary" disabled style="flex: 1;">✅ Conectado</button>`
                        }
                        <button class="btn btn-primary" onclick="showQRCode('${instance.id}')">📋 Ver QR Code</button>
                        <button class="btn btn-danger" onclick="disconnectInstance('${instance.id}')">❌ Desconectar</button>
                        <button class="btn btn-danger" onclick="deleteInstance('${instance.id}', '${instance.name}')">🗑️ Excluir</button>
                    </div>
                </div>
            `).join('');
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            checkConnectionStatus();
            
            // Start status polling
            statusPollingInterval = setInterval(checkConnectionStatus, 5000);
            
            // Update stats every 30 seconds
            setInterval(loadStats, 30000);
            
            document.getElementById('createModal').addEventListener('click', function(e) {
                if (e.target === this) this.classList.remove('show');
            });
            
            document.getElementById('qrModal').addEventListener('click', function(e) {
                if (e.target === this) closeQRModal();
            });
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {
            if (qrPollingInterval) clearInterval(qrPollingInterval);
            if (statusPollingInterval) clearInterval(statusPollingInterval);
        });
    </script>
</body>
</html>'''

# Database (same as Pure)
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
    
    # Instances table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instances (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            connected INTEGER DEFAULT 0,
            user_name TEXT,
            user_id TEXT,
            created_at TEXT
        )
    """)
    
    # Contacts table (updated with instance_id)
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
    
    # Messages table (updated with instance support)
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
    
    # Webhooks table (new)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS webhooks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            created_at TEXT
        )
    """)
    
    # Chats table (new for conversation management)
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
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado")

def add_sample_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM instances")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    current_time = datetime.now(timezone.utc).isoformat()
    
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
app.use(cors());
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
                    
                    console.log(`📥 Nova mensagem na instância ${instanceId} de: ${from.split('@')[0]} - ${messageText.substring(0, 50)}...`);
                    
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
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Baileys service rodando na porta ${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);
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
    def do_GET(self):
        if self.path == '/':
            self.send_html_response(HTML_APP)
        elif self.path == '/api/instances':
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
        else:
            self.send_error(404, "Not Found")
    
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
        else:
            self.send_error(404, "Not Found")
    
    def do_DELETE(self):
        if self.path.startswith('/api/instances/'):
            instance_id = self.path.split('/')[-1]
            self.handle_delete_instance(instance_id)
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
            created_at = datetime.now(timezone.utc).isoformat()
            
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
                response = requests.post('http://localhost:3002/connect', timeout=5)
                
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
                    req = urllib.request.Request('http://localhost:3002/connect', data=data, 
                                               headers={'Content-Type': 'application/json'})
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
                response = requests.get('http://localhost:3002/status', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"connected": False, "connecting": False})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen('http://localhost:3002/status', timeout=5) as response:
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
                response = requests.get('http://localhost:3002/qr', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"qr": None, "connected": False})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen('http://localhost:3002/qr', timeout=5) as response:
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
                        """, (contact_id, contact_name, phone, instance_id, datetime.now(timezone.utc).isoformat()))
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
                            last_message_time = datetime.now(timezone.utc).isoformat()
                    
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
                        """, (chat_id, phone, contact_name, instance_id, last_message, last_message_time, unread_count, datetime.now(timezone.utc).isoformat()))
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
                response = requests.post(f'http://localhost:3002/connect/{instance_id}', timeout=5)
                
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
                    req = urllib.request.Request(f'http://localhost:3002/connect/{instance_id}', data=data, 
                                               headers={'Content-Type': 'application/json'})
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
                response = requests.post(f'http://localhost:3002/disconnect/{instance_id}', timeout=5)
                
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
                req = urllib.request.Request(f'http://localhost:3002/disconnect/{instance_id}', data=data,
                                           headers={'Content-Type': 'application/json'})
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
                response = requests.get(f'http://localhost:3002/status/{instance_id}', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"connected": False, "connecting": False, "instanceId": instance_id})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen(f'http://localhost:3002/status/{instance_id}', timeout=5) as response:
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
                response = requests.get(f'http://localhost:3002/qr/{instance_id}', timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    self.send_json_response(data)
                else:
                    self.send_json_response({"qr": None, "connected": False, "instanceId": instance_id})
            except ImportError:
                # Fallback usando urllib
                try:
                    with urllib.request.urlopen(f'http://localhost:3002/qr/{instance_id}', timeout=5) as response:
                        if response.status == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            self.send_json_response(data)
                        else:
                            self.send_json_response({"qr": None, "connected": False, "instanceId": instance_id})
                except:
                    self.send_json_response({"qr": None, "connected": False, "instanceId": instance_id})
                
        except Exception as e:
            self.send_json_response({"qr": None, "connected": False, "error": str(e), "instanceId": instance_id})

    def handle_send_message(self, instance_id):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            to = data.get('to', '')
            message = data.get('message', '')
            message_type = data.get('type', 'text')
            
            try:
                import requests
                response = requests.post(f'http://localhost:3002/send/{instance_id}', 
                                       json=data, timeout=10)
                
                if response.status_code == 200:
                    # Save message to database
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
            except ImportError:
                # Fallback usando urllib
                import urllib.request
                req_data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(f'http://localhost:3002/send/{instance_id}', 
                                           data=req_data, 
                                           headers={'Content-Type': 'application/json'})
                req.get_method = lambda: 'POST'
                
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
            timestamp = data.get('timestamp', datetime.now(timezone.utc).isoformat())
            message_id = data.get('messageId', str(uuid.uuid4()))
            message_type = data.get('messageType', 'text')
            
            # Clean phone number
            phone = from_jid.replace('@s.whatsapp.net', '').replace('@c.us', '')
            
            # Save message and create contact if needed
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Check if contact exists
            cursor.execute("SELECT id, name FROM contacts WHERE phone = ?", (phone,))
            contact = cursor.fetchone()
            
            if not contact:
                # Create new contact
                contact_id = str(uuid.uuid4())
                contact_name = f"Contato {phone[-4:]}"  # Use last 4 digits as name
                
                cursor.execute("""
                    INSERT INTO contacts (id, name, phone, instance_id, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (contact_id, contact_name, phone, instance_id, timestamp))
                
                print(f"📞 Novo contato criado: {contact_name} ({phone}) - Instância: {instance_id}")
            else:
                contact_id, contact_name = contact
            
            # Save message
            msg_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO messages (id, contact_name, phone, message, direction, instance_id, message_type, whatsapp_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (msg_id, contact_name, phone, message, 'incoming', instance_id, message_type, message_id, timestamp))
            
            conn.commit()
            conn.close()
            
            print(f"📥 Mensagem recebida na instância {instance_id} de {contact_name}: {message[:50]}...")
            self.send_json_response({"success": True, "instanceId": instance_id})
            
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
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
    print("🤖 WhatsFlow Real - Conexão WhatsApp Verdadeira")
    print("=" * 50)
    print("✅ Python backend para interface")
    print("✅ Node.js + Baileys para WhatsApp real")
    print("✅ QR Code real para conexão")
    print("✅ Mensagens reais enviadas/recebidas")
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
    
    print("✅ WhatsFlow Real configurado!")
    print(f"🌐 Interface: http://localhost:{PORT}")
    print(f"📱 WhatsApp Service: http://localhost:{BAILEYS_PORT}")
    print("🚀 Servidor iniciando...")
    print("   Para parar: Ctrl+C")
    print()
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), WhatsFlowRealHandler)
        print(f"✅ Servidor rodando na porta {PORT}")
        print("🔗 Pronto para conectar WhatsApp REAL!")
        print(f"🌐 Acesse: http://localhost:{PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 WhatsFlow Real finalizado!")
        baileys_manager.stop_baileys()

if __name__ == "__main__":
    main()