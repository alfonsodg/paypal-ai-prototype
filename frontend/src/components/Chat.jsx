import { useState } from 'react'
import { createInvoice, extractInvoice } from '../api/client.js'

export default function Chat({ onCreated }) {
  const [text, setText] = useState('')
  const [extracted, setExtracted] = useState(null)
  const [status, setStatus] = useState('')

  const handleExtract = async () => {
    setStatus('Extracting...')
    try {
      const data = await extractInvoice(text)
      setExtracted(data)
      setStatus('Extracted. Review and create invoice.')
    } catch (e) {
      setStatus('Error: ' + e.message)
    }
  }

  const handleCreate = async () => {
    if (!extracted) return
    setStatus('Creating invoice...')
    try {
      const payload = {
        client_name: extracted.client_name || 'Unknown',
        client_email: extracted.client_email || 'unknown@example.com',
        currency: extracted.currency || 'USD',
        tax_rate: extracted.tax_rate || 0,
        items: (extracted.items || []).map((i) => ({
          description: i.description,
          quantity: i.quantity,
          unit_price: i.unit_price,
        })),
      }
      const inv = await createInvoice(payload)
      setStatus(`Invoice ${inv.number} created (total ${inv.total})`)
      setExtracted(null)
      setText('')
      onCreated?.()
    } catch (e) {
      setStatus('Error: ' + e.message)
    }
  }

  return (
    <section style={{ marginBottom: 24 }}>
      <h2>Chat</h2>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={3}
        style={{ width: '100%' }}
        placeholder="Factura a Juan por 5 horas de consultoria a $50/hora"
      />
      <div style={{ marginTop: 8 }}>
        <button onClick={handleExtract}>Extract</button>
        {extracted && <button onClick={handleCreate} style={{ marginLeft: 8 }}>Create Invoice</button>}
      </div>
      {extracted && (
        <pre style={{ background: '#f5f5f5', padding: 8, marginTop: 8 }}>
          {JSON.stringify(extracted, null, 2)}
        </pre>
      )}
      <p>{status}</p>
    </section>
  )
}