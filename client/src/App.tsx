// @ts-nocheck
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from 'axios';

function App() {
   const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');

    const sendMessage = async () => {
      const res = await axios.post('http://localhost:8002/chat', { text: input });
      setMessages([...messages, { from: 'user', text: input }, { from: 'agent', text: res.data.response }]);
      setInput('');
    };
  return (
    <div style={{ padding: 20 }}>
      <h2>EcoChain Chat</h2>
      <div style={{ border: '1px solid #ccc', padding: 10, height: 300, overflowY: 'auto' }}>
        {messages.map((m, i) => (
          <div key={i}><b>{m.from}:</b> {m.text}</div>
        ))}
      </div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={sendMessage}>Send</button>
    </div>
  )
}

export default App
