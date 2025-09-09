import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// QR Code Component
const QRCode = ({ value }) => {
  if (!value) return null;
  
  return (
    <div className="qr-container">
      <div className="qr-code">
        <img 
          src={`https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodeURIComponent(value)}`}
          alt="QR Code"
          className="qr-image"
        />
      </div>
    </div>
  );
};

// WhatsApp Connection Component
const WhatsAppConnection = () => {
  const [qrCode, setQrCode] = useState(null);
  const [status, setStatus] = useState('disconnected');
  const [loading, setLoading] = useState(false);
  const [connectedUser, setConnectedUser] = useState(null);
  const [isDemoMode, setIsDemoMode] = useState(false);

  const checkStatus = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/status`);
      setStatus(response.data.connected ? 'connected' : 'disconnected');
      setConnectedUser(response.data.user);
      setIsDemoMode(response.data.demo || false);
      return response.data.connected;
    } catch (error) {
      console.error('Status check failed:', error);
      setStatus('error');
      return false;
    }
  };

  const fetchQR = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/qr`);
      if (response.data.qr) {
        setQrCode(response.data.qr);
      } else {
        setQrCode(null);
      }
    } catch (error) {
      console.error('QR fetch failed:', error);
    }
  };

  const simulateConnection = async () => {
    try {
      const response = await axios.post('http://localhost:3001/demo/connect');
      if (response.data.success) {
        await checkStatus();
      }
    } catch (error) {
      console.error('Demo connection failed:', error);
    }
  };

  const startPolling = () => {
    const interval = setInterval(async () => {
      const isConnected = await checkStatus();
      if (isConnected) {
        setQrCode(null);
        clearInterval(interval);
      } else {
        await fetchQR();
      }
    }, 3000);

    return interval;
  };

  useEffect(() => {
    checkStatus();
    const interval = startPolling();

    return () => clearInterval(interval);
  }, []);

  const handleConnect = async () => {
    setLoading(true);
    await checkStatus();
    if (status !== 'connected') {
      startPolling();
    }
    setLoading(false);
  };

  return (
    <div className="whatsapp-connection">
      <div className="connection-header">
        <h2>🔗 Conexão WhatsApp</h2>
        <div className={`status-indicator ${status}`}>
          <div className="status-dot"></div>
          <span className="status-text">
            {status === 'connected' ? 'Conectado' : 
             status === 'disconnected' ? 'Desconectado' : 'Erro'}
            {isDemoMode && ' (Demo)'}
          </span>
        </div>
      </div>

      {isDemoMode && (
        <div className="demo-badge">
          🚧 <strong>Modo Demonstração</strong> - Simulando funcionalidade WhatsApp para testes
        </div>
      )}

      {status === 'connected' && connectedUser && (
        <div className="connected-info">
          <div className="success-badge">
            ✅ WhatsApp conectado com sucesso!
          </div>
          <div className="user-info">
            <strong>Usuário:</strong> {connectedUser.name || connectedUser.id}
          </div>
        </div>
      )}

      {status === 'disconnected' && (
        <div className="qr-section">
          <div className="warning-badge">
            ⚠️ WhatsApp não está conectado. {isDemoMode ? 'Clique para simular conexão ou ' : ''}Escaneie o QR code para conectar.
          </div>
          
          {qrCode && (
            <div className="qr-display">
              <h3>Escaneie este QR Code com o WhatsApp:</h3>
              <QRCode value={qrCode} />
              <p className="qr-instructions">
                Abra o WhatsApp → Configurações → Aparelhos conectados → Conectar um aparelho
              </p>
            </div>
          )}
          
          <div className="button-group">
            <button 
              className="connect-button"
              onClick={handleConnect}
              disabled={loading}
            >
              {loading ? 'Conectando...' : 'Conectar WhatsApp'}
            </button>
            
            {isDemoMode && (
              <button 
                className="demo-button"
                onClick={simulateConnection}
                disabled={loading}
              >
                🎯 Simular Conexão (Demo)
              </button>
            )}
          </div>
        </div>
      )}

      {status === 'error' && (
        <div className="error-badge">
          ❌ Erro de conexão. Verifique se o serviço WhatsApp está em execução.
        </div>
      )}
    </div>
  );
};

// Dashboard Stats Component
const DashboardStats = () => {
  const [stats, setStats] = useState({
    new_contacts_today: 0,
    active_conversations: 0,
    messages_today: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/dashboard/stats`);
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-stats">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{stats.new_contacts_today}</h3>
            <p>Novos contatos hoje</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">💬</div>
          <div className="stat-content">
            <h3>{stats.active_conversations}</h3>
            <p>Conversas ativas</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📨</div>
          <div className="stat-content">
            <h3>{stats.messages_today}</h3>
            <p>Mensagens hoje</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Contacts List Component
const ContactsList = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        const response = await axios.get(`${API}/contacts`);
        setContacts(response.data);
      } catch (error) {
        console.error('Failed to fetch contacts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchContacts();
  }, []);

  if (loading) {
    return <div className="loading">Carregando contatos...</div>;
  }

  return (
    <div className="contacts-list">
      <h3>📞 Contatos Recentes</h3>
      {contacts.length === 0 ? (
        <div className="empty-state">
          <p>Nenhum contato encontrado ainda.</p>
          <p>Os contatos aparecerão aqui quando começarem a enviar mensagens.</p>
        </div>
      ) : (
        <div className="contacts-grid">
          {contacts.slice(0, 6).map(contact => (
            <div key={contact.id} className="contact-card">
              <div className="contact-avatar">
                {contact.name.charAt(0).toUpperCase()}
              </div>
              <div className="contact-info">
                <h4>{contact.name}</h4>
                <p>{contact.phone_number}</p>
                <div className="contact-tags">
                  {contact.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 WhatsFlow</h1>
          <p>Sistema de Automação para WhatsApp</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          <WhatsAppConnection />
          
          <section className="dashboard-section">
            <h2>📊 Dashboard</h2>
            <DashboardStats />
          </section>

          <section className="contacts-section">
            <ContactsList />
          </section>

          <section className="features-preview">
            <h2>🚀 Em Breve</h2>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">🎯</div>
                <h3>Editor de Funis</h3>
                <p>Crie fluxos de automação arrastando e soltando componentes</p>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">🏷️</div>
                <h3>Sistema de Etiquetas</h3>
                <p>Organize e segmente seus contatos com etiquetas personalizadas</p>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">📱</div>
                <h3>Mídia Avançada</h3>
                <p>Envie áudios, imagens e vídeos através dos seus fluxos</p>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;