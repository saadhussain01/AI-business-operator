const AGENTS = [
  { id: 'planner',  icon: '🗺',  label: 'Planner',  desc: 'Decomposes task' },
  { id: 'research', icon: '🔍', label: 'Research', desc: 'Web search' },
  { id: 'analysis', icon: '📊', label: 'Analysis', desc: 'Finds patterns' },
  { id: 'code',     icon: '⚙',  label: 'Code',     desc: 'Generates charts' },
  { id: 'content',  icon: '✍',  label: 'Content',  desc: 'Writes report' },
  { id: 'memory',   icon: '🧠', label: 'Memory',   desc: 'Stores knowledge' },
]

export default function AgentPipeline({ activeAgent, doneAgents, status }) {
  return (
    <div style={{ marginBottom: '1.25rem' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(6, 1fr)',
        gap: 8,
      }}>
        {AGENTS.map((agent, idx) => {
          const isActive = activeAgent === idx
          const isDone   = doneAgents.includes(agent.id)
          const isPending = !isActive && !isDone

          return (
            <div key={agent.id} style={{
              padding: '10px 8px', borderRadius: 'var(--radius)', textAlign: 'center',
              border: '1px solid',
              borderColor: isActive ? 'rgba(108,99,255,0.5)'
                         : isDone   ? 'rgba(74,222,128,0.35)'
                         : 'var(--border)',
              background: isActive ? 'rgba(108,99,255,0.07)'
                        : isDone   ? 'rgba(74,222,128,0.05)'
                        : 'var(--bg2)',
              transition: 'all 0.35s ease',
              position: 'relative', overflow: 'hidden',
            }}>
              {isActive && (
                <div style={{
                  position: 'absolute', top: 0, left: '-100%', width: '100%', height: '100%',
                  background: 'linear-gradient(90deg, transparent, rgba(108,99,255,0.08), transparent)',
                  animation: 'shimmer 1.4s infinite',
                }} />
              )}
              <div style={{ fontSize: '1.25rem', marginBottom: 4, lineHeight: 1 }}>{agent.icon}</div>
              <div style={{
                fontSize: '0.72rem', fontWeight: 600,
                color: isActive ? '#a78bfa' : isDone ? '#4ade80' : 'var(--txt2)',
                transition: 'color 0.3s',
              }}>{agent.label}</div>
              <div style={{ fontSize: '0.63rem', color: 'var(--txt3)', marginTop: 2 }}>{agent.desc}</div>
              <div style={{ marginTop: 5, fontSize: '0.63rem', fontFamily: 'var(--mono)',
                color: isActive ? '#f59e0b' : isDone ? '#4ade80' : 'var(--txt3)',
                transition: 'color 0.3s',
              }}>
                {isActive ? '● working' : isDone ? '✓ done' : '○ idle'}
              </div>
            </div>
          )
        })}
      </div>

      {/* Progress bar */}
      <div style={{
        marginTop: 10, height: 2, background: 'var(--bg3)', borderRadius: 2, overflow: 'hidden',
      }}>
        <div style={{
          height: '100%', borderRadius: 2,
          background: 'linear-gradient(90deg,#6c63ff,#4ade80)',
          width: `${status === 'completed' ? 100 : status === 'running' ? Math.round((doneAgents.length / 6) * 85) + 5 : 0}%`,
          transition: 'width 0.5s ease',
        }} />
      </div>

      <style>{`
        @keyframes shimmer {
          0%   { left: -100%; }
          100% { left:  100%; }
        }
      `}</style>
    </div>
  )
}
