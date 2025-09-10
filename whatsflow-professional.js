// WhatsFlow Professional - JavaScript Client
// Global variables
let instances = [];
let conversations = [];
let currentInstanceId = null;
let currentChat = null;
let websocket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

// WebSocket Connection Management
function initWebSocket() {
    try {
        websocket = new WebSocket(`ws://localhost:8890`);
        
        websocket.onopen = function(event) {
            console.log('✅ WebSocket conectado');
            updateWebSocketStatus(true);
            reconnectAttempts = 0;
        };

        websocket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                console.log('📥 WebSocket message:', data);
                handleWebSocketMessage(data);
            } catch (error) {
                console.error('❌ Erro ao processar mensagem WebSocket:', error);
            }
        };

        websocket.onclose = function(event) {
            console.log('❌ WebSocket desconectado');
            updateWebSocketStatus(false);
            
            // Auto-reconnect
            if (reconnectAttempts < maxReconnectAttempts) {
                reconnectAttempts++;
                console.log(`🔄 Tentando reconectar WebSocket (${reconnectAttempts}/${maxReconnectAttempts})...`);
                setTimeout(initWebSocket, 3000 * reconnectAttempts);
            }
        };

        websocket.onerror = function(error) {
            console.error('❌ Erro WebSocket:', error);
            updateWebSocketStatus(false);
        };
    } catch (error) {
        console.error('❌ Erro ao inicializar WebSocket:', error);
        updateWebSocketStatus(false);
        
        // Retry connection
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            setTimeout(initWebSocket, 5000);
        }
    }
}

function updateWebSocketStatus(connected) {
    const statusEl = document.getElementById('websocketStatus');
    if (connected) {
        statusEl.textContent = '🟢 Tempo Real Ativo';
        statusEl.className = 'websocket-status websocket-connected';
    } else {
        statusEl.textContent = '🔴 Tempo Real Desconectado';
        statusEl.className = 'websocket-status websocket-disconnected';
    }
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'new_message':
            console.log('📨 Nova mensagem recebida:', data.message);
            handleNewMessage(data.message);
            updateStats();
            break;
        case 'instance_connected':
            console.log('✅ Instância conectada:', data.instanceId);
            loadInstances();
            loadInstancesForSelect();
            break;
        case 'instance_disconnected':
            console.log('❌ Instância desconectada:', data.instanceId);
            loadInstances();
            break;
        case 'contact_updated':
            console.log('👤 Contato atualizado:', data.contact);
            if (currentInstanceId) {
                loadConversations();
            }
            break;
        default:
            console.log('📡 Mensagem WebSocket desconhecida:', data);
    }
}

function handleNewMessage(message) {
    // Update conversations list
    if (currentInstanceId === message.instance_id) {
        loadConversations();
    }
    
    // Update current chat if it's the same contact
    if (currentChat && currentChat.phone === message.phone && currentChat.instanceId === message.instance_id) {
        addMessageToChat(message);
    }
}

function addMessageToChat(message) {
    const messagesContainer = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-bubble ${message.direction}`;
    
    messageDiv.innerHTML = `
        <div class="message-content ${message.direction}">
            <div class="message-text">${message.message}</div>
            <div class="message-time">
                ${new Date(message.created_at).toLocaleTimeString('pt-BR', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                })}
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Navigation
function showSection(name) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(name).classList.add('active');
    event.target.classList.add('active');
    
    if (name === 'instances') {
        loadInstances();
    } else if (name === 'dashboard') {
        loadStats();
    } else if (name === 'contacts') {
        loadContacts();
    } else if (name === 'messages') {
        loadInstancesForSelect();
        if (currentInstanceId) {
            loadConversations();
        }
    } else if (name === 'flows') {
        loadFlows();
    }
}

// Instance Management
function showCreateModal() {
    document.getElementById('createModal').classList.add('show');
}

