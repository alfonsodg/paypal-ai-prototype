import { useEffect, useState } from 'react'
import { getAnalytics, getMetrics, listInvoices } from '../api/client.js'
import { t } from '../i18n.js'

export default function Dashboard({ refreshKey, lang = 'es' }) {
  const [invoices, setInvoices] = useState([])
  const [metrics, setMetrics] = useState(null)
  const [analytics, setAnalytics] = useState(null)

  useEffect(() => {
    listInvoices().then(setInvoices).catch(() => {})
    getMetrics().then(setMetrics).catch(() => {})
    getAnalytics().then(setAnalytics).catch(() => {})
  }, [refreshKey])

  const maxBilled = analytics
    ? Math.max(1, ...analytics.revenue_by_month.map((m) => m.billed))
    : 1

  return (
    <section>
      <h2>{t(lang, 'dashboard')}</h2>
      {metrics && (
        <div style={{ marginBottom: 12 }}>
          <strong>{t(lang, 'billed')}:</strong> {metrics.total_billed}{' '}
          <strong>{t(lang, 'paid')}:</strong> {metrics.total_paid}{' '}
          <strong>{t(lang, 'pending')}:</strong> {metrics.total_pending}
          {' '}<strong>{t(lang, 'avgDays')}:</strong> {analytics ? analytics.avg_days_to_pay : '-'}
        </div>
      )}
      {analytics && analytics.revenue_by_month.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <h3>{t(lang, 'revenueByMonth')}</h3>
          <svg width="100%" height="120" viewBox={`0 0 ${analytics.revenue_by_month.length * 40} 120`}>
            {analytics.revenue_by_month.map((m, i) => {
              const h = (m.billed / maxBilled) * 100
              return (
                <g key={m.month}>
                  <rect x={i * 40 + 4} y={110 - h} width={24} height={h} fill="#1d76db" />
                  <text x={i * 40 + 16} y={118} fontSize="8" textAnchor="middle">{m.month.slice(5)}</text>
                </g>
              )
            })}
          </svg>
        </div>
      )}
      {analytics && analytics.top_clients.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <h3>{t(lang, 'topClients')}</h3>
          <ul>
            {analytics.top_clients.map((c) => (
              <li key={c.name}>{c.name}: {c.total} ({c.count} invoices)</li>
            ))}
          </ul>
        </div>
      )}
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left' }}>Number</th>
            <th>Status</th>
            <th>Total</th>
            <th>PDF</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv) => (
            <tr key={inv.id}>
              <td>{inv.number}</td>
              <td>{inv.status}</td>
              <td>{inv.total}</td>
              <td>
                <a href={`http://localhost:8000/api/v1/invoices/${inv.id}/pdf`} target="_blank" rel="noreferrer">PDF</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}