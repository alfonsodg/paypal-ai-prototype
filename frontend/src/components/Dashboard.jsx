import { useEffect, useState } from 'react'
import { getMetrics, listInvoices } from '../api/client.js'

export default function Dashboard({ refreshKey }) {
  const [invoices, setInvoices] = useState([])
  const [metrics, setMetrics] = useState(null)

  useEffect(() => {
    listInvoices().then(setInvoices).catch(() => {})
    getMetrics().then(setMetrics).catch(() => {})
  }, [refreshKey])

  return (
    <section>
      <h2>Dashboard</h2>
      {metrics && (
        <div style={{ marginBottom: 12 }}>
          <strong>Billed:</strong> {metrics.total_billed}{' '}
          <strong>Paid:</strong> {metrics.total_paid}{' '}
          <strong>Pending:</strong> {metrics.total_pending}
        </div>
      )}
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left' }}>Number</th>
            <th>Status</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv) => (
            <tr key={inv.id}>
              <td>{inv.number}</td>
              <td>{inv.status}</td>
              <td>{inv.total}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}