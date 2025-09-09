import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function MessagesCenter() {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [webhooks, setWebhooks] = useState([]);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('all');
  const [showWebhookModal, setShowWebhookModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const messagesEndRef = useRef(null);

  // Buscar conversas
  useEffect(() => {
    fetchConversations();
    fetchWebhooks();
    fetchDevices();
    
    // Polling para atualizações em tempo real
    const interval = setInterval(() => {
      fetchConversations();
      if (selectedConversation) {
        fetchMessages(selectedConversation.id);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [selectedConversation, selectedDevice]);

  // Auto scroll para última mensagem
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchConversations = async () => {
    try {
      const deviceParam = selectedDevice !== 'all' ? `?device_id=${selectedDevice}` : '';
      const response = await axios.get(`${API}/contacts${deviceParam}`);
      setConversations(response.data);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${API}/devices`);
      setDevices(response.data);
    } catch (error) {
      console.error('Failed to fetch devices:', error);
    }
  };

  const fetchMessages = async (contactId) => {
    try {
      const response = await axios.get(`${API}/contacts/${contactId}/messages`);
      setMessages(response.data);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const fetchWebhooks = async () => {
    try {
      const response = await axios.get(`${API}/webhooks`);
      setWebhooks(response.data || []);
    } catch (error) {
      console.error('Failed to fetch webhooks:', error);
    }
  };

  const handleConversationSelect = (conversation) => {
    setSelectedConversation(conversation);
    fetchMessages(conversation.id);
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;

    try {
      await axios.post(`${API}/whatsapp/send`, {
        phone_number: selectedConversation.phone_number,
        message: newMessage
      });

      // Adicionar mensagem localmente para feedback imediato
      const newMsg = {
        id: Date.now().toString(),
        direction: 'outgoing',
        message: newMessage,
        timestamp: new Date().toISOString(),
        delivered: false
      };
      
      setMessages(prev => [...prev, newMsg]);
      setNewMessage('');
      
      // Atualizar mensagens do servidor
      setTimeout(() => fetchMessages(selectedConversation.id), 1000);
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Erro ao enviar mensagem');
    }
  };

  const triggerWebhook = async (webhook, contact) => {
    try {
      const webhookData = {
        contact_name: contact.name,
        phone_number: contact.phone_number,
        jid: `${contact.phone_number}@s.whatsapp.net`,
        timestamp: new Date().toISOString(),
        webhook_name: webhook.name,
        tags: contact.tags || []
      };

      await axios.post(`${API}/webhooks/trigger`, {
        webhook_id: webhook.id,
        webhook_url: webhook.url,
        data: webhookData
      });

      alert(`Webhook "${webhook.name}" disparado com sucesso!`);
    } catch (error) {
      console.error('Failed to trigger webhook:', error);
      alert('Erro ao disparar webhook');
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.phone_number.includes(searchTerm)
  );

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Hoje';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Ontem';
    } else {
      return date.toLocaleDateString('pt-BR');
    }
  };

  if (loading) {
    return <div className="loading">Carregando conversas...</div>;
  }

  return (
    <div className="messages-center">
      <div className="messages-layout">
        {/* Sidebar de Conversas */}
        <div className="conversations-sidebar">
          <div className="conversations-header">
            <h3>💬 Conversas</h3>
            <div className="conversations-actions">
              <button
                onClick={() => setShowWebhookModal(true)}
                className="webhook-button"
              >
                🔗 Webhooks
              </button>
            </div>
          </div>

          <div className="search-container">
            <input
              type="text"
              placeholder="🔍 Buscar conversa..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="conversations-list">
            {filteredConversations.length === 0 ? (
              <div className="empty-conversations">
                <p>Nenhuma conversa encontrada</p>
              </div>
            ) : (
              filteredConversations.map(conversation => (
                <div
                  key={conversation.id}
                  className={`conversation-item ${selectedConversation?.id === conversation.id ? 'active' : ''}`}
                  onClick={() => handleConversationSelect(conversation)}
                >
                  <div className="conversation-avatar">
                    {conversation.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="conversation-info">
                    <div className="conversation-name">{conversation.name}</div>
                    <div className="conversation-phone">{conversation.phone_number}</div>
                    <div className="conversation-time">
                      {formatDate(conversation.last_message_at)}
                    </div>
                  </div>
                  <div className="conversation-actions">
                    {webhooks.map(webhook => (
                      <button
                        key={webhook.id}
                        onClick={(e) => {
                          e.stopPropagation();
                          triggerWebhook(webhook, conversation);
                        }}
                        className="trigger-webhook"
                        title={`Disparar ${webhook.name}`}
                      >
                        🚀
                      </button>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Área de Chat */}
        <div className="chat-area">
          {selectedConversation ? (
            <>
              <div className="chat-header">
                <div className="contact-info">
                  <div className="contact-avatar">
                    {selectedConversation.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="contact-details">
                    <h4>{selectedConversation.name}</h4>
                    <p>{selectedConversation.phone_number}</p>
                    <p className="jid">JID: {selectedConversation.phone_number}@s.whatsapp.net</p>
                  </div>
                </div>
                <div className="chat-actions">
                  {webhooks.map(webhook => (
                    <button
                      key={webhook.id}
                      onClick={() => triggerWebhook(webhook, selectedConversation)}
                      className="webhook-trigger-btn"
                    >
                      🎯 {webhook.name}
                    </button>
                  ))}
                </div>
              </div>

              <div className="messages-container">
                {messages.length === 0 ? (
                  <div className="empty-messages">
                    <p>Nenhuma mensagem ainda</p>
                  </div>
                ) : (
                  messages.map(message => (
                    <div
                      key={message.id}
                      className={`message ${message.direction === 'outgoing' ? 'outgoing' : 'incoming'}`}
                    >
                      <div className="message-content">
                        {message.message}
                      </div>
                      <div className="message-time">
                        {formatTime(message.timestamp)}
                        {message.direction === 'outgoing' && (
                          <span className={`delivery-status ${message.delivered ? 'delivered' : 'sending'}`}>
                            {message.delivered ? '✓✓' : '⏳'}
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              <div className="message-input-container">
                <div className="message-input">
                  <input
                    type="text"
                    placeholder="Digite sua mensagem..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    className="message-field"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!newMessage.trim()}
                    className="send-button"
                  >
                    📤
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="no-conversation-selected">
              <div className="no-chat-icon">💬</div>
              <h3>Selecione uma conversa</h3>
              <p>Escolha uma conversa da lista para começar a visualizar mensagens</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Webhooks */}
      {showWebhookModal && (
        <WebhookModal
          webhooks={webhooks}
          onClose={() => setShowWebhookModal(false)}
          onWebhookChange={fetchWebhooks}
        />
      )}
    </div>
  );
}

// Componente do Modal de Webhooks
const WebhookModal = ({ webhooks, onClose, onWebhookChange }) => {
  const [newWebhook, setNewWebhook] = useState({ name: '', url: '', description: '' });
  const [isAdding, setIsAdding] = useState(false);

  const addWebhook = async () => {
    if (!newWebhook.name || !newWebhook.url) {
      alert('Nome e URL são obrigatórios');
      return;
    }

    try {
      await axios.post(`${BACKEND_URL}/api/webhooks`, newWebhook);
      setNewWebhook({ name: '', url: '', description: '' });
      setIsAdding(false);
      onWebhookChange();
      alert('Webhook adicionado com sucesso!');
    } catch (error) {
      console.error('Failed to add webhook:', error);
      alert('Erro ao adicionar webhook');
    }
  };

  const deleteWebhook = async (webhookId) => {
    if (!confirm('Tem certeza que deseja excluir este webhook?')) return;

    try {
      await axios.delete(`${BACKEND_URL}/api/webhooks/${webhookId}`);
      onWebhookChange();
      alert('Webhook excluído com sucesso!');
    } catch (error) {
      console.error('Failed to delete webhook:', error);
      alert('Erro ao excluir webhook');
    }
  };

  return (
    <div className="webhook-modal-overlay">
      <div className="webhook-modal">
        <div className="webhook-modal-header">
          <h3>🔗 Gerenciar Webhooks</h3>
          <button onClick={onClose} className="close-modal">❌</button>
        </div>

        <div className="webhook-modal-content">
          <div className="webhooks-list">
            {webhooks.map(webhook => (
              <div key={webhook.id} className="webhook-item">
                <div className="webhook-info">
                  <h4>{webhook.name}</h4>
                  <p className="webhook-url">{webhook.url}</p>
                  <p className="webhook-description">{webhook.description}</p>
                </div>
                <button
                  onClick={() => deleteWebhook(webhook.id)}
                  className="delete-webhook"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>

          {isAdding ? (
            <div className="add-webhook-form">
              <input
                type="text"
                placeholder="Nome do webhook"
                value={newWebhook.name}
                onChange={(e) => setNewWebhook({...newWebhook, name: e.target.value})}
                className="webhook-input"
              />
              <input
                type="url"
                placeholder="URL do webhook"
                value={newWebhook.url}
                onChange={(e) => setNewWebhook({...newWebhook, url: e.target.value})}
                className="webhook-input"
              />
              <textarea
                placeholder="Descrição (opcional)"
                value={newWebhook.description}
                onChange={(e) => setNewWebhook({...newWebhook, description: e.target.value})}
                className="webhook-textarea"
              />
              <div className="webhook-form-actions">
                <button onClick={addWebhook} className="save-webhook">💾 Salvar</button>
                <button onClick={() => setIsAdding(false)} className="cancel-webhook">❌ Cancelar</button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setIsAdding(true)}
              className="add-webhook-btn"
            >
              ➕ Adicionar Webhook
            </button>
          )}
        </div>
      </div>
    </div>
  );
};