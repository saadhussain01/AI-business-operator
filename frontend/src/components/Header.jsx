import { Settings, Activity } from 'lucide-react'

export default function Header({ status, taskCount, serverOnline, onOpenSettings }) {
  const statusMap = {
    idle:      { label: 'Ready',     color: 'var(--txt3)' },
    running:   { label: 'Working…',  color: '#f59e0b' },
    completed: { label: 'Done',      color: '#4ade80' },
    failed:    { label: 'Failed',    color: '#f43f5e' },
  }
  const s = statusMap[status] || statusMap.idle

  return (
    <header style={{
      height: 52, flexShrink: 0,
      borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'center',
      padding: '0 1.5rem', gap: 12,
      background: 'var(--bg)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
        <Activity size={13} color={s.color} style={{ transition: 'color 0.3s' }} />
        <span style={{ fontSize: '0.75rem', color: s.color, fontFamily: 'var(--mono)', transition: 'color 0.3s' }}>
          {s.label}
        </span>
        {status === 'running' && (
          <span style={{ display: 'flex', gap: 3, marginLeft: 4 }}>
            {[0, 1, 2].map(i => (
              <span key={i} style={{
                width: 4, height: 4, borderRadius: '50%', background: '#f59e0b',
                animation: `bounce 1.2s ${i * 0.2}s infinite`,
              }} />
            ))}
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <span style={{ fontSize: '0.72rem', color: 'var(--txt3)' }}>
          {taskCount} task{taskCount !== 1 ? 's' : ''} run
        </span>
        <button onClick={onOpenSettings} style={{
          background: 'none', border: '1px solid var(--border)',
          borderRadius: 6, padding: '5px 8px', color: 'var(--txt2)',
          display: 'flex', alignItems: 'center', gap: 5, fontSize: '0.75rem',
          transition: 'all 0.15s',
        }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--border2)'; e.currentTarget.style.color = 'var(--txt)' }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--txt2)' }}
        >
          <Settings size={12} /> Settings
        </button>
      </div>

      <style>{`
        @keyframes bounce {
          0%,80%,100% { transform: translateY(0); opacity:0.5; }
          40% { transform: translateY(-4px); opacity:1; }
        }
      `}</style>
    </header>
  )
}
