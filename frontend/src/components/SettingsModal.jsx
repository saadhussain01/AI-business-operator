import { useState } from 'react'
import { X, Eye, EyeOff, ExternalLink, CheckCircle } from 'lucide-react'

const GEMINI_MODELS = [
  { value: 'gemini-2.0-flash',      label: 'Gemini 2.0 Flash — fastest, free (recommended)' },
  { value: 'gemini-2.0-flash-lite', label: 'Gemini 2.0 Flash Lite — lightest' },
  { value: 'gemini-1.5-flash-latest', label: 'Gemini 1.5 Flash — stable' },
  { value: 'gemini-1.5-pro-latest', label: 'Gemini 1.5 Pro — most capable free' },
]

export default function SettingsModal({ settings, onSave, onClose }) {
  const [form, setForm] = useState({ ...settings })
  const [showKey, setShowKey] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState(null)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const testConnection = async () => {
    setTesting(true)
    setTestResult(null)
    try {
      const res = await fetch('/api/health')
      const data = await res.json()
      setTestResult({ ok: true, msg: `API online — ${data.agents?.length} agents ready` })
    } catch {
      setTestResult({ ok: false, msg: 'Cannot reach API server. Is it running?' })
    }
    setTesting(false)
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 1000,
      background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div style={{
        width: 480, background: 'var(--bg2)',
        border: '1px solid var(--border2)', borderRadius: 'var(--radius-lg)',
        overflow: 'hidden', boxShadow: '0 24px 60px rgba(0,0,0,0.5)',
      }}>
        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '1rem 1.25rem', borderBottom: '1px solid var(--border)',
        }}>
          <div>
            <div style={{ fontFamily: 'var(--display)', fontSize: '1rem', fontWeight: 700, color: 'var(--txt)' }}>
              API Keys & Settings
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--txt3)', marginTop: 2 }}>
              Configure your LLM provider
            </div>
          </div>
          <button onClick={onClose} style={{
            background: 'none', border: 'none', color: 'var(--txt2)', cursor: 'pointer', padding: 4, borderRadius: 6,
          }}
            onMouseEnter={e => e.currentTarget.style.color = 'var(--txt)'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--txt2)'}
          >
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '1.25rem' }}>
          {/* Provider select */}
          <Field label="LLM Provider">
            <div style={{ display: 'flex', gap: 8 }}>
              {['gemini', 'anthropic'].map(p => (
                <button key={p} onClick={() => set('provider', p)} style={{
                  flex: 1, padding: '8px 0', borderRadius: 8,
                  border: '1px solid',
                  borderColor: form.provider === p ? 'var(--accent)' : 'var(--border)',
                  background: form.provider === p ? 'rgba(108,99,255,0.1)' : 'var(--bg3)',
                  color: form.provider === p ? 'var(--accent)' : 'var(--txt2)',
                  fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', transition: 'all 0.15s',
                }}>
                  {p === 'gemini' ? '🆓 Google Gemini' : '🤖 Anthropic'}
                </button>
              ))}
            </div>
            {form.provider === 'gemini' && (
              <div style={{ marginTop: 6, padding: '6px 10px', background: 'rgba(74,222,128,0.07)', border: '1px solid rgba(74,222,128,0.2)', borderRadius: 6, fontSize: '0.72rem', color: '#4ade80' }}>
                ✓ Gemini free tier — no billing required
              </div>
            )}
          </Field>

          {/* Gemini key */}
          {form.provider === 'gemini' && (
            <>
              <Field label="Gemini API Key" hint={
                <a href="https://aistudio.google.com/apikey" target="_blank" rel="noreferrer"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 3, color: 'var(--accent)', fontSize: '0.7rem' }}>
                  Get free key <ExternalLink size={9} />
                </a>
              }>
                <PasswordInput
                  value={form.geminiApiKey}
                  onChange={v => set('geminiApiKey', v)}
                  placeholder="AIzaSy..."
                  show={showKey}
                  onToggle={() => setShowKey(s => !s)}
                />
              </Field>

              <Field label="Model">
                <select value={form.model} onChange={e => set('model', e.target.value)} style={selectStyle}>
                  {GEMINI_MODELS.map(m => (
                    <option key={m.value} value={m.value}>{m.label}</option>
                  ))}
                </select>
              </Field>
            </>
          )}

          {/* Anthropic key */}
          {form.provider === 'anthropic' && (
            <Field label="Anthropic API Key" hint={<a href="https://console.anthropic.com" target="_blank" rel="noreferrer" style={{ color: 'var(--accent)', fontSize: '0.7rem', display: 'inline-flex', alignItems: 'center', gap: 3 }}>Console <ExternalLink size={9} /></a>}>
              <PasswordInput
                value={form.anthropicApiKey}
                onChange={v => set('anthropicApiKey', v)}
                placeholder="sk-ant-..."
                show={showKey}
                onToggle={() => setShowKey(s => !s)}
              />
            </Field>
          )}

          {/* Test connection */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4 }}>
            <button onClick={testConnection} disabled={testing} style={{
              padding: '6px 14px', borderRadius: 7, fontSize: '0.75rem', fontWeight: 500,
              border: '1px solid var(--border2)', background: 'var(--bg3)', color: 'var(--txt2)',
              cursor: testing ? 'not-allowed' : 'pointer', transition: 'all 0.15s',
            }}>
              {testing ? 'Testing…' : 'Test API server'}
            </button>
            {testResult && (
              <span style={{ fontSize: '0.73rem', color: testResult.ok ? '#4ade80' : '#f87171', display: 'flex', alignItems: 'center', gap: 4 }}>
                {testResult.ok ? <CheckCircle size={12} /> : '✕'}
                {testResult.msg}
              </span>
            )}
          </div>
        </div>

        {/* Footer */}
        <div style={{
          padding: '1rem 1.25rem', borderTop: '1px solid var(--border)',
          display: 'flex', gap: 8, justifyContent: 'flex-end',
        }}>
          <button onClick={onClose} style={{
            padding: '7px 16px', borderRadius: 7, fontSize: '0.8rem', fontWeight: 500,
            border: '1px solid var(--border2)', background: 'transparent', color: 'var(--txt2)',
            cursor: 'pointer',
          }}>
            Cancel
          </button>
          <button onClick={() => onSave(form)} style={{
            padding: '7px 20px', borderRadius: 7, fontSize: '0.8rem', fontWeight: 600,
            border: 'none',
            background: 'linear-gradient(135deg,#6c63ff,#4f46e5)',
            color: '#fff', cursor: 'pointer',
          }}>
            Save Settings
          </button>
        </div>
      </div>
    </div>
  )
}

