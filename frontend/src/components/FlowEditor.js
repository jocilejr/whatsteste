import React, { useState, useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  ConnectionLineType,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';

// Custom Node Components
const MessageNode = ({ data, isConnectable }) => {
  return (
    <div className="flow-node message-node">
      <div className="node-header">
        <span className="node-icon">💬</span>
        <span className="node-title">Mensagem</span>
      </div>
      <div className="node-content">
        <textarea
          placeholder="Digite sua mensagem..."
          value={data.message || ''}
          onChange={(e) => data.onChange?.(e.target.value)}
          className="message-input"
        />
        <div className="delay-section">
          <label>⏱️ Delay (segundos):</label>
          <input
            type="number"
            min="0"
            max="300"
            placeholder="0"
            value={data.delay || ''}
            onChange={(e) => data.onDelayChange?.(e.target.value)}
            className="delay-input"
          />
        </div>
      </div>
      <div className="node-handles">
        <div className="target-handle">📥</div>
        <div className="source-handle">📤</div>
      </div>
    </div>
  );
};

const ConditionNode = ({ data, isConnectable }) => {
  return (
    <div className="flow-node condition-node">
      <div className="node-header">
        <span className="node-icon">🔀</span>
        <span className="node-title">Condição</span>
      </div>
      <div className="node-content">
        <input
          type="text"
          placeholder="Palavra-chave ou condição..."
          value={data.condition || ''}
          onChange={(e) => data.onChange?.(e.target.value)}
          className="condition-input"
        />
        <div className="condition-options">
          <label>
            <input
              type="radio"
              name={`condition-type-${data.id}`}
              value="contains"
              checked={data.conditionType === 'contains'}
              onChange={(e) => data.onConditionTypeChange?.(e.target.value)}
            />
            Contém texto
          </label>
          <label>
            <input
              type="radio"
              name={`condition-type-${data.id}`}
              value="equals"
              checked={data.conditionType === 'equals'}
              onChange={(e) => data.onConditionTypeChange?.(e.target.value)}
            />
            Igual a
          </label>
        </div>
      </div>
      <div className="node-handles">
        <div className="target-handle">📥</div>
        <div className="source-handle success">✅ SIM</div>
        <div className="source-handle error">❌ NÃO</div>
      </div>
    </div>
  );
};

const TagNode = ({ data, isConnectable }) => {
  return (
    <div className="flow-node tag-node">
      <div className="node-header">
        <span className="node-icon">🏷️</span>
        <span className="node-title">Etiqueta</span>
      </div>
      <div className="node-content">
        <input
          type="text"
          placeholder="Nome da etiqueta..."
          value={data.tag || ''}
          onChange={(e) => data.onChange?.(e.target.value)}
          className="tag-input"
        />
        <select 
          value={data.action || 'add'}
          onChange={(e) => data.onActionChange?.(e.target.value)}
          className="tag-action"
        >
          <option value="add">➕ Adicionar</option>
          <option value="remove">➖ Remover</option>
        </select>
      </div>
      <div className="node-handles">
        <div className="target-handle">📥</div>
        <div className="source-handle">📤</div>
      </div>
    </div>
  );
};

const MediaNode = ({ data, isConnectable }) => {
  return (
    <div className="flow-node media-node">
      <div className="node-header">
        <span className="node-icon">📁</span>
        <span className="node-title">Mídia</span>
      </div>
      <div className="node-content">
        <select 
          value={data.mediaType || 'audio'}
          onChange={(e) => data.onTypeChange?.(e.target.value)}
          className="media-type"
        >
          <option value="audio">🎵 Áudio</option>
          <option value="image">🖼️ Imagem</option>
          <option value="video">🎥 Vídeo</option>
        </select>
        <input
          type="file"
          accept="audio/*,image/*,video/*"
          onChange={(e) => data.onFileChange?.(e.target.files[0])}
          className="media-file"
        />
        <div className="delay-section">
          <label>⏱️ Delay (segundos):</label>
          <input
            type="number"
            min="0"
            max="300"
            placeholder="0"
            value={data.delay || ''}
            onChange={(e) => data.onDelayChange?.(e.target.value)}
            className="delay-input"
          />
        </div>
      </div>
      <div className="node-handles">
        <div className="target-handle">📥</div>
        <div className="source-handle">📤</div>
      </div>
    </div>
  );
};

const StartNode = ({ data, isConnectable }) => {
  return (
    <div className="flow-node start-node">
      <div className="node-header">
        <span className="node-icon">🚀</span>
        <span className="node-title">Início</span>
      </div>
      <div className="node-content">
        <p>Ponto de início do fluxo</p>
      </div>
      <div className="node-handles">
        <div className="source-handle"></div>
      </div>
    </div>
  );
};

// Node types
const nodeTypes = {
  messageNode: MessageNode,
  conditionNode: ConditionNode,
  tagNode: TagNode,
  mediaNode: MediaNode,
  startNode: StartNode,
};

// Initial nodes and edges
const initialNodes = [
  {
    id: 'start',
    type: 'startNode',
    position: { x: 250, y: 50 },
    data: { label: 'Início' },
  },
];

const initialEdges = [];

export default function FlowEditor({ flowId, onSave, onClose }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [flowName, setFlowName] = useState('Novo Fluxo');
  const [selectedNodeType, setSelectedNodeType] = useState('messageNode');

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const addNode = useCallback((type) => {
    const id = `${type}_${Date.now()}`;
    const newNode = {
      id,
      type,
      position: { x: Math.random() * 400 + 100, y: Math.random() * 400 + 100 },
      data: { 
        label: `Novo ${type}`,
        onChange: (value) => updateNodeData(id, 'message', value),
        onActionChange: (value) => updateNodeData(id, 'action', value),
        onTypeChange: (value) => updateNodeData(id, 'mediaType', value),
        onFileChange: (file) => updateNodeData(id, 'file', file),
      },
    };
    setNodes((nodes) => [...nodes, newNode]);
  }, [setNodes]);

  const updateNodeData = useCallback((nodeId, key, value) => {
    setNodes((nodes) =>
      nodes.map((node) => {
        if (node.id === nodeId) {
          return {
            ...node,
            data: {
              ...node.data,
              [key]: value,
            },
          };
        }
        return node;
      })
    );
  }, [setNodes]);

  const handleSave = async () => {
    const flowData = {
      name: flowName,
      nodes: nodes,
      edges: edges,
      created_at: new Date().toISOString(),
    };
    
    try {
      // Here we would save to backend
      console.log('Saving flow:', flowData);
      onSave?.(flowData);
      alert('Fluxo salvo com sucesso!');
    } catch (error) {
      console.error('Error saving flow:', error);
      alert('Erro ao salvar fluxo');
    }
  };

  return (
    <div className="flow-editor">
      <div className="flow-editor-header">
        <div className="flow-info">
          <input
            type="text"
            value={flowName}
            onChange={(e) => setFlowName(e.target.value)}
            className="flow-name-input"
            placeholder="Nome do fluxo"
          />
        </div>
        <div className="flow-actions">
          <button onClick={handleSave} className="save-button">
            💾 Salvar
          </button>
          <button onClick={onClose} className="close-button">
            ❌ Fechar
          </button>
        </div>
      </div>

      <div className="flow-editor-content">
        <div className="node-palette">
          <h3>Componentes</h3>
          <div className="palette-items">
            <button
              onClick={() => addNode('messageNode')}
              className="palette-item"
            >
              <span className="palette-icon">💬</span>
              <span>Mensagem</span>
            </button>
            <button
              onClick={() => addNode('conditionNode')}
              className="palette-item"
            >
              <span className="palette-icon">🔀</span>
              <span>Condição</span>
            </button>
            <button
              onClick={() => addNode('tagNode')}
              className="palette-item"
            >
              <span className="palette-icon">🏷️</span>
              <span>Etiqueta</span>
            </button>
            <button
              onClick={() => addNode('mediaNode')}
              className="palette-item"
            >
              <span className="palette-icon">📁</span>
              <span>Mídia</span>
            </button>
          </div>
        </div>

        <div className="flow-canvas">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            connectionLineType={ConnectionLineType.SmoothStep}
            fitView
          >
            <Controls />
            <MiniMap />
            <Background variant="dots" gap={12} size={1} />
            <Panel position="top-right">
              <div className="flow-stats">
                <div>Nós: {nodes.length}</div>
                <div>Conexões: {edges.length}</div>
              </div>
            </Panel>
          </ReactFlow>
        </div>
      </div>
    </div>
  );
}