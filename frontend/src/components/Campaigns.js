import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Calendar } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Form component for creating/editing campaigns
function CampaignForm({ initialData, onSave, onCancel }) {
  // Step control
  const [step, setStep] = useState(1);

  // Basic info
  const [name, setName] = useState(initialData?.name || '');
  const [recurrence, setRecurrence] = useState(initialData?.recurrence || 'daily');
  const [time, setTime] = useState(initialData?.time || '');
  const [day, setDay] = useState(initialData?.day || 'monday');
  const [instances, setInstances] = useState([]);
  const [instanceId, setInstanceId] = useState(initialData?.instance_id || '');

  // Groups
  const [groups, setGroups] = useState([]);
  const [selectedGroups, setSelectedGroups] = useState(initialData?.groups || []);

  // Scheduled messages
  const [scheduledMessages, setScheduledMessages] = useState(initialData?.messages || []);
  const [currentMessage, setCurrentMessage] = useState('');
  const [currentMedia, setCurrentMedia] = useState(null);
  const [currentDay, setCurrentDay] = useState('monday');
  const [editingIndex, setEditingIndex] = useState(-1);

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

  const addOrUpdateMessage = () => {
    const msg = currentMessage.trim();
    if (!msg && !currentMedia) return;
    const entry = {
      day: recurrence === 'daily' ? 'daily' : currentDay,
      text: msg,
      media: currentMedia
    };
    setScheduledMessages(prev => {
      const copy = [...prev];
      if (editingIndex >= 0) {
        copy[editingIndex] = entry;
      } else {
        copy.push(entry);
      }
      return copy;
    });
    setCurrentMessage('');
    setCurrentMedia(null);
    setEditingIndex(-1);
  };

  const editMessage = (index) => {
    const msg = scheduledMessages[index];
    setCurrentMessage(msg.text);
    setCurrentMedia(null);
    setCurrentDay(msg.day);
    setEditingIndex(index);
  };

  const removeMessage = (index) => {
    setScheduledMessages(prev => prev.filter((_, i) => i !== index));
  };

  const toggleGroup = (groupId) => {
    setSelectedGroups(prev =>
      prev.includes(groupId) ? prev.filter(id => id !== groupId) : [...prev, groupId]
    );
  };

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
    formData.append(
      'messages',
      JSON.stringify(
        scheduledMessages.map((m, idx) => ({
          day: m.day,
          text: m.text,
          media: m.media ? `media_${idx}` : null
        }))
      )
    );
    scheduledMessages.forEach((m, idx) => {
      if (m.media) formData.append(`media_${idx}`, m.media);
    });

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

  const nextStep = () => setStep(s => s + 1);
  const prevStep = () => setStep(s => s - 1);

  return (
    <form className="campaign-form" onSubmit={handleSubmit}>
      {step === 1 && (
        <>
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
        </>
      )}

      {step === 2 && (
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
      )}

      {step === 3 && (
        <div className="form-row">
          {recurrence === 'weekly' && (
            <div className="form-row">
              <label>Dia</label>
              <select value={currentDay} onChange={e => setCurrentDay(e.target.value)}>
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
          <label>Mensagem</label>
          <textarea value={currentMessage} onChange={e => setCurrentMessage(e.target.value)} />
          <label>Mídia</label>
          <input
            type="file"
            accept="image/*,audio/*,video/*"
            onChange={e => setCurrentMedia(e.target.files[0])}
          />
          <button type="button" onClick={addOrUpdateMessage} className="add-message-btn">
            {editingIndex >= 0 ? 'Atualizar' : 'Adicionar'} mensagem
          </button>
          <div className="messages-preview">
            {scheduledMessages.map((m, idx) => (
              <div key={idx} className="message-card">
                <div className="message-card-header">
                  <strong>{m.day === 'daily' ? 'Todos os dias' : m.day}</strong>
                  <div className="message-card-actions">
                    <button type="button" onClick={() => editMessage(idx)}>Editar</button>
                    <button type="button" onClick={() => removeMessage(idx)}>Excluir</button>
                  </div>
                </div>
                <p>{m.text}</p>
                {m.media && <small>Mídia anexada</small>}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="form-actions">
        {step > 1 && (
          <button type="button" onClick={prevStep}>Voltar</button>
        )}
        {step < 3 && (
          <button type="button" onClick={nextStep}>Próximo</button>
        )}
        {step === 3 && (
          <>
            <button type="button" onClick={onCancel}>Cancelar</button>
            <button type="submit">Salvar</button>
          </>
        )}
      </div>
    </form>
  );
}

 codex/redesign-groups-tab-with-campaign-cards
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
 codex/redesign-groups-tab-with-campaign-cards
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
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
 codex/redesign-groups-tab-with-campaign-cards
  const [groupModal, setGroupModal] = useState(null);
  const [scheduleModal, setScheduleModal] = useState(null);

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

  const handleDelete = async (id) => {
    if (!window.confirm('Excluir campanha?')) return;
    try {
      await axios.delete(`${API}/campaigns/${id}`);
      fetchCampaigns();
    } catch (err) {
      console.error('Erro ao excluir campanha', err);
      alert('Erro ao excluir campanha');
    }
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
        <div className="modal-overlay">
          <CampaignForm
            initialData={editing}
            onSave={handleSave}
            onCancel={() => { setShowForm(false); setEditing(null); }}
          />
        </div>
      )}

 codex/redesign-groups-tab-with-campaign-cards
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
                <button className="card-btn" onClick={() => setGroupModal(c)}><Users size={16}/> Selecionar grupos</button>
                <button className="card-btn" onClick={() => setScheduleModal(c)}><Calendar size={16}/> Agendar mensagens</button>
                <button className="card-btn" onClick={() => { setEditing(c); setShowForm(true); }}>Editar</button>
                <button className="card-btn" onClick={() => handleDelete(c.id)}>Excluir</button>

              </div>
          </div>
        ))}
      </div>
    </div>
  );
}

