import { useState } from 'react'
import Chat from './components/Chat.jsx'
import Dashboard from './components/Dashboard.jsx'
import { t } from './i18n.js'

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0)
  const [lang, setLang] = useState('es')
  const [dark, setDark] = useState(false)
  return (
    <div className={dark ? 'dark' : ''}>
      <main style={{ padding: 24, fontFamily: 'sans-serif', maxWidth: 900, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>{t(lang, 'title')}</h1>
          <div>
            <button onClick={() => setLang(lang === 'es' ? 'en' : 'es')} style={{ marginRight: 8 }}>{lang === 'es' ? 'EN' : 'ES'}</button>
            <button onClick={() => setDark(!dark)}>{dark ? 'Light' : 'Dark'}</button>
          </div>
        </div>
      <Chat onCreated={() => setRefreshKey((k) => k + 1)} lang={lang} />
      <Dashboard refreshKey={refreshKey} lang={lang} />
    </main>
    </div>
  )
}