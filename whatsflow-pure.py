#!/usr/bin/env python3
"""
WhatsFlow Pure - Versão 100% Python Puro
Sistema de Automação WhatsApp APENAS com bibliotecas padrão do Python

Requisitos: APENAS Python 3 (bibliotecas built-in)
Instalação: python3 whatsflow-pure.py
Acesso: http://localhost:8888
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configurações
DB_FILE = "whatsflow.db"
PORT = 8888

# HTML completo da aplicação (CSS inline, JS inline)
HTML_APP = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsFlow Pure - Zero Dependências</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            min-height: 100vh;
            color: #1f2937;
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        /* Header */
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { 
            font-size: 2.5rem; 
            margin-bottom: 10px; 
            text-shadow: 0 2px 4px rgba(0,0,0,0.3); 
        }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .header .subtitle {
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
            font-size: 0.9rem;
        }
        
        /* Navigation */
        .nav {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .nav-btn {
            background: rgba(255,255,255,0.9);
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        .nav-btn:hover { 
            background: white; 
            transform: translateY(-2px); 
            box-shadow: 0 4px 12px rgba(0,0,0,0.2); 
        }
        .nav-btn.active { 
            background: white; 
            color: #4f46e5; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.3); 
        }
        
        /* Cards */
        .card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        /* Status indicator */
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 500;
            font-size: 14px;
        }
        .status-connected { background: #d1fae5; color: #065f46; }
        .status-disconnected { background: #fef2f2; color: #991b1b; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; }
        .status-connected .status-dot { background: #10b981; }
        .status-disconnected .status-dot { background: #ef4444; }
        
        /* Stats */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }
        .stat-number { 
            font-size: 2rem; 
            font-weight: bold; 
            color: #4f46e5; 
            margin-bottom: 5px; 
        }
        .stat-label { color: #6b7280; font-size: 14px; }
        
        /* Instances */
        .instances-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .instance-card {
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            background: white;
            transition: all 0.3s ease;
        }
        .instance-card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-color: #4f46e5;
        }
        
        .instance-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        .instance-name { 
            font-size: 1.2rem; 
            font-weight: 600; 
            color: #1f2937; 
            margin-bottom: 5px; 
        }
        .instance-id { 
            font-size: 12px; 
            color: #6b7280; 
            font-family: 'Courier New', monospace; 
        }
        
        .instance-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }
        .instance-stat {
            text-align: center;
            padding: 15px;
            background: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        .instance-stat-number { 
            font-size: 1.5rem; 
            font-weight: bold; 
            color: #4f46e5; 
            display: block;
        }
        .instance-stat-label { 
            font-size: 12px; 
            color: #6b7280; 
            margin-top: 5px; 
        }
        
        .instance-actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        /* Buttons */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
            font-size: 14px;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        .btn-primary { background: #4f46e5; color: white; }
        .btn-success { background: #10b981; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .btn-secondary { background: #6b7280; color: white; }
        .btn:hover { 
            transform: translateY(-1px); 
            opacity: 0.9; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .btn:active { transform: translateY(0); }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal.show { display: flex; }
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 16px;
            width: 90%;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .modal-title { 
            font-size: 1.3rem; 
            font-weight: 600; 
            color: #1f2937; 
        }
        .close-btn { 
            background: none; 
            border: none; 
            font-size: 24px; 
            cursor: pointer; 
            color: #6b7280; 
            padding: 5px;
            border-radius: 4px;
        }
        .close-btn:hover { 
            color: #374151; 
            background: #f3f4f6;
        }
        
        /* Forms */
        .form-group { margin-bottom: 20px; }
        .form-label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 500; 
            color: #374151; 
        }
        .form-input {
            width: 100%;
            padding: 12px;
            border: 2px solid #d1d5db;
            border-radius: 6px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        .form-input:focus { 
            outline: none; 
            border-color: #4f46e5; 
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); 
        }
        .form-help { 
            font-size: 12px; 
            color: #6b7280; 
            margin-top: 5px; 
        }
        
        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6b7280;
        }
        .empty-icon { 
            font-size: 4rem; 
            margin-bottom: 20px; 
            opacity: 0.5;
        }
        .empty-title { 
            font-size: 1.5rem; 
            font-weight: 600; 
            color: #1f2937; 
            margin-bottom: 10px; 
        }
        .empty-description { 
            margin-bottom: 30px; 
            line-height: 1.6; 
        }
        
        /* QR Section */
        .qr-section { text-align: center; padding: 20px; }
        .qr-instructions {
            text-align: left;
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 2px solid #e5e7eb;
        }
        .qr-instructions h4 { 
            color: #1f2937; 
            margin-bottom: 15px; 
            font-size: 1.1rem;
        }
        .qr-instructions ol { 
            color: #6b7280; 
            line-height: 1.6; 
            padding-left: 20px;
        }
        .qr-instructions li { margin-bottom: 8px; }
        .qr-code-container {
            background: white;
            padding: 20px;
            border-radius: 12px;
            display: inline-block;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin: 20px 0;
            border: 2px solid #e5e7eb;
        }
        .qr-footer { margin-top: 20px; }
        .qr-demo-note { 
            color: #f59e0b; 
            font-weight: 500; 
            background: #fef3c7;
            padding: 10px;
            border-radius: 6px;
            display: inline-block;
        }
        
        /* Loading */
        .loading { 
            text-align: center; 
            padding: 40px; 
            color: #6b7280; 
        }
        .loading-spinner { 
            font-size: 2rem; 
            margin-bottom: 15px; 
            animation: spin 1s linear infinite; 
        }
        @keyframes spin { 
            0% { transform: rotate(0deg); } 
            100% { transform: rotate(360deg); } 
        }
        
        /* Success message */
        .success-message {
            background: #d1fae5;
            color: #065f46;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
            font-weight: 500;
        }
        
        /* Section visibility */
        .section { display: none; }
        .section.active { display: block; }
        
        /* Responsive */
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .header h1 { font-size: 2rem; }
            .nav { justify-content: center; }
            .stats-grid { grid-template-columns: 1fr; }
            .instances-grid { grid-template-columns: 1fr; }
            .instance-actions { flex-direction: column; }
            .modal-content { 
                margin: 20px; 
                width: calc(100% - 40px); 
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 WhatsFlow Pure</h1>
            <p>Sistema de Automação WhatsApp - 100% Python Puro</p>
            <div class="subtitle">✅ Zero dependências • Zero npm • Zero complicações</div>
        </div>
        
        <nav class="nav">
            <button class="nav-btn active" onclick="showSection('dashboard')">📊 Dashboard</button>
            <button class="nav-btn" onclick="showSection('instances')">📱 Instâncias</button>
            <button class="nav-btn" onclick="showSection('messages')">💬 Mensagens</button>
            <button class="nav-btn" onclick="showSection('info')">ℹ️ Info</button>
        </nav>
        
        <!-- Dashboard Section -->
        <div id="dashboard" class="section active">
            <div class="card">
                <h2>🔗 Status da Conexão</h2>
                <div class="status-indicator status-disconnected">
                    <div class="status-dot"></div>
                    <span>WhatsApp não conectado (modo demonstração)</span>
                </div>
                <div class="success-message">
                    ✅ WhatsFlow Pure funcionando sem dependências externas!
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Estatísticas do Sistema</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="contacts-count">0</div>
                        <div class="stat-label">Contatos registrados</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="conversations-count">0</div>
                        <div class="stat-label">Conversas ativas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="messages-count">0</div>
                        <div class="stat-label">Mensagens processadas</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Instances Section -->
        <div id="instances" class="section">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h2>📱 Instâncias WhatsApp</h2>
                    <button class="btn btn-primary" onclick="showCreateModal()">➕ Nova Instância</button>
                </div>
                <div id="instances-container" class="instances-grid">
                    <div class="loading">
                        <div class="loading-spinner">🔄</div>
                        <p>Carregando instâncias...</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Messages Section -->
        <div id="messages" class="section">
            <div class="card">
                <h2>💬 Central de Mensagens</h2>
                <div class="empty-state">
                    <div class="empty-icon">💬</div>
                    <div class="empty-title">Central de Mensagens</div>
                    <div class="empty-description">
                        Esta funcionalidade permite gerenciar todas as conversas do WhatsApp de forma centralizada. 
                        Implementação disponível na versão completa.
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Info Section -->
        <div id="info" class="section">
            <div class="card">
                <h2>ℹ️ Informações do Sistema</h2>
                <div style="line-height: 1.8;">
                    <p><strong>🤖 WhatsFlow Pure</strong> - Versão sem dependências externas</p>
                    <p><strong>🐍 Python:</strong> Apenas bibliotecas built-in</p>
                    <p><strong>🗄️ Banco:</strong> SQLite (criado automaticamente)</p>
                    <p><strong>🌐 Servidor:</strong> HTTP simples integrado</p>
                    <p><strong>🎨 Interface:</strong> HTML + CSS puro</p>
                    <p><strong>📡 API:</strong> REST endpoints funcionais</p>
                    <p><strong>🔧 Requisitos:</strong> Python 3.6+ (apenas!)</p>
                </div>
                
                <h3 style="margin: 20px 0 10px 0;">📋 APIs Disponíveis:</h3>
                <div style="font-family: monospace; background: #f3f4f6; padding: 15px; border-radius: 8px;">
                    <div>GET /api/instances - Listar instâncias</div>
                    <div>POST /api/instances - Criar instância</div>
                    <div>DELETE /api/instances/{id} - Excluir instância</div>
                    <div>GET /api/stats - Estatísticas</div>
                </div>
                
                <h3 style="margin: 20px 0 10px 0;">✅ Características:</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div style="background: #f0fdf4; padding: 10px; border-radius: 6px; text-align: center;">
                        <strong>Zero npm</strong><br><small>Sem Node.js</small>
                    </div>
                    <div style="background: #f0fdf4; padding: 10px; border-radius: 6px; text-align: center;">
                        <strong>Zero MongoDB</strong><br><small>Usa SQLite</small>
                    </div>
                    <div style="background: #f0fdf4; padding: 10px; border-radius: 6px; text-align: center;">
                        <strong>Zero sudo</strong><br><small>Usuário normal</small>
                    </div>
                    <div style="background: #f0fdf4; padding: 10px; border-radius: 6px; text-align: center;">
                        <strong>Zero frameworks</strong><br><small>CSS puro</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Create Instance Modal -->
    <div id="createModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">➕ Nova Instância WhatsApp</div>
                <button class="close-btn" onclick="hideCreateModal()">&times;</button>
            </div>
            <form onsubmit="createInstance(event)">
                <div class="form-group">
                    <label class="form-label">📝 Nome da Instância</label>
                    <input type="text" id="instanceName" class="form-input" 
                           placeholder="Ex: WhatsApp Vendas, WhatsApp Suporte..." 
                           required maxlength="50">
                    <div class="form-help">Este nome aparecerá na lista de instâncias e relatórios</div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button type="button" class="btn btn-secondary" onclick="hideCreateModal()">❌ Cancelar</button>
                    <button type="submit" class="btn btn-success" style="flex: 1;">✅ Criar Instância</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- QR Code Modal -->
    <div id="qrModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">📱 Conectar WhatsApp</div>
                <button class="close-btn" onclick="hideQRModal()">&times;</button>
            </div>
            <div class="qr-section">
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
                
                <div class="qr-code-container">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=whatsflow-pure-demo" 
                         alt="QR Code WhatsApp" style="border-radius: 8px;">
                </div>
                
                <div class="qr-footer">
                    <div class="qr-demo-note">🚧 Modo demonstração - QR Code simulado para testes</div>
                </div>
                
                <div style="margin-top: 30px; text-align: center;">
                    <button class="btn btn-danger" onclick="hideQRModal()">🚫 Fechar</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global state
        let instances = [];
        let currentInstanceId = null;

        // Navigation
        function showSection(sectionName) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
            });
            
            // Remove active class from all nav buttons
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected section
            document.getElementById(sectionName).classList.add('active');
            event.target.classList.add('active');
            
            // Load data if needed
            if (sectionName === 'instances') {
                loadInstances();
            } else if (sectionName === 'dashboard') {
                loadStats();
            }
        }

        // Modal functions
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
            
            // Simulate connection after 3 seconds
            setTimeout(() => {
                hideQRModal();
                alert('✅ WhatsApp conectado com sucesso! (modo demonstração)');
                loadInstances();
            }, 3000);
        }

        function hideQRModal() {
            document.getElementById('qrModal').classList.remove('show');
            currentInstanceId = null;
        }

        // API functions
        async function loadInstances() {
            try {
                const response = await fetch('/api/instances');
                if (response.ok) {
                    instances = await response.json();
                    renderInstances();
                } else {
                    throw new Error('Failed to load instances');
                }
            } catch (error) {
                console.error('Error loading instances:', error);
                document.getElementById('instances-container').innerHTML = `
                    <div class="empty-state" style="grid-column: 1 / -1;">
                        <div class="empty-icon">❌</div>
                        <div class="empty-title">Erro ao carregar</div>
                        <div class="empty-description">Não foi possível carregar as instâncias. Verifique se o servidor está funcionando.</div>
                    </div>
                `;
            }
        }

        async function createInstance(event) {
            event.preventDefault();
            const name = document.getElementById('instanceName').value.trim();
            
            if (!name) return;
            
            try {
                const response = await fetch('/api/instances', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name })
                });
                
                if (response.ok) {
                    hideCreateModal();
                    loadInstances();
                    alert(`✅ Instância "${name}" criada com sucesso!`);
                } else {
                    throw new Error('Failed to create instance');
                }
            } catch (error) {
                console.error('Error creating instance:', error);
                alert('❌ Erro ao criar instância. Tente novamente.');
            }
        }

        async function deleteInstance(instanceId, instanceName) {
            if (!confirm(`Tem certeza que deseja excluir a instância "${instanceName}"?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/instances/${instanceId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    loadInstances();
                    alert(`✅ Instância "${instanceName}" excluída com sucesso!`);
                } else {
                    throw new Error('Failed to delete instance');
                }
            } catch (error) {
                console.error('Error deleting instance:', error);
                alert('❌ Erro ao excluir instância. Tente novamente.');
            }
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                if (response.ok) {
                    const stats = await response.json();
                    document.getElementById('contacts-count').textContent = stats.contacts_count || 0;
                    document.getElementById('conversations-count').textContent = stats.conversations_count || 0;
                    document.getElementById('messages-count').textContent = stats.messages_count || 0;
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        // Render functions
        function renderInstances() {
            const container = document.getElementById('instances-container');
            
            if (!instances || instances.length === 0) {
                container.innerHTML = `
                    <div class="empty-state" style="grid-column: 1 / -1;">
                        <div class="empty-icon">📱</div>
                        <div class="empty-title">Nenhuma instância WhatsApp</div>
                        <div class="empty-description">Crie sua primeira instância para começar a gerenciar suas automações do WhatsApp.</div>
                        <button class="btn btn-primary" onclick="showCreateModal()">🚀 Criar Primeira Instância</button>
                    </div>
                `;
                return;
            }

            container.innerHTML = instances.map(instance => `
                <div class="instance-card">
                    <div class="instance-header">
                        <div>
                            <div class="instance-name">${escapeHtml(instance.name)}</div>
                            <div class="instance-id">ID: ${instance.id.substring(0, 8)}...</div>
                        </div>
                        <div class="status-indicator ${instance.connected ? 'status-connected' : 'status-disconnected'}">
                            <div class="status-dot"></div>
                            <span>${instance.connected ? 'Conectado' : 'Desconectado'}</span>
                        </div>
                    </div>
                    
                    <div class="instance-stats">
                        <div class="instance-stat">
                            <span class="instance-stat-number">${instance.contacts_count || 0}</span>
                            <div class="instance-stat-label">Contatos</div>
                        </div>
                        <div class="instance-stat">
                            <span class="instance-stat-number">${instance.messages_today || 0}</span>
                            <div class="instance-stat-label">Mensagens hoje</div>
                        </div>
                    </div>
                    
                    <div class="instance-actions">
                        ${!instance.connected ? 
                            `<button class="btn btn-success" onclick="showQRModal('${instance.id}')" style="flex: 1;">🔗 Conectar</button>` :
                            `<button class="btn btn-secondary" onclick="disconnectInstance('${instance.id}')" style="flex: 1;">⏸️ Desconectar</button>`
                        }
                        <button class="btn btn-danger" onclick="deleteInstance('${instance.id}', '${escapeHtml(instance.name)}')">🗑️ Excluir</button>
                    </div>
                </div>
            `).join('');
        }

        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🤖 WhatsFlow Pure inicializado!');
            loadStats();
            
            // Update stats every 30 seconds
            setInterval(loadStats, 30000);
            
            // Close modals when clicking outside
            document.querySelectorAll('.modal').forEach(modal => {
                modal.addEventListener('click', function(e) {
                    if (e.target === modal) {
                        modal.classList.remove('show');
                    }
                });
            });
            
            console.log('✅ Interface carregada com sucesso!');
        });
    </script>
</body>
</html>'''

# Database initialization
def init_database():
    """Initialize SQLite database with tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create instances table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instances (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            connected INTEGER DEFAULT 0,
            contacts_count INTEGER DEFAULT 0,
            messages_today INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            instance_id TEXT,
            last_message TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            instance_id TEXT,
            contact_id TEXT,
            message TEXT NOT NULL,
            direction TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_sample_data():
    """Add sample data for demonstration"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM instances")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Add sample instances
    current_time = datetime.now(timezone.utc).isoformat()
    
    sample_instances = [
        {
            "id": str(uuid.uuid4()),
            "name": "WhatsApp Vendas",
            "connected": 0,
            "contacts_count": 5,
            "messages_today": 12
        },
        {
            "id": str(uuid.uuid4()),
            "name": "WhatsApp Suporte",
            "connected": 1,
            "contacts_count": 8,
            "messages_today": 25
        }
    ]
    
    for instance in sample_instances:
        cursor.execute("""
            INSERT INTO instances (id, name, connected, contacts_count, messages_today, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            instance["id"],
            instance["name"],
            instance["connected"],
            instance["contacts_count"],
            instance["messages_today"],
            current_time
        ))
    
    # Add sample contacts
    sample_contacts = [
        {"name": "João Silva", "phone": "+5511999999999"},
        {"name": "Maria Santos", "phone": "+5511888888888"},
        {"name": "Pedro Costa", "phone": "+5511777777777"},
        {"name": "Ana Oliveira", "phone": "+5511666666666"},
        {"name": "Carlos Lima", "phone": "+5511555555555"}
    ]
    
    for i, contact in enumerate(sample_contacts):
        cursor.execute("""
            INSERT INTO contacts (id, name, phone, instance_id, last_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            contact["name"],
            contact["phone"],
            sample_instances[0]["id"],
            f"Mensagem exemplo {i+1}",
            current_time
        ))
    
    # Add sample messages
    for i in range(15):
        cursor.execute("""
            INSERT INTO messages (id, instance_id, contact_id, message, direction, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            sample_instances[0]["id"],
            str(uuid.uuid4()),
            f"Mensagem de exemplo {i+1}",
            "incoming" if i % 2 == 0 else "outgoing",
            current_time
        ))
    
    conn.commit()
    conn.close()

# HTTP Request Handler
class WhatsFlowHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_html_response(HTML_APP)
        elif self.path == '/api/instances':
            self.handle_get_instances()
        elif self.path == '/api/stats':
            self.handle_get_stats()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        if self.path == '/api/instances':
            self.handle_create_instance()
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

def main():
    print("🤖 WhatsFlow Pure - 100% Python Puro")
    print("=" * 45)
    print("✅ Zero dependências externas")
    print("✅ Zero npm/Node.js")
    print("✅ Zero MongoDB")
    print("✅ Zero sudo")
    print("✅ Zero TailwindCSS")
    print()
    
    # Initialize database
    print("📁 Inicializando banco SQLite...")
    init_database()
    add_sample_data()
    
    print("✅ WhatsFlow Pure configurado!")
    print(f"🌐 Acesse: http://localhost:{PORT}")
    print(f"📁 Banco: {os.path.abspath(DB_FILE)}")
    print("🚀 Servidor HTTP iniciando...")
    print("   Para parar: Ctrl+C")
    print()
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), WhatsFlowHandler)
        print(f"✅ Servidor rodando na porta {PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 WhatsFlow Pure finalizado!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()