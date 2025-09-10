import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Form component for creating/editing campaigns
function CampaignForm({ initialData, onSave, onCancel }) {
  const [name, setName] = useState(initialData?.name || '');
  const [recurrence, setRecurrence] = useState(initialData?.recurrence || 'daily');
  const [time, setTime] = useState(initialData?.time || '');
  const [day, setDay] = useState(initialData?.day || 'monday');
  const [message, setMessage] = useState(initialData?.message || '');
  const [media, setMedia] = useState(null);
  const [instances, setInstances] = useState([]);
  const [instanceId, setInstanceId] = useState(initialData?.instance_id || '');
  const [groups, setGroups] = useState([]);
  const [selectedGroups, setSelectedGroups] = useState(initialData?.groups || []);

  useEffect(() => {
    const fetchInstances = async () => {
      try {
        const res = await axios.get(`${API}/whatsapp/instances`);
        setInstances(res.data);
        const defaultId = initialData?.instance_id || res.data[0]?.id;
        if (defaultId) {
          setInstanceId(defaultId);
        }
      } catch (err) {
        console.error('Erro ao buscar instâncias', err);
      }
    };
    fetchInstances();
  }, [initialData]);

  useEffect(() => {
    const fetchGroups = async () => {
      if (!instanceId) return;
      try {
        const res = await axios.get(`${API}/groups/${instanceId}`);
        setGroups(res.data || []);
      } catch (err) {
        console.error('Erro ao buscar grupos', err);
      }
    };
    fetchGroups();
  }, [instanceId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', name);
    formData.append('recurrence', recurrence);
    formData.append('time', time);
    if (recurrence === 'weekly') {
      formData.append('day', day);
    }
    formData.append('instance_id', instanceId);
    formData.append('groups', JSON.stringify(selectedGroups));
    formData.append('message', message);
    if (media) {
      formData.append('media', media);
    }

    try {
      if (initialData?.id) {
        await axios.put(`${API}/campaigns/${initialData.id}`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else {
        await axios.post(`${API}/campaigns`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }
      onSave();
    } catch (err) {
      console.error('Erro ao salvar campanha', err);
      alert('Erro ao salvar campanha');
    }
  };

  const toggleGroup = (groupId) => {
    setSelectedGroups(prev =>
      prev.includes(groupId) ? prev.filter(id => id !== groupId) : [...prev, groupId]
    );
  };

  return (
    <form className="campaign-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label>Nome da Campanha</label>
        <input value={name} onChange={e => setName(e.target.value)} required />
      </div>
      <div className="form-row">
        <label>Instância</label>
        <select value={instanceId} onChange={e => setInstanceId(e.target.value)} required>
          <option value="">Selecione...</option>
          {instances.map(inst => (
            <option key={inst.id} value={inst.id}>{inst.name}</option>
          ))}
        </select>
      </div>
      <div className="form-row">
        <label>Recorrência</label>
        <select value={recurrence} onChange={e => setRecurrence(e.target.value)}>
          <option value="daily">Diária</option>
          <option value="weekly">Semanal</option>
        </select>
      </div>
      {recurrence === 'weekly' && (
        <div className="form-row">
          <label>Dia da Semana</label>
          <select value={day} onChange={e => setDay(e.target.value)}>
            <option value="monday">Segunda</option>
            <option value="tuesday">Terça</option>
            <option value="wednesday">Quarta</option>
            <option value="thursday">Quinta</option>
            <option value="friday">Sexta</option>
            <option value="saturday">Sábado</option>
            <option value="sunday">Domingo</option>
          </select>
        </div>
      )}
      <div className="form-row">
        <label>Horário</label>
        <input type="time" value={time} onChange={e => setTime(e.target.value)} required />
      </div>
      <div className="form-row">
        <label>Grupos</label>
        <div className="groups-list">
          {groups.map(g => (
            <label key={g.id} className="group-item">
              <input
                type="checkbox"
                checked={selectedGroups.includes(g.id)}
                onChange={() => toggleGroup(g.id)}
              />
              {g.subject || g.name || g.id}
            </label>
          ))}
        </div>
      </div>
      <div className="form-row">
        <label>Mensagem</label>
        <textarea value={message} onChange={e => setMessage(e.target.value)} />
      </div>
      <div className="form-row">
        <label>Mídia</label>
        <input type="file" onChange={e => setMedia(e.target.files[0])} />
      </div>
      <div className="form-actions">
        <button type="button" onClick={onCancel}>Cancelar</button>
        <button type="submit">Salvar</button>
      </div>
    </form>
  );
}

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);

  const fetchCampaigns = async () => {
    try {
      const res = await axios.get(`${API}/campaigns`);
      setCampaigns(res.data || []);
    } catch (err) {
      console.error('Erro ao buscar campanhas', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const handleSave = () => {
    setShowForm(false);
    setEditing(null);
    fetchCampaigns();
  };

  if (loading) {
    return <div className="loading">Carregando campanhas...</div>;
  }

  return (
    <div className="campaigns-section">
      <div className="campaigns-header">
        <h2>📢 Campanhas</h2>
        <button onClick={() => { setEditing(null); setShowForm(true); }}>➕ Nova Campanha</button>
      </div>

      {showForm && (
        <CampaignForm
          initialData={editing}
          onSave={handleSave}
          onCancel={() => { setShowForm(false); setEditing(null); }}
        />
      )}

      <div className="campaigns-list">
        {campaigns.map(c => (
          <div key={c.id} className="campaign-card">
            <div className="campaign-info">
              <h3>{c.name}</h3>
              {c.recurrence && (
                <div className="campaign-schedule">
                  {c.recurrence === 'daily' && `Diária às ${c.time}`}
                  {c.recurrence === 'weekly' && `Toda ${c.day} às ${c.time}`}
                </div>
              )}
            </div>
            <button onClick={() => { setEditing(c); setShowForm(true); }}>Editar</button>
          </div>
        ))}
      </div>
    </div>
  );
}

