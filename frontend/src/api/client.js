const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function extractInvoice(text) {
  const r = await fetch(`${BASE}/api/v1/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!r.ok) throw new Error('extract failed')
  return r.json()
}

export async function createInvoice(payload) {
  const r = await fetch(`${BASE}/api/v1/invoices`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!r.ok) throw new Error('create failed')
  return r.json()
}

export async function listInvoices() {
  const r = await fetch(`${BASE}/api/v1/invoices`)
  if (!r.ok) throw new Error('list failed')
  return r.json()
}

export async function getMetrics() {
  const r = await fetch(`${BASE}/api/v1/metrics`)
  if (!r.ok) throw new Error('metrics failed')
  return r.json()
}

export async function getAnalytics() {
  const r = await fetch(`${BASE}/api/v1/analytics`)
  if (!r.ok) throw new Error('analytics failed')
  return r.json()
}