function hideCreateModal() {
    document.getElementById('createModal').classList.remove('show');
    document.getElementById('instanceName').value = '';
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
            loadInstancesForSelect();
            console.log(`✅ Instância "${name}" criada com sucesso!`);
        } else {
            console.error('❌ Erro ao criar instância:', response.status);
        }
    } catch (error) {
        console.error('❌ Erro ao criar instância:', error);
    }
}

async function loadInstances() {
    try {
        const response = await fetch('/api/instances');
        instances = await response.json();
        renderInstances();
    } catch (error) {
        console.error('❌ Erro ao carregar instâncias:', error);
        document.getElementById('instances-container').innerHTML = 
            '<div class="empty-state"><div class="empty-icon">❌</div><div class="empty-title">Erro ao carregar</div></div>';
    }
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
                <button class="btn btn-primary" onclick="showCreateModal()">
                    🚀 Criar Primeira Instância
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = instances.map(instance => `
        <div class="instance-card ${instance.connected ? 'connected' : ''}">
            <div class="instance-header">
                <div class="instance-info">
                    <h3>${instance.name}</h3>
                    <div class="instance-id">ID: ${instance.id.substring(0, 12)}...</div>
                </div>
                <div class="status-indicator ${instance.connected ? 'status-connected' : 'status-disconnected'}">
                    <div class="status-dot"></div>
                    <span>${instance.connected ? 'Conectado' : 'Desconectado'}</span>
                </div>
            </div>
            
            <div class="instance-stats">
                <div class="stat-box">
                    <div class="stat-number">${instance.contacts_count || 0}</div>
                    <div class="stat-label">Contatos</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">${instance.messages_today || 0}</div>
                    <div class="stat-label">Mensagens</div>
                </div>
            </div>
            
            <div class="instance-actions">
                ${!instance.connected ? 
                    `<button class="btn btn-success" onclick="connectInstance('${instance.id}')">
                        🔗 Conectar
                    </button>` :
                    `<button class="btn btn-secondary" disabled>✅ Conectado</button>`
                }
                <button class="btn btn-sm btn-primary" onclick="showQRCode('${instance.id}')" title="Ver QR Code">
                    📋
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteInstance('${instance.id}', '${instance.name}')" title="Excluir">
                    🗑️
                </button>
            </div>
        </div>
    `).join('');
}

async function connectInstance(instanceId) {
    try {
        const response = await fetch(`/api/instances/${instanceId}/connect`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showQRModal(instanceId);
        } else {
            console.error('❌ Erro ao conectar instância');
        }
    } catch (error) {
        console.error('❌ Erro ao conectar instância:', error);
    }
}

