import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Download, FileText, BarChart2, Search, Code2, ListChecks, Clock, Globe } from 'lucide-react'

const TABS = [
  { id: 'report',   label: 'Report',   icon: FileText },
  { id: 'analysis', label: 'Analysis', icon: BarChart2 },
  { id: 'research', label: 'Research', icon: Search },
  { id: 'charts',   label: 'Charts',   icon: BarChart2 },
  { id: 'log',      label: 'Agent Log',icon: ListChecks },
]

export default function ResultPanel({ result, status, activeTab, setActiveTab }) {
  const running = status === 'running'

  return (
    <div style={{
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
      background: 'var(--bg2)',
      marginTop: '0.25rem',
    }}>
      {/* Tab bar */}
      <div style={{
        display: 'flex', alignItems: 'center',
        borderBottom: '1px solid var(--border)',
        background: 'var(--bg3)',
        padding: '0 0.5rem',
        gap: 2,
      }}>
        {TABS.map(t => {
          const Icon = t.icon
          const active = activeTab === t.id
          return (
            <button key={t.id} onClick={() => setActiveTab(t.id)} style={{
              display: 'flex', alignItems: 'center', gap: 5,
              padding: '9px 12px', fontSize: '0.75rem', fontWeight: active ? 600 : 400,
              color: active ? 'var(--txt)' : 'var(--txt2)',
              background: 'none', border: 'none',
              borderBottom: `2px solid ${active ? 'var(--accent)' : 'transparent'}`,
              marginBottom: -1, transition: 'all 0.15s', cursor: 'pointer',
            }}
              onMouseEnter={e => { if (!active) e.currentTarget.style.color = 'var(--txt)' }}
              onMouseLeave={e => { if (!active) e.currentTarget.style.color = 'var(--txt2)' }}
            >
              <Icon size={12} />
              {t.label}
            </button>
          )
        })}

        {/* Meta info */}
        {result && (
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12, paddingRight: 8 }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.7rem', color: 'var(--txt3)' }}>
              <Clock size={10} />{result.elapsed_time}s
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.7rem', color: 'var(--txt3)' }}>
              <Globe size={10} />{result.sources_count} sources
            </span>
            {result.report_path && (
              <a href={`/api/reports/download/${result.report_path.split('/').pop()}`}
                style={{
                  display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.7rem',
                  color: 'var(--accent)', textDecoration: 'none',
                  padding: '3px 8px', border: '1px solid rgba(108,99,255,0.3)',
                  borderRadius: 5,
                }}>
                <Download size={10} /> Download
              </a>
            )}
          </div>
        )}
      </div>

      {/* Tab content */}
      <div style={{ padding: '1.25rem 1.5rem', minHeight: 280, maxHeight: 560, overflow: 'auto' }}>
        {running && !result && <LoadingSkeleton />}

        {activeTab === 'report' && (
          result?.final_report
            ? <div className="prose"><ReactMarkdown>{result.final_report}</ReactMarkdown></div>
            : !running && <Empty icon="📄" msg="Report will appear here after the pipeline completes" />
        )}

        {activeTab === 'analysis' && (
          result?.analysis_output
            ? <div className="prose"><ReactMarkdown>{result.analysis_output}</ReactMarkdown></div>
            : !running && <Empty icon="📊" msg="Analysis will appear here" />
        )}

        {activeTab === 'research' && (
          result?.research_output
            ? <div className="prose"><ReactMarkdown>{result.research_output}</ReactMarkdown></div>
            : !running && <Empty icon="🔍" msg="Research findings will appear here" />
        )}

        {activeTab === 'charts' && (
          result?.chart_paths?.length > 0
            ? <ChartsTab paths={result.chart_paths} />
            : !running && <Empty icon="📈" msg="Charts will appear here once the Code Agent runs" />
        )}

        {activeTab === 'log' && (
          result?.agent_log?.length > 0
            ? <LogTab log={result.agent_log} errors={result.errors} />
            : !running && <Empty icon="📋" msg="Agent activity log will appear here" />
        )}
      </div>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {[100, 80, 90, 60, 85, 70].map((w, i) => (
        <div key={i} style={{
          height: 14, borderRadius: 4, background: 'var(--bg4)',
          width: `${w}%`, animation: `pulse 1.5s ${i * 0.1}s infinite`,
        }} />
      ))}
      <style>{`@keyframes pulse { 0%,100%{opacity:0.4} 50%{opacity:0.8} }`}</style>
    </div>
  )
}

function Empty({ icon, msg }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      minHeight: 200, gap: 10, color: 'var(--txt3)',
    }}>
      <span style={{ fontSize: '2rem' }}>{icon}</span>
      <p style={{ fontSize: '0.82rem' }}>{msg}</p>
    </div>
  )
}

function ChartsTab({ paths }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
      {paths.map((p, i) => {
        const filename = p.split('/').pop()
        return (
          <div key={i} style={{
            border: '1px solid var(--border)', borderRadius: 'var(--radius)',
            overflow: 'hidden', background: 'var(--bg3)',
          }}>
            <img
              src={`/api/reports/download/${filename}`}
              alt={`Chart ${i + 1}`}
              style={{ width: '100%', display: 'block' }}
              onError={e => { e.target.parentElement.style.display = 'none' }}
            />
          </div>
        )
      })}
    </div>
  )
}

function LogTab({ log, errors }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {log.map((entry, i) => (
        <div key={i} style={{
          display: 'flex', gap: 10, alignItems: 'flex-start',
          padding: '7px 10px', borderRadius: 6, background: 'var(--bg3)',
          border: '1px solid var(--border)',
        }}>
          <span style={{ fontSize: '0.67rem', color: 'var(--txt3)', fontFamily: 'var(--mono)', flexShrink: 0, paddingTop: 1 }}>
            {entry.timestamp?.slice(11, 19) || '--:--:--'}
          </span>
          <span style={{
            fontSize: '0.68rem', fontWeight: 600, color: 'var(--accent)',
            flexShrink: 0, paddingTop: 1, minWidth: 110,
          }}>
            {entry.agent}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--txt2)', lineHeight: 1.5 }}>
            {entry.output_preview}…
          </span>
        </div>
      ))}
      {errors?.length > 0 && (
        <div style={{ marginTop: 8, padding: '10px', background: 'rgba(244,63,94,0.07)', border: '1px solid rgba(244,63,94,0.2)', borderRadius: 6 }}>
          <div style={{ fontSize: '0.75rem', color: '#f87171', fontWeight: 600, marginBottom: 6 }}>Errors</div>
          {errors.map((e, i) => (
            <pre key={i} style={{ fontSize: '0.72rem', color: '#fca5a5', whiteSpace: 'pre-wrap', fontFamily: 'var(--mono)' }}>{e}</pre>
          ))}
        </div>
      )}
    </div>
  )
}
