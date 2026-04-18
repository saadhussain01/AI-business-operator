import { Clock, Trash2 } from 'lucide-react'

export default function HistoryPanel({ history, onSelect, onClear }) {
  if (!history.length) return null

  return (
    <aside style={{
      width: 220, flexShrink: 0,
      background: 'var(--bg2)',
      borderLeft: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column',
      overflow: 'hidden',
    }}>
      <div style={{
        padding: '0.875rem 1rem',
        borderBottom: '1px solid var(--border)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.72rem', fontWeight: 600, color: 'var(--txt2)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
          <Clock size={11} /> History
        </div>
        <button onClick={onClear} style={{
          background: 'none', border: 'none', color: 'var(--txt3)', cursor: 'pointer', padding: 2,
        }}
          onMouseEnter={e => e.currentTarget.style.color = 'var(--danger)'}
          onMouseLeave={e => e.currentTarget.style.color = 'var(--txt3)'}
          title="Clear history"
        >
          <Trash2 size={12} />
        </button>
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '0.5rem' }}>
        {history.map((entry) => (
          <button key={entry.id} onClick={() => onSelect(entry)} style={{
            width: '100%', textAlign: 'left', padding: '8px 10px', marginBottom: 4,
            background: 'transparent', border: '1px solid transparent',
            borderRadius: 7, cursor: 'pointer', transition: 'all 0.12s',
          }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg3)'; e.currentTarget.style.borderColor = 'var(--border)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = 'transparent' }}
          >
            <div style={{
              fontSize: '0.74rem', color: 'var(--txt)',
              whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
              marginBottom: 3,
            }}>
              {entry.task}
            </div>
            <div style={{ display: 'flex', gap: 8, fontSize: '0.66rem', color: 'var(--txt3)' }}>
              <span>{new Date(entry.ts).toLocaleDateString()}</span>
              {entry.time && <span>{entry.time}s</span>}
            </div>
          </button>
        ))}
      </div>
    </aside>
  )
}
