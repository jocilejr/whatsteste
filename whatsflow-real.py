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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            min-height: 100vh; color: #1f2937;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .subtitle { background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; 
                   display: inline-block; margin-top: 10px; font-size: 0.9rem; }
        
        .nav { display: flex; gap: 10px; margin-bottom: 30px; flex-wrap: wrap; justify-content: center; }
        .nav-btn { background: rgba(255,255,255,0.9); border: none; padding: 12px 20px; 
                  border-radius: 8px; cursor: pointer; font-weight: 500; transition: all 0.3s ease; }
        .nav-btn:hover { background: white; transform: translateY(-2px); }
        .nav-btn.active { background: white; color: #4f46e5; }
        
        .card { background: white; border-radius: 16px; padding: 25px; 
               box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px; }
        
        .status-indicator { display: inline-flex; align-items: center; gap: 8px; 
                           padding: 8px 16px; border-radius: 20px; font-weight: 500; }
        .status-connected { background: #d1fae5; color: #065f46; }
        .status-disconnected { background: #fef2f2; color: #991b1b; }
        .status-connecting { background: #fef3c7; color: #92400e; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; }
        .status-connected .status-dot { background: #10b981; }
        .status-disconnected .status-dot { background: #ef4444; }
        .status-connecting .status-dot { background: #f59e0b; animation: pulse 1s infinite; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                     gap: 20px; margin: 20px 0; }
        .stat-card { text-align: center; padding: 20px; background: #f8fafc; 
                    border-radius: 12px; border: 1px solid #e2e8f0; }
        .stat-number { font-size: 2rem; font-weight: bold; color: #4f46e5; margin-bottom: 5px; }
        .stat-label { color: #6b7280; font-size: 14px; }
        
        .instances-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .instance-card { border: 2px solid #e5e7eb; border-radius: 12px; padding: 20px; 
                        background: white; transition: all 0.3s ease; }
        .instance-card:hover { transform: translateY(-2px); border-color: #4f46e5; }
        .instance-card.connected { border-color: #10b981; background: #f0fdf4; }
        
        .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; 
              font-weight: 500; transition: all 0.3s ease; }
        .btn-primary { background: #4f46e5; color: white; }
        .btn-success { background: #10b981; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .btn:hover { transform: translateY(-1px); opacity: 0.9; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                background: rgba(0,0,0,0.5); z-index: 1000; align-items: center; justify-content: center; }
        .modal.show { display: flex; }
        .modal-content { background: white; padding: 30px; border-radius: 16px; 
                        width: 90%; max-width: 500px; }
        
        .form-input { width: 100%; padding: 12px; border: 2px solid #d1d5db; 
                     border-radius: 6px; font-size: 16px; }
        .form-input:focus { outline: none; border-color: #4f46e5; }
        
        .empty-state { text-align: center; padding: 60px 20px; color: #6b7280; }
        .empty-icon { font-size: 4rem; margin-bottom: 20px; opacity: 0.5; }
        .empty-title { font-size: 1.5rem; font-weight: 600; color: #1f2937; margin-bottom: 10px; }
        
        .section { display: none; }
        .section.active { display: block; }
        
        .success-message { background: #d1fae5; color: #065f46; padding: 15px; 
                          border-radius: 8px; margin: 20px 0; text-align: center; font-weight: 500; }
        
        .real-connection-badge { background: #10b981; color: white; padding: 10px 15px; 
                               border-radius: 8px; margin: 20px 0; text-align: center; font-weight: 500; }
        
        .qr-container { text-align: center; margin: 20px 0; }
        .qr-code { background: white; padding: 20px; border-radius: 12px; 
                  display: inline-block; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .qr-instructions { background: #f8fafc; padding: 20px; border-radius: 8px; 
                          margin-bottom: 20px; text-align: left; }
        
        .connected-user { background: #d1fae5; padding: 15px; border-radius: 8px; 
                         margin: 15px 0; border: 2px solid #10b981; }
        
        .loading { text-align: center; padding: 40px; color: #6b7280; }
        .loading-spinner { font-size: 2rem; margin-bottom: 15px; animation: pulse 1s infinite; }
        
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .header h1 { font-size: 2rem; }
            .stats-grid, .instances-grid { grid-template-columns: 1fr; }
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
        
        <div id="messages" class="section">
            <div class="card">
                <h2>💬 Mensagens Recebidas</h2>
                <div id="messages-container">
                    <div class="empty-state">
                        <div class="empty-icon">💬</div>
                        <div class="empty-title">Nenhuma mensagem ainda</div>
                        <p>As mensagens do WhatsApp aparecerão aqui quando começar a receber</p>
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
                <h3>📱 Conectar WhatsApp Real</h3>
                <button onclick="hideQRModal()" style="background: none; border: none; font-size: 20px; cursor: pointer;">&times;</button>
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
            
            <div id="qr-container" class="qr-container">
                <div id="qr-loading" style="text-align: center; padding: 40px;">
                    <div style="font-size: 2rem; margin-bottom: 15px;">⏳</div>
                    <p>Gerando QR Code real...</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <button class="btn btn-danger" onclick="hideQRModal()">🚫 Fechar</button>
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

        function showQRModal(instanceId) {
            currentInstanceId = instanceId;
            document.getElementById('qrModal').classList.add('show');
            startQRPolling();
        }

        function hideQRModal() {
            document.getElementById('qrModal').classList.remove('show');
            if (qrPollingInterval) {
                clearInterval(qrPollingInterval);
                qrPollingInterval = null;
            }
            currentInstanceId = null;
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
                    alert(`✅ Instância "${name}" criada!`);
                }
            } catch (error) {
                alert('❌ Erro ao criar instância');
            }
        }

        async function connectInstance(instanceId) {
            try {
                const response = await fetch(`/api/instances/${instanceId}/connect`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    showQRModal(instanceId);
                } else {
                    alert('❌ Erro ao iniciar conexão');
                }
            } catch (error) {
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
                const response = await fetch('/api/messages');
                const messages = await response.json();
                renderMessages(messages);
            } catch (error) {
                console.error('Error loading messages');
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
                if (e.target === this) hideQRModal();
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS instances (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, connected INTEGER DEFAULT 0,
        contacts_count INTEGER DEFAULT 0, messages_today INTEGER DEFAULT 0,
        created_at TEXT NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT NOT NULL,
        instance_id TEXT, created_at TEXT NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY, contact_name TEXT, phone TEXT, message TEXT NOT NULL, 
        direction TEXT, instance_id TEXT, created_at TEXT NOT NULL)''')
    
    conn.commit()
    conn.close()

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
                        await fetch('http://localhost:8889/api/whatsapp/connected', {
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
                        await fetch('http://localhost:8889/api/messages/receive', {
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

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
    console.log(`🚀 Baileys service rodando na porta ${PORT}`);
    console.log('⏳ Aguardando comando para conectar...');
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
            self.handle_whatsapp_status()
        elif self.path == '/api/whatsapp/qr':
            self.handle_whatsapp_qr()
        elif self.path == '/api/contacts':
            self.handle_get_contacts()
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
        elif self.path == '/api/messages/receive':
            self.handle_receive_message()
        elif self.path == '/api/whatsapp/connected':
            self.handle_whatsapp_connected()
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
    
    def handle_whatsapp_connected(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Update instance connection status
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Update all instances to connected (for now, single instance support)
            cursor.execute("UPDATE instances SET connected = 1")
            
            conn.commit()
            conn.close()
            
            print(f"✅ WhatsApp conectado: {data.get('name', data.get('id', 'Unknown'))}")
            self.send_json_response({"success": True})
            
        except Exception as e:
            print(f"❌ Erro ao processar conexão: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_receive_message(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract contact info
            from_jid = data.get('from', '')
            message = data.get('message', '')
            timestamp = data.get('timestamp', datetime.now(timezone.utc).isoformat())
            
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
                    INSERT INTO contacts (id, name, phone, created_at)
                    VALUES (?, ?, ?, ?)
                """, (contact_id, contact_name, phone, timestamp))
                
                print(f"📞 Novo contato criado: {contact_name} ({phone})")
            else:
                contact_id, contact_name = contact
            
            # Save message
            message_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO messages (id, contact_name, phone, message, direction, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, contact_name, phone, message, 'incoming', timestamp))
            
            conn.commit()
            conn.close()
            
            print(f"📥 Mensagem recebida de {contact_name}: {message[:50]}...")
            self.send_json_response({"success": True})
            
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_get_contacts(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY timestamp DESC")
            contacts = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(contacts)
        except Exception as e:
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