import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import FlowEditor from './components/FlowEditor';
import FlowList from './components/FlowList';
import MessagesCenter from './components/MessagesCenter';
import WhatsAppInstances from './components/WhatsAppInstances';
import Groups from './components/Groups';
import DashboardStats from './components/DashboardStats';
import ContactsList from './components/ContactsList';

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

// Navigation Component
const Navigation = ({ currentView, onViewChange }) => {
  return (
    <nav className="main-navigation">
      <div className="nav-items">
        <button 
          className={`nav-item ${currentView === 'dashboard' ? 'active' : ''}`}
          onClick={() => onViewChange('dashboard')}
        >
          <span className="nav-icon">📊</span>
          <span>Dashboard</span>
        </button>
        <button
          className={`nav-item ${currentView === 'flows' ? 'active' : ''}`}
          onClick={() => onViewChange('flows')}
        >
          <span className="nav-icon">🎯</span>
          <span>Fluxos</span>
        </button>
        <button
          className={`nav-item ${currentView === 'groups' ? 'active' : ''}`}
          onClick={() => onViewChange('groups')}
        >
          <span className="nav-icon">👥</span>
          <span>Grupos</span>
        </button>
        <button
          className={`nav-item ${currentView === 'contacts' ? 'active' : ''}`}
          onClick={() => onViewChange('contacts')}
        >
          <span className="nav-icon">👥</span>
          <span>Contatos</span>
        </button>
        <button 
          className={`nav-item ${currentView === 'messages' ? 'active' : ''}`}
          onClick={() => onViewChange('messages')}
        >
          <span className="nav-icon">💬</span>
          <span>Mensagens</span>
        </button>
        <button 
          className={`nav-item ${currentView === 'instances' ? 'active' : ''}`}
          onClick={() => onViewChange('instances')}
        >
          <span className="nav-icon">📱</span>
          <span>Instâncias</span>
        </button>
      </div>
    </nav>
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


// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [showFlowEditor, setShowFlowEditor] = useState(false);
  const [editingFlow, setEditingFlow] = useState(null);

  const handleCreateFlow = () => {
    setEditingFlow(null);
    setShowFlowEditor(true);
  };

  const handleEditFlow = (flow) => {
    setEditingFlow(flow);
    setShowFlowEditor(true);
  };

  const handleCloseFlowEditor = () => {
    setShowFlowEditor(false);
    setEditingFlow(null);
  };

  const handleSaveFlow = (flowData) => {
    console.log('Flow saved:', flowData);
    // Here we would save to backend
    setShowFlowEditor(false);
    setEditingFlow(null);
  };

  if (showFlowEditor) {
    return (
      <FlowEditor
        flowId={editingFlow?.id}
        onSave={handleSaveFlow}
        onClose={handleCloseFlowEditor}
      />
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 WhatsFlow</h1>
          <p>Sistema de Automação para WhatsApp</p>
        </div>
      </header>

      <Navigation currentView={currentView} onViewChange={setCurrentView} />

      <main className="app-main">
        <div className="container">
          {currentView === 'dashboard' && (
            <>
              <WhatsAppConnection />
              
              <section className="dashboard-section">
                <h2>📊 Dashboard</h2>
                <DashboardStats />
              </section>

              <section className="contacts-section">
                <ContactsList />
              </section>
            </>
          )}

          {currentView === 'flows' && (
            <FlowList
              onCreateFlow={handleCreateFlow}
              onEditFlow={handleEditFlow}
            />
          )}

          {currentView === 'groups' && (
            <Groups />
          )}

          {currentView === 'contacts' && (
            <section className="contacts-section">
              <h2>👥 Gerenciamento de Contatos</h2>
              <ContactsList />
            </section>
          )}

          {currentView === 'messages' && (
            <MessagesCenter />
          )}

          {currentView === 'instances' && (
            <WhatsAppInstances />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;