function Field({ label, hint, children }) {
  return (
    <div style={{ marginBottom: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        <label style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--txt2)' }}>{label}</label>
        {hint}
      </div>
      {children}
    </div>
  )
}

function PasswordInput({ value, onChange, placeholder, show, onToggle }) {
  return (
    <div style={{ position: 'relative' }}>
      <input
        type={show ? 'text' : 'password'}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: '100%', padding: '8px 36px 8px 10px',
          background: 'var(--bg3)', border: '1px solid var(--border2)',
          borderRadius: 7, color: 'var(--txt)', fontSize: '0.82rem',
          fontFamily: 'var(--mono)', outline: 'none',
        }}
        onFocus={e => e.target.style.borderColor = 'rgba(108,99,255,0.5)'}
        onBlur={e => e.target.style.borderColor = 'var(--border2)'}
      />
      <button onClick={onToggle} style={{
        position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)',
        background: 'none', border: 'none', color: 'var(--txt3)', cursor: 'pointer', padding: 2,
      }}>
        {show ? <EyeOff size={13} /> : <Eye size={13} />}
      </button>
    </div>
  )
}

const selectStyle = {
  width: '100%', padding: '8px 10px',
  background: 'var(--bg3)', border: '1px solid var(--border2)',
  borderRadius: 7, color: 'var(--txt)', fontSize: '0.8rem',
  outline: 'none', cursor: 'pointer',
}
