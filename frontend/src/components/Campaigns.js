import React, { useState, useEffect } from 'react';
import axios from 'axios';

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

function ScheduleModal({ campaignId, onClose }) {
  const [type, setType] = useState('daily');
  const [day, setDay] = useState('monday');
  const [runAt, setRunAt] = useState(() => {
    const now = new Date();
    const br = now.toLocaleString('sv-SE', { timeZone: 'America/Sao_Paulo' });
    return br.slice(0, 16);
  });
  const [text, setText] = useState('');
  const [media, setMedia] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeTab, setActiveTab] = useState('monday');

  const days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday'];

  const fetchMessages = async () => {
    try {
      const res = await axios.get(`${API}/campaigns/${campaignId}/messages`);
      setMessages(res.data || []);
    } catch (err) {
      console.error('Erro ao listar mensagens', err);
    }
  };

  useEffect(() => {
    if (campaignId) {
      fetchMessages();
    }
  }, [campaignId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const form = new FormData();
    form.append('type', type);
    if (type === 'weekly') form.append('day', day);
    form.append('run_at', runAt);
    form.append('text', text);
    if (media) form.append('media', media);
    try {
      await axios.post(`${API}/campaigns/${campaignId}/messages`, form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setText('');
      setMedia(null);
      fetchMessages();
    } catch (err) {
      console.error('Erro ao salvar mensagem', err);
      alert('Erro ao salvar mensagem');
    }
  };

  const grouped = days.reduce((acc, d) => ({ ...acc, [d]: [] }), {});
  messages.forEach(m => {
    if (m.type === 'daily') {
      days.forEach(d => grouped[d].push(m));
    } else if (m.day && grouped[m.day]) {
      grouped[m.day].push(m);
    }
  });

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>Agendar mensagens</h3>
          <button className="close-modal" onClick={onClose}>✖</button>
        </div>
        <div className="modal-content">
          <form onSubmit={handleSubmit} className="schedule-form">
            <div className="form-row">
              <label>Tipo</label>
              <select value={type} onChange={e => setType(e.target.value)}>
                <option value="daily">Diário</option>
                <option value="weekly">Semanal</option>
              </select>
            </div>
            {type === 'weekly' && (
              <div className="form-row">
                <label>Dia</label>
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
              <label>Horário de execução</label>
              <input type="datetime-local" value={runAt} onChange={e => setRunAt(e.target.value)} />
            </div>
            <div className="form-row">
              <label>Conteúdo</label>
              <textarea value={text} onChange={e => setText(e.target.value)} />
            </div>
            <div className="form-row">
              <label>Mídia</label>
              <input type="file" accept="image/*,video/*,audio/*" onChange={e => setMedia(e.target.files[0])} />
            </div>
            <div className="form-actions">
              <button type="submit">Salvar</button>
            </div>
          </form>

          <div className="schedule-tabs">
            <div className="tabs-header">
              {days.map(d => (
                <button
                  key={d}
                  className={activeTab === d ? 'active' : ''}
                  onClick={() => setActiveTab(d)}
                >
                  {d}
                </button>
              ))}
            </div>
            <div className="tabs-content">
              {grouped[activeTab].length === 0 ? (
                <p>Nenhuma mensagem</p>
              ) : (
                grouped[activeTab].map((m, idx) => (
                  <div key={idx} className="message-card">
                    <strong>{m.run_at}</strong>
                    <p>{m.text}</p>
                    {m.media_url && <small>Mídia</small>}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [showSchedule, setShowSchedule] = useState(false);
  const [scheduleId, setScheduleId] = useState(null);

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

      {showSchedule && (
        <ScheduleModal
          campaignId={scheduleId}
          onClose={() => { setShowSchedule(false); setScheduleId(null); }}
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
            <div className="campaign-actions">
              <button onClick={() => { setEditing(c); setShowForm(true); }}>Editar</button>
              <button onClick={() => handleDelete(c.id)}>Excluir</button>
              <button onClick={() => { setScheduleId(c.id); setShowSchedule(true); }}>Agendar mensagens</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