async function deleteInstance(id, name) {
    if (!confirm(`Excluir instância "${name}"?`)) return;
    
    try {
        const response = await fetch(`/api/instances/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadInstances();
            loadInstancesForSelect();
        }
    } catch (error) {
        console.error('❌ Erro ao excluir instância:', error);
    }
}

// QR Code Management
let qrInterval = null;
let currentQRInstance = null;

async function showQRModal(instanceId) {
    currentQRInstance = instanceId;
    document.getElementById('qr-instance-name').textContent = instanceId;
    document.getElementById('qrModal').classList.add('show');
    
    loadQRCode();
    qrInterval = setInterval(loadQRCode, 3000);
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
        const statusElement = document.getElementById('connection-status-modal');
        
        if (status.connected && status.user) {
            qrContainer.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">✅</div>
                    <h3 style="color: var(--primary-light); margin-bottom: 0.5rem;">WhatsApp Conectado!</h3>
                    <p><strong>Usuário:</strong> ${status.user.name}</p>
                    <p><strong>Telefone:</strong> ${status.user.phone || status.user.id.split(':')[0]}</p>
                </div>
            `;
            statusElement.textContent = '✅ Conectado com sucesso!';
            statusElement.style.color = 'var(--primary-light)';
            
            if (qrInterval) {
                clearInterval(qrInterval);
                qrInterval = null;
            }
            
            setTimeout(() => {
                closeQRModal();
                loadInstances();
                loadInstancesForSelect();
            }, 3000);
            
        } else if (status.connecting && qrData.qr) {
            const expiresIn = qrData.expiresIn || 60;
            qrContainer.innerHTML = `
                <div style="text-align: center;">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=280x280&data=${encodeURIComponent(qrData.qr)}" 
                         alt="QR Code" style="max-width: 280px; border: 2px solid var(--primary); border-radius: 1rem; box-shadow: var(--shadow-lg);">
                    <p style="margin-top: 1rem; font-weight: 600;">Escaneie com seu WhatsApp</p>
                    <p style="font-size: 0.8rem; color: var(--text-secondary);">Válido por ${expiresIn} segundos</p>
                </div>
            `;
            statusElement.textContent = '📱 Aguardando escaneamento...';
            statusElement.style.color = 'var(--primary)';
            
        } else if (status.connecting) {
            qrContainer.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🔄</div>
                    <p>Preparando conexão...</p>
                </div>
            `;
            statusElement.textContent = '⏳ Preparando...';
            statusElement.style.color = '#f59e0b';
            
        } else {
            qrContainer.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📱</div>
                    <p>Instância desconectada</p>
                    <button class="btn btn-primary" onclick="connectInstance('${currentQRInstance}')" style="margin-top: 1rem;">
                        🔗 Iniciar Conexão
                    </button>
                </div>
            `;
            statusElement.textContent = '❌ Desconectado';
            statusElement.style.color = '#dc2626';
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar QR code:', error);
        document.getElementById('qr-code-container').innerHTML = `
            <div style="text-align: center; padding: 2rem; color: red;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
                <p>Erro ao carregar QR Code</p>
                <button class="btn btn-primary" onclick="loadQRCode()" style="margin-top: 1rem;">
                    🔄 Tentar Novamente
                </button>
            </div>
        `;
    }
}

function closeQRModal() {
    document.getElementById('qrModal').classList.remove('show');
    currentQRInstance = null;
    
    if (qrInterval) {
        clearInterval(qrInterval);
        qrInterval = null;
    }
}

function showQRCode(instanceId) {
    showQRModal(instanceId);
}

// Messages Management
async function loadInstancesForSelect() {
    try {
        const response = await fetch('/api/instances');
        const instances = await response.json();
        
        const select = document.getElementById('instanceSelect');
        select.innerHTML = '<option value="">Selecione uma instância</option>';
        
        instances.forEach(instance => {
            const option = document.createElement('option');
            option.value = instance.id;
            option.textContent = `${instance.name} ${instance.connected ? '(Conectado)' : '(Desconectado)'}`;
            select.appendChild(option);
        });
        
    } catch (error) {
        console.error('❌ Erro ao carregar instâncias para seletor:', error);
    }
}

function switchInstance() {
    const select = document.getElementById('instanceSelect');
    currentInstanceId = select.value;
    
    if (currentInstanceId) {
        loadConversations();
    } else {
        document.getElementById('conversationsList').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">💬</div>
                <div class="empty-title">Nenhuma conversa</div>
                <p>Selecione uma instância para ver as conversas</p>
            </div>
        `;
        clearChat();
    }
}

async function loadConversations() {
    if (!currentInstanceId) return;
    
    try {
        const response = await fetch(`/api/chats?instance_id=${currentInstanceId}`);
        conversations = await response.json();
        renderConversations();
    } catch (error) {
        console.error('❌ Erro ao carregar conversas:', error);
        document.getElementById('conversationsList').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <div class="empty-title">Erro ao carregar</div>
            </div>
        `;
    }
}

function renderConversations() {
    const container = document.getElementById('conversationsList');
    
    if (!conversations || conversations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">💬</div>
                <div class="empty-title">Nenhuma conversa</div>
                <p>As conversas aparecerão aqui quando receber mensagens</p>
            </div>
        `;
        return;
    }

    container.innerHTML = conversations.map(chat => `
        <div class="conversation-item" onclick="openChat('${chat.contact_phone}', '${chat.contact_name}', '${chat.instance_id}')">
            <div class="conversation-avatar">
                ${getContactInitial(chat.contact_name, chat.contact_phone)}
            </div>
            <div class="conversation-info">
                <div class="conversation-name">${getContactDisplayName(chat.contact_name, chat.contact_phone)}</div>
                <div class="conversation-last-message">${chat.last_message || 'Nova conversa'}</div>
            </div>
            <div class="conversation-meta">
                <div class="conversation-time">
                    ${chat.last_message_time ? new Date(chat.last_message_time).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : ''}
                </div>
                ${chat.unread_count > 0 ? `<div class="unread-badge">${chat.unread_count}</div>` : ''}
            </div>
        </div>
    `).join('');
}

function getContactDisplayName(name, phone) {
    // Se o nome é um número de telefone ou está vazio, usar o número formatado
    if (!name || name === phone || /^\+?\d+$/.test(name)) {
        return formatPhoneNumber(phone);
    }
    return name;
}

function formatPhoneNumber(phone) {
    // Formatar número do telefone para exibição
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 13 && cleaned.startsWith('55')) {
        return `+55 (${cleaned.substr(2, 2)}) ${cleaned.substr(4, 5)}-${cleaned.substr(9)}`;
    } else if (cleaned.length === 11) {
        return `(${cleaned.substr(0, 2)}) ${cleaned.substr(2, 5)}-${cleaned.substr(7)}`;
    }
    return phone;
}

function getContactInitial(name, phone) {
    if (name && name !== phone && !/^\+?\d+$/.test(name)) {
        return name.charAt(0).toUpperCase();
    }
    // Se é número de telefone, usar o último dígito
    const digits = phone.replace(/\D/g, '');
    return digits.slice(-1);
}

function searchConversations() {
    const query = document.getElementById('searchConversations').value.toLowerCase();
    const items = document.querySelectorAll('.conversation-item');
    
    items.forEach(item => {
        const name = item.querySelector('.conversation-name').textContent.toLowerCase();
        const message = item.querySelector('.conversation-last-message').textContent.toLowerCase();
        
        if (name.includes(query) || message.includes(query)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

async function openChat(phone, contactName, instanceId) {
    currentChat = { phone, contactName, instanceId };
    
    // Update active conversation
    document.querySelectorAll('.conversation-item').forEach(item => item.classList.remove('active'));
    event.currentTarget.classList.add('active');
    
    // Update chat header
    const displayName = getContactDisplayName(contactName, phone);
    document.getElementById('chatContactName').textContent = displayName;
    document.getElementById('chatContactPhone').textContent = formatPhoneNumber(phone);
    document.getElementById('chatAvatar').textContent = getContactInitial(contactName, phone);
    
    // Show chat header and input area
    document.getElementById('chatHeader').classList.add('active');
    document.getElementById('messageInputArea').classList.add('active');
    
    // Load messages
    await loadChatMessages(phone, instanceId);
}

async function loadChatMessages(phone, instanceId) {
    try {
        const response = await fetch(`/api/messages?phone=${phone}&instance_id=${instanceId}`);
        const messages = await response.json();
        
        const container = document.getElementById('messagesContainer');
        
        if (messages.length === 0) {
            container.innerHTML = `
                <div class="empty-chat-state">
                    <div class="empty-chat-icon">💭</div>
                    <h3>Nenhuma mensagem ainda</h3>
                    <p>Comece uma conversa!</p>
                </div>
            `;
        } else {
            container.innerHTML = messages.map(msg => `
                <div class="message-bubble ${msg.direction}">
                    <div class="message-content ${msg.direction}">
                        <div class="message-text">${msg.message}</div>
                        <div class="message-time">
                            ${new Date(msg.created_at).toLocaleTimeString('pt-BR', { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                            })}
                        </div>
                    </div>
                </div>
            `).join('');
            
            container.scrollTop = container.scrollHeight;
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar mensagens:', error);
        document.getElementById('messagesContainer').innerHTML = `
            <div class="empty-chat-state">
                <div style="color: red;">❌ Erro ao carregar mensagens</div>
            </div>
        `;
    }
}

function clearChat() {
    currentChat = null;
    document.getElementById('chatHeader').classList.remove('active');
    document.getElementById('messageInputArea').classList.remove('active');
    document.getElementById('messagesContainer').innerHTML = `
        <div class="empty-chat-state">
            <div class="empty-chat-icon">💭</div>
            <h3>Selecione uma conversa</h3>
            <p>Escolha uma conversa da lista para visualizar mensagens</p>
        </div>
    `;
}

function handleMessageKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    if (!currentChat) return;
    
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    try {
        const response = await fetch(`/api/messages/send/${currentChat.instanceId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                to: currentChat.phone,
                message: message
            })
        });
        
        if (response.ok) {
            messageInput.value = '';
            
            // Add message to UI immediately
            const container = document.getElementById('messagesContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message-bubble outgoing';
            messageDiv.innerHTML = `
                <div class="message-content outgoing">
                    <div class="message-text">${message}</div>
                    <div class="message-time">
                        ${new Date().toLocaleTimeString('pt-BR', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                        })}
                    </div>
                </div>
            `;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
            
            // Update conversations list
            loadConversations();
            
        } else {
            console.error('❌ Erro ao enviar mensagem');
        }
        
    } catch (error) {
        console.error('❌ Erro ao enviar mensagem:', error);
    }
}

