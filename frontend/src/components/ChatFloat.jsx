import { useState } from 'react'
import { postChat } from '../api/client'

export default function ChatFloat({ paperId }) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const send = async () => {
    if (!input.trim() || loading) return
    const userMsg = { role: 'user', content: input.trim() }
    setMessages((m) => [...m, userMsg])
    setInput('')
    setLoading(true)
    try {
      const res = await postChat(paperId, [...messages, userMsg].map((m) => ({ role: m.role, content: m.content })))
      setMessages((m) => [...m, { role: 'assistant', content: res.reply || '' }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: `Error: ${e.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-float">
      <button type="button" className="chat-toggle" onClick={() => setOpen(!open)} aria-label="Toggle chat">
        💬
      </button>
      {open && (
        <div className="chat-panel">
          <div className="chat-messages">
            {messages.length === 0 && <p className="chat-placeholder">Ask anything about this paper (English).</p>}
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg ${m.role}`}>
                <strong>{m.role === 'user' ? 'You' : 'AI'}:</strong> {m.content}
              </div>
            ))}
          </div>
          <div className="chat-input-row">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
              placeholder="Type a question..."
              disabled={loading}
            />
            <button type="button" onClick={send} disabled={loading}>
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
