import { useEffect, useRef } from 'react'
import { Play, Loader } from 'lucide-react'

const MODES = [
  { value: 'auto',       label: 'Auto' },
  { value: 'research',   label: 'Research' },
  { value: 'analysis',   label: 'Analysis' },
  { value: 'content',    label: 'Content' },
  { value: 'report',     label: 'Report' },
]

export default function TaskInput({ task, setTask, mode, setMode, onRun, status, hasKey }) {
  const taRef = useRef(null)

  // Listen for quick-task events from Sidebar
  useEffect(() => {
    const h = (e) => { setTask(e.detail); taRef.current?.focus() }
    window.addEventListener('aibo:quicktask', h)
    return () => window.removeEventListener('aibo:quicktask', h)
  }, [setTask])

  const running = status === 'running'

  const handleKey = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey) && !running) onRun()
  }

  return (
    <div style={{ marginBottom: '1.25rem' }}>
      {/* Mode pills */}
      <div style={{ display: 'flex', gap: 6, marginBottom: '0.75rem', flexWrap: 'wrap' }}>
        {MODES.map(m => (
          <button key={m.value} onClick={() => setMode(m.value)} style={{
            padding: '4px 12px', borderRadius: 20, fontSize: '0.75rem', fontWeight: 500,
            border: '1px solid',
            borderColor: mode === m.value ? 'var(--accent)' : 'var(--border)',
            background: mode === m.value ? 'rgba(108,99,255,0.12)' : 'transparent',
            color: mode === m.value ? 'var(--accent)' : 'var(--txt2)',
            transition: 'all 0.15s',
          }}>{m.label}</button>
        ))}
      </div>

      {/* Textarea + button */}
      <div style={{
        border: '1px solid var(--border2)',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
        transition: 'border-color 0.2s',
        background: 'var(--bg2)',
      }}
        onFocusCapture={e => e.currentTarget.style.borderColor = 'rgba(108,99,255,0.5)'}
        onBlurCapture={e => e.currentTarget.style.borderColor = 'var(--border2)'}
      >
        <textarea
          ref={taRef}
          value={task}
          onChange={e => setTask(e.target.value)}
          onKeyDown={handleKey}
          rows={3}
          placeholder="Describe your business task… e.g. Analyze Tesla's EV market competitors and generate a strategic report"
          style={{
            width: '100%', resize: 'none', border: 'none', outline: 'none',
            padding: '0.875rem 1rem', fontSize: '0.9rem', lineHeight: 1.65,
            background: 'transparent', color: 'var(--txt)',
            fontFamily: 'var(--sans)',
          }}
        />
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '0.5rem 0.75rem',
          borderTop: '1px solid var(--border)',
          background: 'var(--bg3)',
        }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--txt3)' }}>
            {running ? 'Pipeline running…' : 'Ctrl+Enter to run · Choose a mode above'}
          </span>
          <button
            onClick={onRun}
            disabled={running || !task.trim()}
            style={{
              display: 'flex', alignItems: 'center', gap: 7,
              padding: '7px 18px', borderRadius: 8, fontSize: '0.82rem', fontWeight: 600,
              border: 'none',
              background: running || !task.trim()
                ? 'var(--bg4)'
                : 'linear-gradient(135deg,#6c63ff,#4f46e5)',
              color: running || !task.trim() ? 'var(--txt3)' : '#fff',
              cursor: running || !task.trim() ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s', fontFamily: 'var(--display)',
              letterSpacing: '0.01em',
            }}
            onMouseEnter={e => { if (!running && task.trim()) e.currentTarget.style.opacity = '0.85' }}
            onMouseLeave={e => { e.currentTarget.style.opacity = '1' }}
          >
            {running
              ? <><Loader size={13} style={{ animation: 'spin 1s linear infinite' }} /> Running</>
              : <><Play size={13} fill="currentColor" /> Run Agents</>
            }
          </button>
        </div>
      </div>

      {!hasKey && (
        <div style={{
          marginTop: '0.5rem', padding: '8px 12px',
          background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.2)',
          borderRadius: 8, fontSize: '0.75rem', color: '#fbbf24',
        }}>
          ⚠ No API key set — click <strong>Settings</strong> to add your free Gemini key
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
