import { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, Zap } from 'lucide-react'
import { chat } from '../services/api'
import toast from 'react-hot-toast'

const WELCOME = "Hello! I'm BuildWise AI, your construction planning assistant. Ask me about material estimation, BOQ, structural design, cost planning, and more."

const Chat = () => {
  const [messages, setMessages] = useState([{ text: WELCOME, sender: 'ai' }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const messagesEndRef = useRef(null)
  const abortRef = useRef(null)

  useEffect(() => { loadHistory() }, [])
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const loadHistory = async () => {
    try {
      const response = await chat.getHistory()
      const history = response.data.history
        .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
        .flatMap(h => [
          { text: h.message, sender: 'user' },
          { text: h.reply, sender: 'ai' }
        ])
      if (history.length > 0) {
        setMessages([{ text: WELCOME, sender: 'ai' }, ...history])
      }
    } catch {
      // silent fail
    }
  }

  const handleSend = async () => {
    if (!input.trim() || loading || streaming) return

    const userText = input.trim()
    setMessages(prev => [...prev, { text: userText, sender: 'user' }])
    setInput('')

    // Add empty AI message placeholder for streaming
    setMessages(prev => [...prev, { text: '', sender: 'ai', streaming: true }])
    setStreaming(true)
    setLoading(true)

    const token = localStorage.getItem('token')

    try {
      const controller = new AbortController()
      abortRef.current = controller

      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userText }),
        signal: controller.signal
      })

      if (!res.ok) {
        // Fallback to non-streaming
        throw new Error('stream_failed')
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let accumulated = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data = JSON.parse(line.slice(6))
            if (data.token) {
              accumulated += data.token
              // Update the last message in place
              setMessages(prev => {
                const updated = [...prev]
                updated[updated.length - 1] = { text: accumulated, sender: 'ai', streaming: true }
                return updated
              })
            }
            if (data.done) {
              setMessages(prev => {
                const updated = [...prev]
                updated[updated.length - 1] = { text: accumulated, sender: 'ai' }
                return updated
              })
            }
          } catch { /* skip malformed */ }
        }
      }

    } catch (err) {
      if (err.message === 'stream_failed' || err.name !== 'AbortError') {
        // Fallback to regular endpoint
        try {
          const response = await chat.sendMessage(userText)
          const reply = response.data.reply
          setMessages(prev => {
            const updated = [...prev]
            updated[updated.length - 1] = { text: reply, sender: 'ai' }
            return updated
          })
        } catch {
          toast.error('Failed to send message')
          setMessages(prev => prev.slice(0, -1)) // remove empty placeholder
        }
      }
    } finally {
      setStreaming(false)
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col bg-white rounded-xl shadow-lg">
      <div className="p-6 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">AI Assistant</h1>
          <p className="text-gray-600 text-sm">Construction planning — materials, costs, structure</p>
        </div>
        <div className="flex items-center gap-1 text-xs text-green-600 bg-green-50 px-3 py-1 rounded-full">
          <Zap size={12} />
          <span>Instant calculations</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'ai' && (
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="text-white" size={20} />
              </div>
            )}
            <div
              className={`max-w-2xl p-4 rounded-lg ${
                msg.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="whitespace-pre-wrap font-mono text-sm leading-relaxed">
                {msg.text}
                {msg.streaming && <span className="inline-block w-2 h-4 bg-gray-500 ml-1 animate-pulse" />}
              </p>
            </div>
            {msg.sender === 'user' && (
              <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                <User className="text-gray-600" size={20} />
              </div>
            )}
          </div>
        ))}

        {loading && !streaming && (
          <div className="flex gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Bot className="text-white" size={20} />
            </div>
            <div className="bg-gray-100 p-4 rounded-lg">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-6 border-t border-gray-200">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="e.g. How much steel for 1500 sqft? What is BOQ?"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading || streaming}
          />
          <button
            onClick={handleSend}
            disabled={loading || streaming || !input.trim()}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Calculation questions (steel, cement, sand, bricks, labour) get instant answers. Other questions use AI.
        </p>
      </div>
    </div>
  )
}

export default Chat
