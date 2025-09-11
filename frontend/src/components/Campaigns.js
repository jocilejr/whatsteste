import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Calendar } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Modal for creating a campaign with just the name
function CreateCampaignModal({ onClose, onCreated }) {
  const [name, setName] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/campaigns`, { name });
      onCreated();
    } catch (err) {
      console.error('Erro ao criar campanha', err);
      alert('Erro ao criar campanha');
    }
  };

  return (
    <div className="modal">
      <h3>Criar campanha</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <label>Nome</label>
          <input value={name} onChange={e => setName(e.target.value)} required />
        </div>
        <div className="modal-actions">
          <button type="button" className="card-btn" onClick={onClose}>Cancelar</button>
          <button type="submit" className="card-btn primary">Salvar</button>
        </div>
      </form>
    </div>
  );
}

// Modal for selecting groups
function GroupModal({ campaign, onClose, onSaved }) {
  const [instances, setInstances] = useState([]);
  const [instanceId, setInstanceId] = useState('');
  const [groups, setGroups] = useState([]);
  const [selected, setSelected] = useState(campaign.groups || []);

  useEffect(() => {
    const loadInstances = async () => {
      try {
        const res = await axios.get(`${API}/whatsapp/instances`);
        setInstances(res.data || []);
      } catch (err) {
        console.error('Erro ao buscar instâncias', err);
      }
    };
    loadInstances();
  }, []);

  useEffect(() => {
    if (!instanceId) return;
    const loadGroups = async () => {
      try {
        const res = await axios.get(`${API}/groups/${instanceId}`);
        setGroups(res.data || []);
      } catch (err) {
        console.error('Erro ao buscar grupos', err);
      }
    };
    loadGroups();
  }, [instanceId]);

  const toggle = (id) => {
    setSelected(prev =>
      prev.includes(id) ? prev.filter(g => g !== id) : [...prev, id]
    );
  };

  const save = async () => {
    try {
      await axios.put(`${API}/campaigns/${campaign.id}`, { groups: selected });
      onSaved();
    } catch (err) {
      console.error('Erro ao salvar grupos', err);
      alert('Erro ao salvar grupos');
    }
  };

  return (
    <div className="modal">
      <h3>Selecionar grupos</h3>
      <div className="form-row">
        <label>Instância</label>
        <select value={instanceId} onChange={e => setInstanceId(e.target.value)}>
          <option value="">Selecione...</option>
          {instances.map(inst => (
            <option key={inst.id} value={inst.id}>{inst.name}</option>
          ))}
        </select>
      </div>
      {groups.length > 0 && (
        <div className="form-row groups-list">
          {groups.map(g => (
            <label key={g.id} className="group-item">
              <input
                type="checkbox"
                checked={selected.includes(g.id)}
                onChange={() => toggle(g.id)}
              />
              {g.subject || g.name || g.id}
            </label>
          ))}
        </div>
      )}
      <div className="modal-actions">
        <button type="button" className="card-btn" onClick={onClose}>Cancelar</button>
        <button type="button" className="card-btn primary" onClick={save}>Salvar</button>
      </div>
    </div>
  );
}

// Modal for scheduling messages
function ScheduleModal({ campaign, onClose }) {
  const dayLabels = {
    monday: 'Segunda',
    tuesday: 'Terça',
    wednesday: 'Quarta',
    thursday: 'Quinta',
    friday: 'Sexta',
    saturday: 'Sábado',
    sunday: 'Domingo'
  };

  const [messagesByDay, setMessagesByDay] = useState({
    monday: [], tuesday: [], wednesday: [], thursday: [], friday: [], saturday: [], sunday: []
  });
  const [text, setText] = useState('');
  const [day, setDay] = useState('monday');

  const loadMessages = async () => {
    try {
      const res = await axios.get(`${API}/campaigns/${campaign.id}/messages`);
      const byDay = {
        monday: [], tuesday: [], wednesday: [], thursday: [], friday: [], saturday: [], sunday: []
      };
      (res.data.messages || []).forEach(m => {
        if (m.next_run) {
          const d = new Date(m.next_run);
          const key = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday'][d.getDay()];
          byDay[key].push(m);
        }
      });
      setMessagesByDay(byDay);
    } catch (err) {
      console.error('Erro ao carregar agenda', err);
    }
  };

  useEffect(() => {
    loadMessages();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const add = async () => {
    if (!text.trim()) return;
    try {
      await axios.post(`${API}/campaigns/${campaign.id}/messages`, { content: text, weekday: day });
      setText('');
      await loadMessages();
    } catch (err) {
      console.error('Erro ao agendar mensagem', err);
      alert('Erro ao agendar mensagem');
    }
  };

  return (
    <div className="modal schedule-modal">
      <h3>Agenda de mensagens</h3>
      <div className="schedule-grid">
        {Object.keys(dayLabels).map(k => (
          <div key={k} className="schedule-day">
            <h4>{dayLabels[k]}</h4>
            <ul>
              {messagesByDay[k].map(m => (
                <li key={m.id}>{m.content}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="form-row">
        <label>Dia</label>
        <select value={day} onChange={e => setDay(e.target.value)}>
          {Object.keys(dayLabels).map(k => (
            <option key={k} value={k}>{dayLabels[k]}</option>
          ))}
        </select>
      </div>
      <div className="form-row">
        <label>Mensagem</label>
        <input value={text} onChange={e => setText(e.target.value)} />
      </div>
      <div className="modal-actions">
        <button type="button" className="card-btn" onClick={onClose}>Fechar</button>
        <button type="button" className="card-btn primary" onClick={add}>Adicionar</button>
      </div>
    </div>
  );
}

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [groupModal, setGroupModal] = useState(null);
  const [scheduleModal, setScheduleModal] = useState(null);

  const fetchCampaigns = async () => {
    try {
      const res = await axios.get(`${API}/campaigns`);
      const sorted = (res.data || []).sort((a, b) => a.name.localeCompare(b.name));
      setCampaigns(sorted);
    } catch (err) {
      console.error('Erro ao buscar campanhas', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);

  if (loading) {
    return <div className="loading">Carregando campanhas...</div>;
  }

  return (
    <div className="campaigns-section">
      <div className="campaigns-header">
        <h2>📢 Campanhas</h2>
        <button onClick={() => setShowCreate(true)}>Criar campanha</button>
      </div>

      {showCreate && (
        <div className="modal-overlay">
          <CreateCampaignModal
            onClose={() => setShowCreate(false)}
            onCreated={() => { setShowCreate(false); fetchCampaigns(); }}
          />
        </div>
      )}

      {groupModal && (
        <div className="modal-overlay">
          <GroupModal
            campaign={groupModal}
            onClose={() => setGroupModal(null)}
            onSaved={() => { setGroupModal(null); fetchCampaigns(); }}
          />
        </div>
      )}

      {scheduleModal && (
        <div className="modal-overlay">
          <ScheduleModal
            campaign={scheduleModal}
            onClose={() => setScheduleModal(null)}
          />
        </div>
      )}

      <div className="campaigns-grid">
        {campaigns.map(c => (
          <div key={c.id} className="campaign-card">
            <div className="campaign-info">
              <h3>{c.name}</h3>
            </div>
            <div className="card-actions">
              <button className="card-btn" onClick={() => setGroupModal(c)}>
                <Users size={16} /> Selecionar grupos
              </button>
              <button className="card-btn" onClick={() => setScheduleModal(c)}>
                <Calendar size={16} /> Programar mensagens
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

