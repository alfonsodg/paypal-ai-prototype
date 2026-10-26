import { useState } from 'react'
import Chat from './components/Chat.jsx'
import Dashboard from './components/Dashboard.jsx'

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0)
  return (
    <main style={{ padding: 24, fontFamily: 'sans-serif', maxWidth: 900, margin: '0 auto' }}>
      <h1>PayPal AI Prototype</h1>
      <Chat onCreated={() => setRefreshKey((k) => k + 1)} />
      <Dashboard refreshKey={refreshKey} />
    </main>
  )
}