import { Settings, Clock, Zap, Database, ExternalLink } from 'lucide-react'

export default function Sidebar({ history, onSelectHistory, onClearHistory, taskCount, serverOnline, settings, onOpenSettings }) {
  return (
    <aside style={{
      width: 240, flexShrink: 0,
      background: 'var(--bg2)',
      borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* Logo */}
      <div style={{ padding: '1.25rem 1.25rem 1rem', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'linear-gradient(135deg,#6c63ff,#4f46e5)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexShrink: 0,
          }}>
            <Zap size={16} color="#fff" />
          </div>
          <div>
            <div style={{ fontFamily: 'var(--display)', fontSize: '0.95rem', fontWeight: 700, color: 'var(--txt)', letterSpacing: '-0.3px' }}>AI Operator</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--txt3)', marginTop: -1 }}>Business Intelligence</div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div style={{ padding: '0.875rem 1.25rem', borderBottom: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: 8 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--txt3)' }}>Server</span>
          <span style={{
            fontSize: '0.7rem', fontWeight: 600, padding: '2px 7px', borderRadius: 20,
            background: serverOnline ? 'rgba(74,222,128,0.1)' : 'rgba(244,63,94,0.1)',
            color: serverOnline ? '#4ade80' : '#f87171',
            border: `1px solid ${serverOnline ? 'rgba(74,222,128,0.2)' : 'rgba(244,63,94,0.2)'}`,
          }}>
            {serverOnline === null ? '...' : serverOnline ? 'Online' : 'Offline'}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--txt3)' }}>Model</span>
          <span style={{ fontSize: '0.7rem', color: 'var(--accent)', fontFamily: 'var(--mono)' }}>
            {settings.model?.replace('gemini-', 'g-') || 'not set'}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--txt3)' }}>Tasks run</span>
          <span style={{ fontSize: '0.72rem', color: 'var(--txt)', fontFamily: 'var(--mono)', fontWeight: 600 }}>{taskCount}</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--txt3)' }}>API cost</span>
          <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#4ade80' }}>FREE</span>
        </div>
      </div>

      {/* Quick tasks */}
      <div style={{ padding: '0.875rem 1.25rem', borderBottom: '1px solid var(--border)' }}>
        <div style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--txt3)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 8 }}>Quick tasks</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {QUICK_TASKS.map((qt) => (
            <QuickTaskBtn key={qt.label} {...qt} />
          ))}
        </div>
      </div>

      {/* Links */}
      <div style={{ padding: '0.875rem 1.25rem', borderBottom: '1px solid var(--border)' }}>
        <div style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--txt3)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 8 }}>Resources</div>
        <a href="https://aistudio.google.com/apikey" target="_blank" rel="noreferrer"
          style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--accent)', padding: '4px 0' }}>
          <ExternalLink size={11} /> Get free Gemini API key
        </a>
        <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer"
          style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--txt2)', padding: '4px 0' }}>
          <ExternalLink size={11} /> API docs (FastAPI)
        </a>
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Settings btn */}
      <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--border)' }}>
        <button onClick={onOpenSettings} style={{
          width: '100%', padding: '8px 12px',
          background: 'var(--bg3)', border: '1px solid var(--border2)',
          borderRadius: 'var(--radius)', color: 'var(--txt2)',
          display: 'flex', alignItems: 'center', gap: 8,
          fontSize: '0.8rem', transition: 'all 0.15s',
        }}
          onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg4)'; e.currentTarget.style.color = 'var(--txt)' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg3)'; e.currentTarget.style.color = 'var(--txt2)' }}
        >
          <Settings size={13} />
          API Keys & Settings
        </button>
      </div>
    </aside>
  )
}

function QuickTaskBtn({ label, icon, task }) {
  return (
    <button
      onClick={() => {
        // Emit to parent via custom event since we're in sidebar
        window.dispatchEvent(new CustomEvent('aibo:quicktask', { detail: task }))
      }}
      style={{
        width: '100%', textAlign: 'left', padding: '6px 8px',
        background: 'transparent', border: '1px solid transparent',
        borderRadius: 6, color: 'var(--txt2)', fontSize: '0.75rem',
        display: 'flex', alignItems: 'center', gap: 6, transition: 'all 0.12s',
      }}
      onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg3)'; e.currentTarget.style.color = 'var(--txt)'; e.currentTarget.style.borderColor = 'var(--border)' }}
      onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--txt2)'; e.currentTarget.style.borderColor = 'transparent' }}
    >
      <span>{icon}</span>
      <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{label}</span>
    </button>
  )
}

const QUICK_TASKS = [
  { icon: '🚗', label: 'Tesla EV competitors', task: 'Analyze competitors of Tesla in the EV market and generate a business report' },
  { icon: '🏥', label: 'Healthcare AI startups', task: 'Research top AI startups in healthcare and identify investment opportunities' },
  { icon: '🤖', label: 'LLM market analysis', task: 'Compare Google Gemini, Anthropic Claude, and Meta AI in the LLM market' },
  { icon: '📱', label: 'LinkedIn posts (SaaS)', task: 'Generate 5 LinkedIn marketing posts for an AI-powered SaaS analytics product' },
  { icon: '🛒', label: 'E-commerce trends 2025', task: 'Analyze e-commerce market trends and predict key growth sectors for 2025' },
]
