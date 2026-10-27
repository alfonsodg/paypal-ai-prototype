import { useEffect, useState } from 'react'
import { getAudit } from '../api/client.js'

export default function Audit({ refreshKey }) {
  const [rows, setRows] = useState([])
  useEffect(() => {
    getAudit().then(setRows).catch(() => {})
  }, [refreshKey])

  return (
    <section>
      <h2>Audit Log</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead><tr><th>Time</th><th>Entity</th><th>ID</th><th>Action</th><th>Details</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.created_at}</td><td>{r.entity}</td><td>{r.id}</td><td>{r.action}</td><td>{r.details}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}