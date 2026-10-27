import { useState } from 'react'
import Chat from './components/Chat.jsx'
import Dashboard from './components/Dashboard.jsx'
import { t } from './i18n.js'

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0)
  const [lang, setLang] = useState('es')
  return (
    <main style={{ padding: 24, fontFamily: 'sans-serif', maxWidth: 900, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>{t(lang, 'title')}</h1>
        <button onClick={() => setLang(lang === 'es' ? 'en' : 'es')}>{lang === 'es' ? 'EN' : 'ES'}</button>
      </div>
      <Chat onCreated={() => setRefreshKey((k) => k + 1)} lang={lang} />
      <Dashboard refreshKey={refreshKey} lang={lang} />
    </main>
  )
}