function refreshMessages() {
    if (currentInstanceId) {
        loadConversations();
        if (currentChat) {
            loadChatMessages(currentChat.phone, currentChat.instanceId);
        }
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
            headers: { 'Content-Type': 'application/json' },
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
        console.error('❌ Erro ao enviar webhook:', error);
        alert('❌ Erro de conexão');
    }
}

// Contacts Management
async function loadContacts() {
    try {
        const response = await fetch('/api/contacts');
        const contacts = await response.json();
        renderContacts(contacts);
    } catch (error) {
        console.error('❌ Erro ao carregar contatos:', error);
        document.getElementById('contacts-container').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <div class="empty-title">Erro ao carregar contatos</div>
            </div>
        `;
    }
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
        <div class="card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div class="conversation-avatar">
                        ${getContactInitial(contact.name, contact.phone)}
                    </div>
                    <div>
                        <div style="font-weight: 600; color: var(--text-primary);">${getContactDisplayName(contact.name, contact.phone)}</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">📱 ${formatPhoneNumber(contact.phone)}</div>
                        <div style="color: var(--text-secondary); font-size: 0.8rem;">Adicionado: ${new Date(contact.created_at).toLocaleDateString('pt-BR')}</div>
                    </div>
                </div>
                <button class="btn btn-primary" onclick="startChatFromContact('${contact.phone}', '${contact.name}')">
                    💬 Conversar
                </button>
            </div>
        </div>
    `).join('');
}

