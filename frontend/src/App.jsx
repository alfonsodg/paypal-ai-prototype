import { useState } from 'react'
import Audit from './components/Audit.jsx'
import Chat from './components/Chat.jsx'
import Clients from './components/Clients.jsx'
import Dashboard from './components/Dashboard.jsx'
import Recurring from './components/Recurring.jsx'
import { t } from './i18n.js'

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0)
  const [lang, setLang] = useState('es')
  const [dark, setDark] = useState(false)
  const [tab, setTab] = useState('dashboard')
  const tabs = ['dashboard', 'chat', 'clients', 'recurring', 'audit']
  return (
    <div className={dark ? 'dark' : ''}>
      <main style={{ padding: 24, fontFamily: 'sans-serif', maxWidth: 900, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
          <h1>{t(lang, 'title')}</h1>
          <div>
            <button onClick={() => setLang(lang === 'es' ? 'en' : 'es')} style={{ marginRight: 8 }}>{lang === 'es' ? 'EN' : 'ES'}</button>
            <button onClick={() => setDark(!dark)}>{dark ? 'Light' : 'Dark'}</button>
          </div>
        </div>
        <div style={{ marginBottom: 16 }}>
          {tabs.map((tb) => (
            <button key={tb} onClick={() => setTab(tb)} style={{ marginRight: 4, fontWeight: tab === tb ? 'bold' : 'normal' }}>{tb}</button>
          ))}
        </div>
        {tab === 'chat' && <Chat onCreated={() => setRefreshKey((k) => k + 1)} lang={lang} />}
        {tab === 'dashboard' && <Dashboard refreshKey={refreshKey} lang={lang} />}
        {tab === 'clients' && <Clients refreshKey={refreshKey} />}
        {tab === 'recurring' && <Recurring refreshKey={refreshKey} />}
        {tab === 'audit' && <Audit refreshKey={refreshKey} />}
      </main>
    </div>
  )
}