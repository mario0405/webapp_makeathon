import React, { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const API_BASE = 'http://localhost:8000/api'

function useAutoScroll(dep) {
  const ref = useRef(null)
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight
  }, [dep])
  return ref
}

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hallo! Bitte wähle eine Kategorie, um zu starten.' },
    { role: 'user', content: 'Zeig mir die Kategorien' },
    { role: 'assistant', content: 'Hier sind die Top-Kategorien. Wähle eine Option.' },
  ])
  const [currentOptions, setCurrentOptions] = useState([])
  const [currentPath, setCurrentPath] = useState([])
  const [selections, setSelections] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const scrollRef = useAutoScroll(messages)

  // Load top-level options initially or after reset
  const loadTop = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/top`)
      const data = await res.json()
      setCurrentOptions(data)
      setMessages(m => ([...m, { role: 'assistant', content: 'Bitte wähle eine Kategorie.' }]))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTop()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchChildren = async (name) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/children?name=${encodeURIComponent(name)}`)
      const data = await res.json()
      const children = data?.subcategories ?? []
      setCurrentOptions(children)
      if (!children.length) {
        // Leaf reached: record and reset
        const path = [...currentPath, name]
        setSelections(s => [...s, path])
        setMessages(m => ([...m, { role: 'assistant', content: `Pfad abgeschlossen: ${path.join(' > ')}. Starte oben neu.` }]))
        setCurrentPath([])
        await loadTop()
      }
    } finally {
      setLoading(false)
    }
  }

  const handleChoose = async (opt) => {
    setMessages(m => ([...m, { role: 'user', content: opt }]))
    if (!currentPath.length) {
      setCurrentPath([opt])
    } else {
      setCurrentPath(p => ([...p, opt]))
    }
    await fetchChildren(opt)
  }

  const sendMessage = async () => {
    const text = input.trim()
    if (!text) return
    setInput('')
    await handleChoose(text)
  }

  const onBack = async () => {
    if (!currentPath.length) return
    const newPath = currentPath.slice(0, -1)
    setCurrentPath(newPath)
    setMessages(m => ([...m, { role: 'assistant', content: 'Eine Ebene zurück.' }]))
    if (!newPath.length) {
      await loadTop()
    } else {
      await fetchChildren(newPath[newPath.length - 1])
    }
  }

  const onReset = async () => {
    setCurrentPath([])
    setMessages(m => ([...m, { role: 'assistant', content: 'Pfad zurückgesetzt. Bitte erneut oben wählen.' }]))
    await loadTop()
  }

  const onQuitDownload = () => {
    // Build simple text report on client
    const lines = ['Material Navigator Report', '==========================', '']
    if (!selections.length) lines.push('No selections.')
    selections.forEach((p, i) => lines.push(`${i + 1}. ${p.join(' > ')}`))
    const blob = new Blob([lines.join('\n') + '\n'], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'selection_report.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="h-screen bg-gray-100">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="max-w-3xl mx-auto py-3 text-center font-semibold">ChatGPT Clone</div>
      </header>

      {/* Chat layout */}
      <div className="max-w-3xl mx-auto h-[calc(100vh-56px)] flex flex-col">
        {/* Top toolbar */}
        <div className="flex items-center justify-between gap-2 px-4 py-2">
          <div className="text-sm text-gray-600 truncate">{currentPath.length ? `Aktueller Pfad: ${currentPath.join(' > ')}` : 'Obere Ebene'}</div>
          <div className="flex items-center gap-2">
            <button onClick={onBack} disabled={!currentPath.length} className="px-3 py-2 rounded-xl border border-gray-300 text-gray-700 disabled:opacity-40">Back</button>
            <button onClick={onReset} className="px-3 py-2 rounded-xl border border-gray-300 text-gray-700">Reset</button>
            <button onClick={onQuitDownload} className="px-3 py-2 rounded-xl bg-green-500 hover:bg-green-600 text-white">Quit & Download Report</button>
          </div>
        </div>

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

          {/* Assistant options bubble */}
          {!!currentOptions.length && (
            <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.18 }} className="w-full flex justify-start">
              <div className="bg-gray-200 text-gray-800 rounded-xl px-4 py-3 max-w-[70%]">
                <div className="mb-2 font-medium">Bitte auswählen:</div>
                <div className="flex flex-wrap gap-2">
                  {currentOptions.map((opt, i) => (
                    <button key={i} onClick={() => handleChoose(opt)} className="px-3 py-1.5 rounded-xl bg-white border border-gray-300 hover:bg-gray-50 text-gray-800">
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {loading && (
            <div className="text-sm text-gray-500">Laden…</div>
          )}
        </div>

        {/* Input bar */}
        <div className="border-t bg-white p-3">
          <div className="flex">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Nachricht eingeben oder Option tippen…"
              className="flex-grow p-3 rounded-xl border border-gray-300 focus:outline-none"
            />
            <button onClick={sendMessage} className="ml-2 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-xl">Send</button>
          </div>
        </div>
      </div>
    </div>
  )
}

