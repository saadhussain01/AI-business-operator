import { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar.jsx'
import Header from './components/Header.jsx'
import TaskInput from './components/TaskInput.jsx'
import AgentPipeline from './components/AgentPipeline.jsx'
import ResultPanel from './components/ResultPanel.jsx'
import HistoryPanel from './components/HistoryPanel.jsx'
import SettingsModal from './components/SettingsModal.jsx'
import { createTask, pollTask, getHealth } from './utils/api.js'

const AGENT_STEPS = ['planner', 'research', 'analysis', 'code', 'content', 'memory']

const defaultSettings = {
  provider: 'gemini',
  geminiApiKey: '',
  anthropicApiKey: '',
  model: 'gemini-2.0-flash',
}

export default function App() {
  const [settings, setSettings] = useState(() => {
    try { return { ...defaultSettings, ...JSON.parse(localStorage.getItem('aibo_settings') || '{}') } }
    catch { return defaultSettings }
  })
  const [showSettings, setShowSettings] = useState(false)
  const [task, setTask]           = useState('')
  const [mode, setMode]           = useState('auto')
  const [status, setStatus]       = useState('idle') // idle | running | completed | failed
  const [activeAgent, setActiveAgent] = useState(-1)
  const [doneAgents, setDoneAgents]   = useState([])
  const [result, setResult]       = useState(null)
  const [error, setError]         = useState(null)
  const [history, setHistory]     = useState(() => {
    try { return JSON.parse(localStorage.getItem('aibo_history') || '[]') }
    catch { return [] }
  })
  const [serverOnline, setServerOnline] = useState(null)
  const [activeTab, setActiveTab] = useState('report')
  const [taskCount, setTaskCount] = useState(0)

  // Check server health on mount
  useEffect(() => {
    getHealth()
      .then(d => setServerOnline(!!d))
      .catch(() => setServerOnline(false))
  }, [])

  const saveSettings = useCallback((s) => {
    setSettings(s)
    localStorage.setItem('aibo_settings', JSON.stringify(s))
    setShowSettings(false)
  }, [])

  const simulateAgentProgress = useCallback((taskId, stopFn) => {
    let step = 0
    const advance = setInterval(() => {
      if (step < AGENT_STEPS.length) {
        setActiveAgent(step)
        setDoneAgents(prev => step > 0 ? [...prev, AGENT_STEPS[step - 1]] : prev)
        step++
      }
    }, 1800)
    return advance
  }, [])

  const runTask = useCallback(async () => {
    if (!task.trim()) return
    const apiKey = settings.provider === 'gemini' ? settings.geminiApiKey : settings.anthropicApiKey
    if (!apiKey) { setShowSettings(true); return }

    setStatus('running')
    setResult(null)
    setError(null)
    setActiveAgent(0)
    setDoneAgents([])
    setActiveTab('report')

    try {
      const { task_id } = await createTask({
        task: task.trim(),
        mode,
        provider: settings.provider,
        gemini_api_key: settings.provider === 'gemini' ? settings.geminiApiKey : undefined,
        anthropic_api_key: settings.provider === 'anthropic' ? settings.anthropicApiKey : undefined,
        model: settings.model,
      })

      const animInterval = simulateAgentProgress(task_id)

      const stop = pollTask(task_id, (data) => {
        if (data.status === 'completed') {
          clearInterval(animInterval)
          setActiveAgent(-1)
          setDoneAgents([...AGENT_STEPS])
          setResult(data)
          setStatus('completed')
          setTaskCount(c => c + 1)
          const entry = { id: task_id, task: task.trim(), time: data.elapsed_time, ts: new Date().toISOString() }
          setHistory(h => {
            const next = [entry, ...h].slice(0, 20)
            localStorage.setItem('aibo_history', JSON.stringify(next))
            return next
          })
          stop()
        } else if (data.status === 'failed') {
          clearInterval(animInterval)
          setActiveAgent(-1)
          setDoneAgents([])
          setError(data.error || 'Pipeline failed')
          setStatus('failed')
          stop()
        }
      })
    } catch (e) {
      setError(e.message)
      setStatus('failed')
      setActiveAgent(-1)
    }
  }, [task, mode, settings, simulateAgentProgress])

  const loadFromHistory = (entry) => {
    setTask(entry.task)
    setResult(null)
    setStatus('idle')
    setDoneAgents([])
    setActiveAgent(-1)
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar
        history={history}
        onSelectHistory={loadFromHistory}
        onClearHistory={() => { setHistory([]); localStorage.removeItem('aibo_history') }}
        taskCount={taskCount}
        serverOnline={serverOnline}
        settings={settings}
        onOpenSettings={() => setShowSettings(true)}
      />

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg)' }}>
        <Header
          status={status}
          taskCount={taskCount}
          serverOnline={serverOnline}
          onOpenSettings={() => setShowSettings(true)}
        />

        <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem' }}>
          <TaskInput
            task={task}
            setTask={setTask}
            mode={mode}
            setMode={setMode}
            onRun={runTask}
            status={status}
            hasKey={!!(settings.provider === 'gemini' ? settings.geminiApiKey : settings.anthropicApiKey)}
          />

          <AgentPipeline
            activeAgent={activeAgent}
            doneAgents={doneAgents}
            status={status}
          />

          {error && (
            <div style={{
              margin: '1rem 0', padding: '1rem 1.25rem',
              background: 'rgba(244,63,94,0.08)', border: '1px solid rgba(244,63,94,0.25)',
              borderRadius: 'var(--radius)', color: '#f87171', fontSize: '0.85rem'
            }}>
              <strong>Pipeline error:</strong> {error}
            </div>
          )}

          {(result || status === 'running') && (
            <ResultPanel
              result={result}
              status={status}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
            />
          )}
        </div>
      </main>

      {history.length > 0 && (
        <HistoryPanel
          history={history}
          onSelect={loadFromHistory}
          onClear={() => { setHistory([]); localStorage.removeItem('aibo_history') }}
        />
      )}

      {showSettings && (
        <SettingsModal
          settings={settings}
          onSave={saveSettings}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  )
}
