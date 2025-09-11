import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function Groups() {
  const [campaigns, setCampaigns] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [groupText, setGroupText] = useState('');
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [messageText, setMessageText] = useState('');
  const [sendTime, setSendTime] = useState('');

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const res = await axios.get(`${API}/campaigns`);
        setCampaigns(res.data.campaigns || []);
      } catch (err) {
        console.error('Failed to load campaigns', err);
      }
    };
    fetchCampaigns();
  }, [API]);

  const addCampaign = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      const res = await axios.post(`${API}/campaigns`, { name: name.trim() });
      const newCampaign = res.data;
      setCampaigns([...campaigns, newCampaign]);
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
      const groups = res.data.groups || [];
      setGroupText(groups.map(g => g.group_id).join('\n'));
    } catch (err) {
      setGroupText('');
    }
    setShowGroupModal(true);
  };

  const saveGroups = async (e) => {
    e.preventDefault();
    try {
      const groups = groupText
        .split(/\n|,/)
        .map(g => g.trim())
        .filter(Boolean)
        .map(g => ({ group_id: g }));
      await axios.post(`${API}/campaigns/${selectedCampaign.id}/groups`, { groups });
      setCampaigns(campaigns.map(c =>
        c.id === selectedCampaign.id ? { ...c, groups: groups.map(g => g.group_id) } : c
      ));
      setShowGroupModal(false);
      setGroupText('');
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
      await axios.post(`${API}/campaigns/${selectedCampaign.id}/messages`, {
        schedule_type: 'once',
        weekday: null,
        send_time: sendTime,
        message: messageText,
        media_type: null,
        media_data: null,
      });
      setCampaigns(campaigns.map(c =>
        c.id === selectedCampaign.id
          ? { ...c, messages: [...(c.messages || []), { message: messageText, send_time: sendTime }] }
          : c
      ));
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
                <label>IDs dos grupos (um por linha)</label>
                <textarea
                  value={groupText}
                  onChange={e => setGroupText(e.target.value)}
                  rows={4}
                />
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
                <label>Horário</label>
                <input
                  type="time"
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

