import { useEffect, useState } from 'react'
import { createRecurring, getRecurring } from '../api/client.js'

export default function Recurring({ refreshKey }) {
  const [rows, setRows] = useState([])
  const [form, setForm] = useState({ client_id: '', description: '', amount: '', frequency: 'monthly' })
  const [status, setStatus] = useState('')

  const load = () => getRecurring().then(setRows).catch(() => {})
  useEffect(() => { load() }, [refreshKey])

  const handleCreate = async () => {
    try {
      await createRecurring({ client_id: Number(form.client_id), description: form.description, amount: Number(form.amount), frequency: form.frequency })
      setStatus('Created')
      setForm({ client_id: '', description: '', amount: '', frequency: 'monthly' })
      load()
    } catch (e) {
      setStatus('Error: ' + e.message)
    }
  }

  return (
    <section>
      <h2>Recurring Invoices</h2>
      <div style={{ marginBottom: 12 }}>
        <input placeholder="Client ID" value={form.client_id} onChange={(e) => setForm({ ...form, client_id: e.target.value })} style={{ marginRight: 4 }} />
        <input placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} style={{ marginRight: 4 }} />
        <input placeholder="Amount" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} style={{ marginRight: 4, width: 80 }} />
        <select value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })} style={{ marginRight: 4 }}>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
        <button onClick={handleCreate}>Create</button>
        <span style={{ marginLeft: 8 }}>{status}</span>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead><tr><th>ID</th><th>Client</th><th>Description</th><th>Amount</th><th>Freq</th><th>Next run</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.id}</td><td>{r.client_id}</td><td>{r.description}</td><td>{r.amount}</td><td>{r.frequency}</td><td>{r.next_run}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}