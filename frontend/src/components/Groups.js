import React, { useState } from 'react';

export default function Groups() {
  const [campaigns, setCampaigns] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');

  const addCampaign = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    setCampaigns([...campaigns, { id: Date.now(), name: name.trim() }]);
    setName('');
    setShowModal(false);
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
              <button className="card-btn" onClick={() => alert('Selecionar grupos')}>
                Selecionar grupos
              </button>
              <button className="card-btn" onClick={() => alert('Programar mensagens')}>
                Programar mensagens
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