function startChatFromContact(phone, name) {
    // Switch to messages tab and start chat
    showSection('messages');
    setTimeout(() => {
        if (currentInstanceId) {
            openChat(phone, name, currentInstanceId);
        } else {
            alert('❌ Selecione uma instância primeiro na aba Mensagens');
        }
    }, 500);
}

// Flows Management
async function loadFlows() {
    try {
        const response = await fetch('/api/flows');
        const flows = await response.json();
        renderFlows(flows);
    } catch (error) {
        console.error('❌ Erro ao carregar fluxos:', error);
        document.getElementById('flows-container').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <div class="empty-title">Erro ao carregar fluxos</div>
            </div>
        `;
    }
}

function renderFlows(flows) {
    const container = document.getElementById('flows-container');
    
    if (!flows || flows.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🎯</div>
                <div class="empty-title">Nenhum fluxo criado ainda</div>
                <p>Crie fluxos de automação drag-and-drop para otimizar seu atendimento</p>
                <br>
                <button class="btn btn-primary" onclick="createNewFlow()">
                    🚀 Criar Primeiro Fluxo
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="flows-grid">
            ${flows.map(flow => `
                <div class="flow-card">
                    <div class="flow-card-header">
                        <div>
                            <h3>${flow.name}</h3>
                            <p style="color: var(--text-secondary); font-size: 0.9rem;">${flow.description || 'Sem descrição'}</p>
                        </div>
                        <div class="flow-status ${flow.active ? 'active' : 'inactive'}">
                            ${flow.active ? 'Ativo' : 'Inativo'}
                        </div>
                    </div>
                    
                    <div style="margin: 1rem 0; padding: 1rem; background: var(--bg-primary); border-radius: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.8rem; color: var(--text-secondary);">Nós:</span>
                            <span style="font-weight: 600;">${flow.nodes ? flow.nodes.length : 0}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.8rem; color: var(--text-secondary);">Criado:</span>
                            <span style="font-size: 0.8rem;">${new Date(flow.created_at).toLocaleDateString('pt-BR')}</span>
                        </div>
                    </div>
                    
                    <div class="flow-actions">
                        <button class="btn btn-sm btn-primary" onclick="editFlow('${flow.id}')">
                            ✏️ Editar
                        </button>
                        <button class="btn btn-sm ${flow.active ? 'btn-secondary' : 'btn-success'}" onclick="toggleFlow('${flow.id}', ${flow.active})">
                            ${flow.active ? '⏸️ Pausar' : '▶️ Ativar'}
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteFlow('${flow.id}', '${flow.name}')">
                            🗑️ Excluir
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function createNewFlow() {
    alert('🚧 Editor de Fluxos em Desenvolvimento!\n\nEm breve você poderá criar fluxos de automação drag-and-drop com ReactFlow.\n\nFuncionalidades:\n• Nodes de mensagem, condição, delay\n• Editor visual drag-and-drop\n• Automação de respostas\n• Integração com instâncias');
}

function editFlow(flowId) {
    alert(`🚧 Editar fluxo ${flowId} - Em desenvolvimento!`);
}

function toggleFlow(flowId, currentStatus) {
    console.log(`Toggle flow ${flowId} from ${currentStatus} to ${!currentStatus}`);
    // Implementar toggle do fluxo
}

function deleteFlow(flowId, flowName) {
    if (confirm(`Excluir fluxo "${flowName}"?`)) {
        console.log(`Delete flow ${flowId}`);
        // Implementar exclusão do fluxo
    }
}

// Stats Management
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('contacts-count').textContent = stats.contacts_count || 0;
        document.getElementById('conversations-count').textContent = stats.conversations_count || 0;
        document.getElementById('messages-count').textContent = stats.messages_count || 0;
        document.getElementById('instances-count').textContent = stats.instances_count || 0;
    } catch (error) {
        console.error('❌ Erro ao carregar estatísticas:', error);
    }
}

function updateStats() {
    loadStats();
}

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando WhatsFlow Professional...');
    
    // Initialize WebSocket
    initWebSocket();
    
    // Load initial data
    loadStats();
    loadInstances();
    loadInstancesForSelect();
    
    // Setup intervals for updates
    setInterval(loadStats, 30000); // Update stats every 30 seconds
    
    // Setup modal click handlers
    document.getElementById('createModal').addEventListener('click', function(e) {
        if (e.target === this) this.classList.remove('show');
    });
    
    document.getElementById('qrModal').addEventListener('click', function(e) {
        if (e.target === this) closeQRModal();
    });
    
    console.log('✅ WhatsFlow Professional iniciado com sucesso!');
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (websocket) websocket.close();
    if (qrInterval) clearInterval(qrInterval);
});