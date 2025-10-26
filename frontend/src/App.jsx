import React, { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

function useAutoScroll(dep) {
  const ref = useRef(null)
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight
  }, [dep])
  return ref
}

export default function App() {
  // Placeholder dummy data at the start
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hallo! Wie kann ich helfen?' },
    { role: 'user', content: 'Erzähl mir einen Witz.' },
    { role: 'assistant', content: 'Warum können Skelette so schlecht lügen? Weil man sie durchschaut.' },
  ])
  const [input, setInput] = useState('')

  const scrollRef = useAutoScroll(messages)

  const sendMessage = () => {
    const text = input.trim()
    if (!text) return
    setInput('')
    // Append user message
    setMessages(m => [...m, { role: 'user', content: text }])
    // Dummy assistant reply after short delay
    setTimeout(() => {
      setMessages(m => [...m, { role: 'assistant', content: `Du sagtest: "${text}"` }])
    }, 500)
  }

  return (
    <div className="bg-gray-100 h-screen">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-3xl mx-auto py-3 text-center font-semibold">ChatGPT Clone</div>
      </header>

      {/* Chat layout */}
      <div className="max-w-3xl mx-auto h-[calc(100vh-56px)] flex flex-col">
        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence initial={false}>
            {messages.map((m, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.18 }}
                className={`w-full flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`${m.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'} rounded-xl px-4 py-3 max-w-[70%] whitespace-pre-wrap`}>{m.content}</div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Input bar */}
        <div className="border-t bg-white p-3">
          <div className="flex">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Nachricht eingeben..."
              className="flex-grow p-3 rounded-xl border border-gray-300 focus:outline-none"
            />
            <button onClick={sendMessage} className="ml-2 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-xl">Send</button>
          </div>
        </div>
      </div>
    </div>
  )
}

