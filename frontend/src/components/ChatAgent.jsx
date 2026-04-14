import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import { Send, Bot, User } from 'lucide-react';

export default function ChatAgent() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const endRef = useRef(null);

  const scrollToBottom = () => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsTyping(true);

    try {
      const formData = new FormData();
      formData.append('prompt', userMsg);
      const res = await axios.post('/api/chat', formData);

      const botMsg = {
        role: 'assistant',
        content: res.data.answer,
        chart: res.data.chart,
        intent: res.data.intent
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. ' + String(err) }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-history">
        {messages.length === 0 && (
          <div style={{textAlign: 'center', marginTop: 'auto', marginBottom: 'auto', color: '#94a3b8'}}>
            <Bot size={48} style={{opacity: 0.5, marginBottom: 16}} />
            <p>Ask me anything about your dataset.<br/>Try "Show me a trend overview" or "What is the average of the numerical columns?"</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{display: 'flex', gap: 12, alignItems: 'flex-start', alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%'}}>
             {msg.role === 'assistant' && <div style={{padding: 8, background: 'rgba(59, 130, 246, 0.2)', borderRadius: 8}}><Bot size={20} color="#3b82f6" /></div>}
             <div className={`chat-message ${msg.role}`}>
                {msg.intent && <div style={{fontSize: 11, textTransform: 'uppercase', color: '#10b981', marginBottom: 4}}>{msg.intent} Route</div>}
                
                <div style={{whiteSpace: 'pre-wrap'}}>{msg.content}</div>
                
                {msg.chart && (
                  <div style={{marginTop: 12, borderRadius: 8, overflow: 'hidden', background: 'rgba(0,0,0,0.2)'}}>
                    <Plot
                      data={msg.chart.data}
                      layout={{...msg.chart.layout, autosize: true, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', font: {color: '#f8fafc'}}}
                      useResizeHandler={true}
                      style={{width: '100%', height: '300px'}}
                    />
                  </div>
                )}
             </div>
             {msg.role === 'user' && <div style={{padding: 8, background: 'rgba(139, 92, 246, 0.2)', borderRadius: 8}}><User size={20} color="#8b5cf6" /></div>}
          </div>
        ))}
        {isTyping && (
          <div style={{display: 'flex', gap: 12, alignItems: 'flex-start', alignSelf: 'flex-start'}}>
            <div style={{padding: 8, background: 'rgba(59, 130, 246, 0.2)', borderRadius: 8}}><Bot size={20} color="#3b82f6" /></div>
            <div className={`chat-message assistant`} style={{fontStyle: 'italic', color: '#94a3b8'}}>
              Analyzing...
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form className="chat-input-area" onSubmit={handleSend}>
        <input 
          type="text" 
          placeholder="Message AI Data Analyst..." 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          autoFocus
        />
        <button type="submit" className="primary" disabled={isTyping || !input.trim()} style={{padding: '8px 12px'}}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
