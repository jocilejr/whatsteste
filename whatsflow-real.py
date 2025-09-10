#!/usr/bin/env python3
"""
WhatsFlow Real - Professional Version
Sistema de Automação WhatsApp com conexão verdadeira e design profissional
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

# HTML da aplicação profissional - Similar ao design enviado
HTML_APP = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsFlow - Plataforma Profissional</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
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
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            overflow: hidden;
        }
        
        .app-container {
            display: flex;
            height: 100vh;
            background: var(--bg-secondary);
        }
        
        /* Sidebar */
        .sidebar {
            width: 320px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }
        
        .sidebar-header {
            padding: 20px;
            background: var(--primary);
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .sidebar-title {
            font-size: 19px;
            font-weight: 600;
        }
        
        .sidebar-nav {
            display: flex;
            border-bottom: 1px solid var(--border);
        }
        
        .nav-item {
            flex: 1;
            padding: 12px;
            text-align: center;
            background: none;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .nav-item.active {
            color: var(--primary);
            border-bottom: 2px solid var(--primary);
        }
        
        .nav-item:hover {
            background: var(--bg-primary);
        }
        
        .device-selector {
            padding: 15px 20px;
            border-bottom: 1px solid var(--border);
        }
        
        .device-select {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--bg-primary);
            font-size: 14px;
        }
        
        .search-container {
            padding: 15px 20px;
            border-bottom: 1px solid var(--border);
        }
        
        .search-input {
            width: 100%;
            padding: 10px 15px;
            border: 1px solid var(--border);
            border-radius: 20px;
            background: var(--bg-primary);
            font-size: 14px;
            outline: none;
        }
        
        .search-input:focus {
            border-color: var(--primary);
        }
        
        .conversations-list {
            flex: 1;
            overflow-y: auto;
        }
        
        .conversation-item {
            padding: 15px 20px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .conversation-item:hover {
            background: var(--bg-primary);
        }
        
        .conversation-item.active {
            background: #e1f5fe;
        }
        
        .avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 18px;
            flex-shrink: 0;
        }
        
        .avatar img {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
        }
        
        .conversation-info {
            flex: 1;
            min-width: 0;
        }
        
        .conversation-name {
            font-weight: 500;
            font-size: 16px;
            margin-bottom: 3px;
            color: var(--text-primary);
        }
        
        .last-message {
            font-size: 14px;
            color: var(--text-secondary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .conversation-time {
            font-size: 12px;
            color: var(--text-secondary);
            flex-shrink: 0;
        }
        
        /* Main Chat Area */
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: var(--bg-primary);
        }
        
        .empty-chat {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 40px;
        }
        
        .empty-icon {
            width: 120px;
            height: 120px;
            background: var(--bg-secondary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            color: var(--text-secondary);
            margin-bottom: 30px;
            box-shadow: var(--shadow);
        }
        
        .empty-title {
            font-size: 32px;
            font-weight: 300;
            color: var(--text-secondary);
            margin-bottom: 15px;
        }
        
        .empty-subtitle {
            font-size: 14px;
            color: var(--text-secondary);
            line-height: 1.5;
            max-width: 400px;
        }
        
        /* Chat Header */
        .chat-header {
            display: none;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            align-items: center;
            gap: 15px;
        }
        
        .chat-header.active {
            display: flex;
        }
        
        .back-button {
            display: none;
            background: none;
            border: none;
            font-size: 18px;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 5px;
        }
        
        /* Messages Area */
        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background-image: url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAiIGhlaWdodD0iMzAiIHZpZXdCb3g9IjAgMCAzMCAzMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTE1IDFMMTcuMDkgNi41ODFMMTI0IDhMMTguNTEgMTJMMTcgMTcuNUwxMiAyMkw2LjQ5IDEyTDAgOEw1LjkxIDYuNThMMTUgMVoiIGZpbGw9IiNmOWY5ZjkiIGZpbGwtb3BhY2l0eT0iMC4xIi8+Cjwvc3ZnPgo=');
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-end;
            gap: 8px;
        }
        
        .message.sent {
            justify-content: flex-end;
        }
        
        .message-bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
            position: relative;
        }
        
        .message.received .message-bubble {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border-bottom-left-radius: 4px;
            box-shadow: var(--shadow);
        }
        
        .message.sent .message-bubble {
            background: #dcf8c6;
            color: var(--text-primary);
            border-bottom-right-radius: 4px;
        }
        
        .message-time {
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 4px;
        }
        
        /* Instance Management */
        .instances-section {
            padding: 30px;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 24px;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        
        .btn-primary:hover {
            background: var(--primary-dark);
        }
        
        .btn-success {
            background: var(--primary-light);
            color: white;
        }
        
        .btn-danger {
            background: #dc2626;
            color: white;
        }
        
        .instances-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .instance-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s;
        }
        
        .instance-card:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
        }
        
        .instance-card.connected {
            border-color: var(--primary-light);
            background: #f0fff4;
        }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .status-connected {
            background: #dcfce7;
            color: #166534;
        }
        
        .status-connecting {
            background: #fef3c7;
            color: #92400e;
        }
        
        .status-disconnected {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: currentColor;
        }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.show {
            display: flex;
        }
        
        .modal-content {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 30px;
            width: 90%;
            max-width: 500px;
            box-shadow: var(--shadow-lg);
        }
        
        .modal h3 {
            margin-bottom: 20px;
            font-size: 20px;
            font-weight: 600;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-input {
            width: 100%;
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 14px;
            outline: none;
        }
        
        .form-input:focus {
            border-color: var(--primary);
        }
        
        .modal-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }
        
        .btn-secondary {
            background: var(--bg-primary);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .sidebar {
                position: absolute;
                left: -100%;
                top: 0;
                height: 100%;
                z-index: 100;
                transition: left 0.3s;
            }
            
            .sidebar.show {
                left: 0;
            }
            
            .back-button {
                display: block;
            }
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            color: var(--text-secondary);
        }
        
        .hidden {
            display: none !important;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-title">🚀 WhatsFlow</div>
            </div>
            
            <div class="sidebar-nav">
                <button class="nav-item active" onclick="showSection('conversations')">Conversas</button>
                <button class="nav-item" onclick="showSection('instances')">Instâncias</button>
            </div>
            
            <div class="device-selector">
                <select class="device-select" id="instanceSelect" onchange="changeInstance()">
                    <option value="">Selecione um dispositivo</option>
                </select>
            </div>
            
            <div class="search-container">
                <input type="text" class="search-input" placeholder="Buscar conversa..." id="searchInput" oninput="filterConversations()">
            </div>
            
            <div class="conversations-list" id="conversationsList">
                <div class="loading">Carregando conversas...</div>
            </div>
        </div>
        
        <!-- Chat Area -->
        <div class="chat-area">
            <div class="chat-header" id="chatHeader">
                <button class="back-button" onclick="closeChatMobile()">←</button>
                <div class="avatar" id="chatAvatar">?</div>
                <div>
                    <div class="conversation-name" id="chatName">Nome do Contato</div>
                    <div class="last-message" id="chatStatus">Online</div>
                </div>
            </div>
            
            <div class="empty-chat" id="emptyChat">
                <div class="empty-icon">💬</div>
                <div class="empty-title">Nenhuma conversa encontrada</div>
                <div class="empty-subtitle">
                    Selecione uma conversa para começar ou conecte uma instância do WhatsApp para ver suas mensagens.
                </div>
            </div>
            
            <div class="messages-area hidden" id="messagesArea">
                <!-- Messages will be loaded here -->
            </div>
        </div>
        
        <!-- Instances Section (hidden by default) -->
        <div class="instances-section hidden" id="instancesSection">
            <div class="section-header">
                <h2 class="section-title">Gerenciar Instâncias</h2>
                <button class="btn btn-primary" onclick="showCreateModal()">
                    <span>+</span> Nova Instância
                </button>
            </div>
            
            <div class="instances-grid" id="instancesGrid">
                <div class="loading">Carregando instâncias...</div>
            </div>
        </div>
    </div>
    
    <!-- Create Instance Modal -->
    <div class="modal" id="createModal">
        <div class="modal-content">
            <h3>Nova Instância WhatsApp</h3>
            <form onsubmit="createInstance(event)">
                <div class="form-group">
                    <input type="text" class="form-input" id="instanceName" placeholder="Nome da instância" required>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="hideCreateModal()">Cancelar</button>
                    <button type="submit" class="btn btn-primary">Criar Instância</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- QR Code Modal -->
    <div class="modal" id="qrModal">
        <div class="modal-content">
            <h3>Conectar WhatsApp</h3>
            <div style="text-align: center; padding: 20px;">
                <div id="qrCode">Gerando QR Code...</div>
                <p style="margin-top: 15px; color: var(--text-secondary);">
                    Escaneie o código QR com seu WhatsApp
                </p>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="hideQRModal()">Fechar</button>
            </div>
        </div>
    </div>

    <script>
        let currentConversation = null;
        let instances = [];
        let conversations = [];
        let selectedInstance = null;
        let qrInterval = null;

        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            loadInstances();
            loadConversations();
            showSection('conversations');
        });

        // Section management
        function showSection(section) {
            // Update nav
            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            event.target.classList.add('active');
            
            // Show/hide sections
            if (section === 'conversations') {
                document.querySelector('.chat-area').style.display = 'flex';
                document.getElementById('instancesSection').classList.add('hidden');
            } else if (section === 'instances') {
                document.querySelector('.chat-area').style.display = 'none';
                document.getElementById('instancesSection').classList.remove('hidden');
                loadInstances();
            }
        }

        // Load instances
        async function loadInstances() {
            try {
                const response = await fetch('/api/instances');
                instances = await response.json();
                
                renderInstancesSelect();
                renderInstancesGrid();
            } catch (error) {
                console.error('Erro ao carregar instâncias:', error);
            }
        }

        function renderInstancesSelect() {
            const select = document.getElementById('instanceSelect');
            select.innerHTML = '<option value="">Selecione um dispositivo</option>';
            
            instances.forEach(instance => {
                const option = document.createElement('option');
                option.value = instance.id;
                option.textContent = `${instance.name} ${instance.connected ? '(Conectado)' : ''}`;
                select.appendChild(option);
            });
        }

        function renderInstancesGrid() {
            const grid = document.getElementById('instancesGrid');
            
            if (instances.length === 0) {
                grid.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 60px; color: var(--text-secondary);">
                        <div style="font-size: 48px; margin-bottom: 20px;">📱</div>
                        <h3>Nenhuma instância criada</h3>
                        <p>Crie sua primeira instância para começar</p>
                    </div>
                `;
                return;
            }

            grid.innerHTML = instances.map(instance => `
                <div class="instance-card ${instance.connected ? 'connected' : ''}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="font-size: 18px; font-weight: 600;">${instance.name}</h3>
                        <span class="status-badge status-${instance.connected ? 'connected' : 'disconnected'}">
                            <span class="status-dot"></span>
                            ${instance.connected ? 'Conectado' : 'Desconectado'}
                        </span>
                    </div>
                    
                    ${instance.user_name ? `
                        <div style="margin-bottom: 15px; padding: 10px; background: var(--bg-primary); border-radius: 8px;">
                            <div style="font-weight: 500;">${instance.user_name}</div>
                            <div style="font-size: 12px; color: var(--text-secondary);">${instance.user_id}</div>
                        </div>
                    ` : ''}
                    
                    <div style="display: flex; gap: 10px;">
                        ${instance.connected ? `
                            <button class="btn btn-danger" onclick="disconnectInstance('${instance.id}')">
                                Desconectar
                            </button>
                        ` : `
                            <button class="btn btn-success" onclick="connectInstance('${instance.id}')">
                                Conectar
                            </button>
                        `}
                        <button class="btn btn-secondary" onclick="deleteInstance('${instance.id}', '${instance.name}')">
                            Excluir
                        </button>
                    </div>
                </div>
            `).join('');
        }

        // Instance management
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
                }
            } catch (error) {
                alert('❌ Erro ao conectar instância');
            }
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
                }
            } catch (error) {
                alert('❌ Erro ao desconectar');
            }
        }

        async function deleteInstance(id, name) {
            if (!confirm(`Excluir instância "${name}"?`)) return;
            
            try {
                const response = await fetch(`/api/instances/${id}`, { 
                    method: 'DELETE' 
                });
                
                if (response.ok) {
                    loadInstances();
                    alert(`✅ Instância "${name}" excluída!`);
                }
            } catch (error) {
                alert('❌ Erro ao excluir instância');
            }
        }

        // Load conversations
        async function loadConversations() {
            try {
                const response = await fetch('/api/chats');
                conversations = await response.json();
                renderConversations();
            } catch (error) {
                console.error('Erro ao carregar conversas:', error);
                document.getElementById('conversationsList').innerHTML = `
                    <div style="padding: 40px; text-align: center; color: var(--text-secondary);">
                        Erro ao carregar conversas
                    </div>
                `;
            }
        }

        function renderConversations() {
            const list = document.getElementById('conversationsList');
            
            if (conversations.length === 0) {
                list.innerHTML = `
                    <div style="padding: 40px; text-align: center; color: var(--text-secondary);">
                        <div style="font-size: 48px; margin-bottom: 15px;">💬</div>
                        <div>Nenhuma conversa</div>
                        <div style="font-size: 12px;">Conecte uma instância para ver conversas</div>
                    </div>
                `;
                return;
            }

            list.innerHTML = conversations.map(conv => `
                <div class="conversation-item" onclick="openConversation('${conv.contact_phone}', '${conv.contact_name}', '${conv.instance_id}')">
                    <div class="avatar">
                        ${conv.avatar_url ? 
                            `<img src="${conv.avatar_url}" alt="${conv.contact_name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                             <div style="display: none;">${conv.contact_name.charAt(0).toUpperCase()}</div>` :
                            conv.contact_name.charAt(0).toUpperCase()
                        }
                    </div>
                    <div class="conversation-info">
                        <div class="conversation-name">${conv.contact_name}</div>
                        <div class="last-message">${conv.last_message || 'Nova conversa'}</div>
                    </div>
                    <div class="conversation-time">
                        ${conv.last_message_time ? new Date(conv.last_message_time).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'}) : ''}
                    </div>
                </div>
            `).join('');
        }

        async function openConversation(phone, name, instanceId) {
            currentConversation = { phone, name, instanceId };
            
            // Update UI
            document.getElementById('emptyChat').style.display = 'none';
            document.getElementById('chatHeader').classList.add('active');
            document.getElementById('messagesArea').classList.remove('hidden');
            
            document.getElementById('chatName').textContent = name;
            document.getElementById('chatAvatar').textContent = name.charAt(0).toUpperCase();
            
            // Load messages
            await loadMessages(phone, instanceId);
        }

        async function loadMessages(phone, instanceId) {
            try {
                const response = await fetch(`/api/messages?phone=${phone}&instance_id=${instanceId}`);
                const messages = await response.json();
                
                const messagesArea = document.getElementById('messagesArea');
                
                if (messages.length === 0) {
                    messagesArea.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
                            Nenhuma mensagem ainda
                        </div>
                    `;
                    return;
                }

                messagesArea.innerHTML = messages.map(msg => `
                    <div class="message ${msg.direction === 'outgoing' ? 'sent' : 'received'}">
                        <div class="message-bubble">
                            <div>${msg.message}</div>
                            <div class="message-time">
                                ${new Date(msg.created_at).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}
                            </div>
                        </div>
                    </div>
                `).join('');
                
                // Scroll to bottom
                messagesArea.scrollTop = messagesArea.scrollHeight;
                
            } catch (error) {
                console.error('Erro ao carregar mensagens:', error);
            }
        }

        // QR Code modal
        function showQRModal(instanceId) {
            document.getElementById('qrModal').classList.add('show');
            startQRPolling(instanceId);
        }

        function hideQRModal() {
            document.getElementById('qrModal').classList.remove('show');
            if (qrInterval) {
                clearInterval(qrInterval);
                qrInterval = null;
            }
        }

        async function startQRPolling(instanceId) {
            const qrContainer = document.getElementById('qrCode');
            
            const checkQR = async () => {
                try {
                    const response = await fetch(`http://localhost:3002/qr/${instanceId}`);
                    const data = await response.json();
                    
                    if (data.qr) {
                        qrContainer.innerHTML = `<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(data.qr)}" alt="QR Code">`;
                    } else if (data.connected) {
                        qrContainer.innerHTML = '✅ Conectado com sucesso!';
                        setTimeout(() => {
                            hideQRModal();
                            loadInstances();
                            loadConversations();
                        }, 2000);
                        return;
                    }
                } catch (error) {
                    qrContainer.innerHTML = 'Erro ao gerar QR Code';
                }
            };
            
            checkQR();
            qrInterval = setInterval(checkQR, 3000);
        }

        // Modal functions
        function showCreateModal() {
            document.getElementById('createModal').classList.add('show');
        }

        function hideCreateModal() {
            document.getElementById('createModal').classList.remove('show');
            document.getElementById('instanceName').value = '';
        }

        // Search functionality
        function filterConversations() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const items = document.querySelectorAll('.conversation-item');
            
            items.forEach(item => {
                const name = item.querySelector('.conversation-name').textContent.toLowerCase();
                const message = item.querySelector('.last-message').textContent.toLowerCase();
                
                if (name.includes(search) || message.includes(search)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        // Mobile functions
        function closeChatMobile() {
            document.getElementById('emptyChat').style.display = 'flex';
            document.getElementById('chatHeader').classList.remove('active');
            document.getElementById('messagesArea').classList.add('hidden');
            currentConversation = null;
        }

        function changeInstance() {
            selectedInstance = document.getElementById('instanceSelect').value;
            if (selectedInstance) {
                loadConversations();
            }
        }

        // Auto refresh
        setInterval(() => {
            if (document.querySelector('.nav-item.active').textContent === 'Conversas') {
                loadConversations();
            }
        }, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>'''

# Database initialization
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
    
    # Contacts table
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
    
    # Messages table
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
    
    # Chats table for conversation management
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            contact_phone TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            instance_id TEXT NOT NULL,
            last_message TEXT,
            last_message_time TEXT,
            unread_count INTEGER DEFAULT 0,
            avatar_url TEXT,
            created_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()

class BaileysService:
    def __init__(self):
        self.process = None
        self.is_running = False
        
    def start(self):
        if self.is_running:
            return True
            
        try:
            # Check if Node.js is available
            subprocess.run(['node', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Node.js não encontrado - Baileys não será iniciado")
            return False
        
        # Create baileys service directory
        baileys_dir = "baileys_service"
        if not os.path.exists(baileys_dir):
            os.makedirs(baileys_dir)
        
        # Create package.json
        package_json = {
            "name": "whatsflow-baileys",
            "version": "1.0.0",
            "main": "server.js",
            "dependencies": {
                "@whiskeysockets/baileys": "^6.7.5",
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "qrcode-terminal": "^0.12.0",
                "node-fetch": "^2.6.7"
            }
        }
        
        with open(f"{baileys_dir}/package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
        
        print("✅ package.json criado")
        
        # Create improved server.js with better name/photo extraction
        server_js = '''const express = require('express');
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
});'''
        
        with open(f"{baileys_dir}/server.js", 'w') as f:
            f.write(server_js)
        
        print("✅ server.js aprimorado criado")
        
        # Install dependencies
        print("📦 Iniciando instalação das dependências...")
        print("   Isso pode levar alguns minutos na primeira vez...")
        
        try:
            subprocess.run(['npm', 'install'], cwd=baileys_dir, capture_output=True, check=True)
            print("✅ Dependências instaladas com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na instalação: {e}")
            return False
        
        # Install node-fetch specifically
        try:
            subprocess.run(['npm', 'install', 'node-fetch@2.6.7'], cwd=baileys_dir, capture_output=True, check=True)
            print("✅ node-fetch instalado com sucesso!")
        except subprocess.CalledProcessError:
            print("⚠️ Erro ao instalar node-fetch - continuando...")
        
        # Start Baileys service
        print("🚀 Iniciando serviço Baileys...")
        try:
            self.process = subprocess.Popen(
                ['node', 'server.js'],
                cwd=baileys_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Check if started successfully
            time.sleep(2)
            if self.process.poll() is None:
                self.is_running = True
                print("✅ Baileys iniciado com sucesso!")
                return True
            else:
                stdout, stderr = self.process.communicate()
                print(f"❌ Baileys falhou ao iniciar:")
                print(f"stdout: {stdout.decode()}")
                print(f"stderr: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar Baileys: {e}")
            return False

# HTTP Handler
class WhatsFlowHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_html_response(HTML_APP)
        elif self.path == '/api/instances':
            self.handle_get_instances()
        elif self.path == '/api/contacts':
            self.handle_get_contacts()
        elif self.path == '/api/chats':
            self.handle_get_chats()
        elif self.path == '/api/messages':
            self.handle_get_messages()
        elif self.path.startswith('/api/messages?'):
            self.handle_get_messages_filtered()
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
        elif self.path == '/api/chats/import':
            self.handle_import_chats()
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
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
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
    
    def handle_create_instance(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = str(uuid.uuid4())
            name = data.get('name', f'Instance {instance_id[:8]}')
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO instances (id, name, connected, created_at)
                VALUES (?, ?, 0, ?)
            """, (instance_id, name, datetime.now(timezone.utc).isoformat()))
            conn.commit()
            conn.close()
            
            self.send_json_response({
                "id": instance_id,
                "name": name,
                "connected": 0,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_connect_instance(self, instance_id):
        try:
            # Make request to Baileys service
            import urllib.request
            req = urllib.request.Request(f'http://localhost:{BAILEYS_PORT}/connect/{instance_id}', method='POST')
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
            
            self.send_json_response({"success": True, "message": f"Conexão da instância {instance_id} iniciada"})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_disconnect_instance(self, instance_id):
        try:
            import urllib.request
            req = urllib.request.Request(f'http://localhost:{BAILEYS_PORT}/disconnect/{instance_id}', method='POST')
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
            
            # Update database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("UPDATE instances SET connected = 0, user_name = NULL, user_id = NULL WHERE id = ?", (instance_id,))
            conn.commit()
            conn.close()
            
            self.send_json_response({"success": True, "message": f"Instância {instance_id} desconectada"})
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_delete_instance(self, instance_id):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM instances WHERE id = ?", (instance_id,))
            conn.commit()
            conn.close()
            
            self.send_json_response({"success": True, "message": f"Instância {instance_id} excluída"})
        except Exception as e:
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
            cursor.execute("SELECT * FROM chats ORDER BY last_message_time DESC")
            chats = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(chats)
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
    
    def handle_get_messages_filtered(self):
        try:
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            phone = query_params.get('phone', [None])[0]
            instance_id = query_params.get('instance_id', [None])[0]
            
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if phone and instance_id:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE phone = ? AND instance_id = ? 
                    ORDER BY created_at ASC
                """, (phone, instance_id))
            elif phone:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE phone = ? 
                    ORDER BY created_at ASC
                """, (phone,))
            else:
                cursor.execute("SELECT * FROM messages ORDER BY created_at DESC LIMIT 50")
            
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json_response(messages)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_receive_message(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = data.get('instanceId', 'default')
            from_jid = data.get('from', '')
            message = data.get('message', '')
            timestamp = data.get('timestamp', datetime.now(timezone.utc).isoformat())
            message_id = data.get('messageId', str(uuid.uuid4()))
            message_type = data.get('messageType', 'text')
            
            phone = from_jid.replace('@s.whatsapp.net', '').replace('@c.us', '')
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Check if contact exists
            cursor.execute("SELECT id, name FROM contacts WHERE phone = ? AND instance_id = ?", (phone, instance_id))
            contact = cursor.fetchone()
            
            if not contact:
                # Create new contact with phone as name initially
                contact_id = str(uuid.uuid4())
                contact_name = f"+{phone}"
                
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
            
            # Update or create chat
            cursor.execute("SELECT id FROM chats WHERE contact_phone = ? AND instance_id = ?", (phone, instance_id))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE chats SET last_message = ?, last_message_time = ?
                    WHERE contact_phone = ? AND instance_id = ?
                """, (message, timestamp, phone, instance_id))
            else:
                chat_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO chats (id, contact_phone, contact_name, instance_id, last_message, last_message_time, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (chat_id, phone, contact_name, instance_id, message, timestamp, timestamp))
            
            conn.commit()
            conn.close()
            
            print(f"📥 Mensagem recebida de {contact_name}: {message[:50]}...")
            self.send_json_response({"success": True, "instanceId": instance_id})
            
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {e}")
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
            
            # Update instance with user info
            if batch_number == 1:
                cursor.execute("""
                    UPDATE instances SET connected = 1, user_name = ?, user_id = ? 
                    WHERE id = ?
                """, (user.get('name', ''), user.get('id', ''), instance_id))
                print(f"👤 Usuário atualizado: {user.get('name', '')} ({user.get('phone', '')})")
            
            imported_contacts = 0
            imported_chats = 0
            
            for chat in chats:
                if chat.get('id') and not chat['id'].endswith('@g.us'):  # Skip groups
                    phone = chat['id'].replace('@s.whatsapp.net', '').replace('@c.us', '')
                    
                    # Use enhanced name from Baileys
                    contact_name = (chat.get('enhancedName') or 
                                   chat.get('name') or 
                                   chat.get('pushName') or 
                                   chat.get('notify') or 
                                   f"+{phone}")
                    
                    profile_pic_url = chat.get('profilePicUrl')
                    
                    # Insert or update contact
                    cursor.execute("SELECT id FROM contacts WHERE phone = ? AND instance_id = ?", (phone, instance_id))
                    if not cursor.fetchone():
                        contact_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO contacts (id, name, phone, instance_id, avatar_url, created_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (contact_id, contact_name, phone, instance_id, profile_pic_url, datetime.now(timezone.utc).isoformat()))
                        imported_contacts += 1
                        print(f"📞 Contato importado: {contact_name} - Foto: {'✅' if profile_pic_url else '❌'}")
                    else:
                        # Update with better name and photo
                        cursor.execute("""
                            UPDATE contacts SET name = ?, avatar_url = ? 
                            WHERE phone = ? AND instance_id = ?
                        """, (contact_name, profile_pic_url, phone, instance_id))
                        print(f"🔄 Contato atualizado: {contact_name} - Foto: {'✅' if profile_pic_url else '❌'}")
                    
                    # Create/update chat
                    last_message = chat.get('lastMessage', {}).get('message', {}).get('conversation', 'Nova conversa')
                    last_message_time = datetime.now(timezone.utc).isoformat()
                    
                    cursor.execute("SELECT id FROM chats WHERE contact_phone = ? AND instance_id = ?", (phone, instance_id))
                    if cursor.fetchone():
                        cursor.execute("""
                            UPDATE chats SET contact_name = ?, last_message = ?, last_message_time = ?, avatar_url = ?
                            WHERE contact_phone = ? AND instance_id = ?
                        """, (contact_name, last_message, last_message_time, profile_pic_url, phone, instance_id))
                    else:
                        chat_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO chats (id, contact_phone, contact_name, instance_id, last_message, last_message_time, avatar_url, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (chat_id, phone, contact_name, instance_id, last_message, last_message_time, profile_pic_url, datetime.now(timezone.utc).isoformat()))
                        imported_chats += 1
            
            conn.commit()
            conn.close()
            
            print(f"📦 Lote {batch_number}/{total_batches}: {imported_contacts} contatos, {imported_chats} chats importados")
            
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
    
    def handle_whatsapp_connected(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            instance_id = data.get('instanceId', '')
            user = data.get('user', {})
            
            # Update instance in database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE instances SET connected = 1, user_name = ?, user_id = ?
                WHERE id = ?
            """, (user.get('name', ''), user.get('id', ''), instance_id))
            conn.commit()
            conn.close()
            
            print(f"✅ WhatsApp conectado na instância {instance_id}: {user.get('id', '')}")
            self.send_json_response({"success": True, "instanceId": instance_id})
            
        except Exception as e:
            print(f"❌ Erro ao processar conexão: {e}")
            self.send_json_response({"error": str(e)}, 500)

def main():
    print("🚀 WhatsFlow Professional - Iniciando...")
    print("=" * 50)
    
    # Initialize database
    print("📁 Inicializando banco de dados...")
    init_db()
    print("✅ Banco de dados inicializado")
    
    # Start Baileys service
    print("📱 Iniciando serviço WhatsApp (Baileys)...")
    baileys = BaileysService()
    baileys_started = baileys.start()
    
    if not baileys_started:
        print("⚠️ Continuando sem Baileys - funcionalidade limitada")
    
    # Start HTTP server
    print(f"🌐 Iniciando servidor HTTP na porta {PORT}...")
    try:
        server = HTTPServer(('0.0.0.0', PORT), WhatsFlowHandler)
        print(f"✅ WhatsFlow Professional iniciado!")
        print(f"🌐 Acesse: http://localhost:{PORT}")
        print("🚀 Sistema profissional pronto para uso!")
        
        def signal_handler(sig, frame):
            print("\\n🛑 Parando WhatsFlow Professional...")
            if baileys.is_running:
                baileys.process.terminate()
            server.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        server.serve_forever()
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()