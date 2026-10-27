import { useEffect, useState } from 'react'
import { getClients } from '../api/client.js'

export default function Clients({ refreshKey }) {
  const [clients, setClients] = useState([])
  useEffect(() => {
    getClients().then(setClients).catch(() => {})
  }, [refreshKey])

  return (
    <section>
      <h2>Clients</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr><th>Name</th><th>Email</th><th>Tags</th><th>Invoices</th><th>Billed</th><th>Paid</th></tr>
        </thead>
        <tbody>
          {clients.map((c) => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{c.email}</td>
              <td>{c.tags || '-'}</td>
              <td>{c.invoice_count}</td>
              <td>{c.total_billed}</td>
              <td>{c.total_paid}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}