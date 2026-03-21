import React, { useState, useRef, useEffect } from 'react';
import './index.css';

type NodeEvent = {
  node: string;
  state: any;
};

type Message = {
  id: string;
  role: 'user' | 'agent';
  content: string; 
  steps: NodeEvent[];
};

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputTitle, setInputTitle] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputTitle.trim() || isProcessing) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: inputTitle, steps: [] };
    const agentMsg: Message = { id: (Date.now() + 1).toString(), role: 'agent', content: '', steps: [] };

    setMessages((prev) => [...prev, userMsg, agentMsg]);
    setInputTitle('');
    setIsProcessing(true);

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg.content }),
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ') && line.trim() !== 'data:') {
            try {
              const dataStr = line.slice(6);
              const data = JSON.parse(dataStr);
              
              setMessages((prev) => {
                const newMsgs = [...prev];
                const lastIdx = newMsgs.length - 1;
                
                if (data.node === 'synthesize' && data.state.final_answer) {
                  newMsgs[lastIdx].content = data.state.final_answer;
                } else if (data.node) {
                  newMsgs[lastIdx].steps.push(data);
                }
                
                return newMsgs;
              });
            } catch (err) {
              console.error('JSON parse error:', err, line);
            }
          }
        }
      }
    } catch (error) {
      console.error('Fetch error:', error);
      setMessages((prev) => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1].content = "Error: Failed to connect to agent backend.";
        return newMsgs;
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const renderState = (node: string, state: any) => {
    if (node === 'extract' && state.country) {
      return `Identified: ${state.country} (${state.fields?.join(', ') || 'N/A'})`;
    }
    if (node === 'api' && state.api_response) {
      return state.api_response.flags ? 'Data retrieved successfully.' : state.api_response.name?.common || 'Data fetched.';
    }
    if (node === 'process') {
      return `Processed details for rendering.`;
    }
    return JSON.stringify(state).slice(0, 100) + '...';
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div style={{ fontSize: '24px' }}>🌍</div>
        <h1>Country AI Agent</h1>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '2rem' }}>
            Ask me anything about a country!<br/><small>e.g., "What is the capital and population of Brazil?"</small>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`msg-row ${msg.role}`}>
            {msg.role === 'user' ? (
              <div className="msg-bubble user">{msg.content}</div>
            ) : (
              <div className="msg-bubble-container agent">
                {msg.steps.map((step, idx) => (
                  <div key={idx} className="agent-step">
                    <div className="agent-step-title">
                      {idx === msg.steps.length - 1 && isProcessing && !msg.content ? <span className="loader"></span> : '✓'}
                      [{step.node}]
                    </div>
                    <div className="agent-step-data">
                      {renderState(step.node, step.state)}
                    </div>
                  </div>
                ))}
                
                {msg.content && (
                  <div className="final-answer fadeIn">
                    {msg.content}
                  </div>
                )}
                
                {(!msg.content && msg.steps.length === 0 && isProcessing) && (
                  <div className="agent-step">
                    <div className="agent-step-title"><span className="loader"></span> INITIALIZING...</div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <form className="input-area" onSubmit={handleSubmit}>
        <input 
          type="text" 
          placeholder="Ask a question about a country..." 
          value={inputTitle}
          onChange={(e) => setInputTitle(e.target.value)}
          disabled={isProcessing}
        />
        <button type="submit" disabled={!inputTitle.trim() || isProcessing}>
          Send
        </button>
      </form>
    </div>
  );
}

export default App;
