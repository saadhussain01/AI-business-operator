// src/utils/api.js — API client for the FastAPI backend

const BASE = '/api'

export async function createTask(payload) {
  const res = await fetch(`${BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getTask(taskId) {
  const res = await fetch(`${BASE}/tasks/${taskId}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function listTasks() {
  const res = await fetch(`${BASE}/tasks`)
  return res.ok ? res.json() : []
}

export async function listReports() {
  const res = await fetch(`${BASE}/reports`)
  return res.ok ? res.json() : []
}

export async function getHealth() {
  const res = await fetch(`${BASE}/health`)
  return res.ok ? res.json() : null
}

export function pollTask(taskId, onUpdate, interval = 2500) {
  const id = setInterval(async () => {
    try {
      const data = await getTask(taskId)
      onUpdate(data)
      if (data.status === 'completed' || data.status === 'failed') {
        clearInterval(id)
      }
    } catch {
      clearInterval(id)
    }
  }, interval)
  return () => clearInterval(id)
}
