import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function Groups() {
  const [campaigns, setCampaigns] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [availableGroups, setAvailableGroups] = useState([]);
  const [selectedGroupIds, setSelectedGroupIds] = useState([]);
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [messageText, setMessageText] = useState('');
  const [sendTime, setSendTime] = useState('');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const BAILEYS_URL = process.env.REACT_APP_BAILEYS_URL || 'http://localhost:3002';
  const INSTANCE_ID = process.env.REACT_APP_WHATSAPP_INSTANCE_ID || 'default';
  const API = `${BACKEND_URL}/api`;

  const fetchCampaigns = async () => {
    try {
      const res = await axios.get(`${API}/campaigns`);
      setCampaigns(res.data.campaigns || []);
    } catch (err) {
      console.error('Failed to load campaigns', err);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, [API]);

  const addCampaign = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      await axios.post(`${API}/campaigns`, { name: name.trim() });
      await fetchCampaigns();
      setName('');
      setShowModal(false);
    } catch (err) {
      console.error('Failed to create campaign', err);
    }
  };

  const openGroupModal = async (campaign) => {
    setSelectedCampaign(campaign);

    try {
      const res = await axios.get(`${API}/campaigns/${campaign.id}/groups`);
      setSelectedGroupIds(res.data.groups || []);
    } catch (err) {
      setSelectedGroupIds([]);
    }

    try {
      const res = await axios.get(`${BAILEYS_URL}/groups/${INSTANCE_ID}`);
      setAvailableGroups(res.data.groups || []);
    } catch (err) {
      console.error('Failed to load groups from Baileys', err);
      setAvailableGroups([]);
    }

    setShowGroupModal(true);
  };

  const toggleGroup = (groupId) => {
    setSelectedGroupIds(prev =>
      prev.includes(groupId)
        ? prev.filter(id => id !== groupId)
        : [...prev, groupId]
    );
  };

  const saveGroups = async (e) => {
    e.preventDefault();
    try {
      const groups = selectedGroupIds.map(id => ({ instance_id: INSTANCE_ID, group_id: id }));
      await axios.patch(`${API}/campaigns/${selectedCampaign.id}/groups`, { groups });
      setCampaigns(campaigns.map(c =>
        c.id === selectedCampaign.id ? { ...c, groups: selectedGroupIds } : c
      ));
      setShowGroupModal(false);
      setSelectedGroupIds([]);
    } catch (err) {
      console.error('Failed to save groups', err);
    }
  };

  const openMessageModal = (campaign) => {
    setSelectedCampaign(campaign);
    setShowMessageModal(true);
  };

  const scheduleMessage = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/campaigns/${selectedCampaign.id}/schedule`, {
        message: messageText,
        send_at: sendTime,
      });
      setShowMessageModal(false);
      setMessageText('');
      setSendTime('');
    } catch (err) {
      console.error('Failed to schedule message', err);
    }
  };

  return (
    <div className="campaigns-section">
      <div className="campaigns-header">
        <button onClick={() => setShowModal(true)}>Criar campanha</button>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Criar campanha</h3>
            <form onSubmit={addCampaign} className="campaign-form">
              <div className="form-row">
                <label>Nome</label>
                <input value={name} onChange={e => setName(e.target.value)} required />
              </div>
              <div className="modal-actions">
                <button type="button" className="card-btn" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="card-btn primary">
                  Salvar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="campaigns-grid">
        {campaigns.map(c => (
          <div key={c.id} className="campaign-card">
            <div className="campaign-info">
              <h3>{c.name}</h3>
            </div>
            <div className="card-actions">
              <button className="card-btn" onClick={() => openGroupModal(c)}>
                Selecionar grupos
              </button>
              <button className="card-btn" onClick={() => openMessageModal(c)}>
                Programar mensagens
              </button>
            </div>
          </div>
        ))}
      </div>

      {showGroupModal && selectedCampaign && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Selecionar grupos</h3>
            <form onSubmit={saveGroups} className="campaign-form">
              <div className="form-row">
                <label>Grupos disponíveis</label>
                <div className="group-list">
                  {availableGroups.map(group => (
                    <label key={group.id} className="group-item">
                      <input
                        type="checkbox"
                        checked={selectedGroupIds.includes(group.id)}
                        onChange={() => toggleGroup(group.id)}
                      />
                      {group.name || group.id}
                    </label>
                  ))}
                </div>
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="card-btn"
                  onClick={() => setShowGroupModal(false)}
                >
                  Cancelar
                </button>
                <button type="submit" className="card-btn primary">
                  Salvar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showMessageModal && selectedCampaign && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Programar mensagem</h3>
            <form onSubmit={scheduleMessage} className="campaign-form">
              <div className="form-row">
                <label>Mensagem</label>
                <textarea
                  value={messageText}
                  onChange={e => setMessageText(e.target.value)}
                  rows={3}
                  required
                />
              </div>
              <div className="form-row">
                <label>Data e horário</label>
                <input
                  type="datetime-local"
                  value={sendTime}
                  onChange={e => setSendTime(e.target.value)}
                  required
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="card-btn"
                  onClick={() => setShowMessageModal(false)}
                >
                  Cancelar
                </button>
                <button type="submit" className="card-btn primary">
                  Agendar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

