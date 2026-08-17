import { useEffect, useState } from 'react'
import { Shield, Wifi, Menu } from 'lucide-react'
import { useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { healthCheck } from '../../services/api'

const PAGE_TITLES = {
  '/chat': 'Chat',
  '/documents': 'Documents',
  '/security': 'Security Audit',
  '/dashboard': 'Dashboard'
}

export default function Topbar({ onMenuClick }) {
  const { currentUserRole, roleMeta } = useAuth()
  const location = useLocation()
  const [backendStatus, setBackendStatus] = useState('Checking...')

  useEffect(() => {
    let active = true

    healthCheck()
      .then(() => {
        if (active) setBackendStatus('Connected')
      })
      .catch(() => {
        if (active) setBackendStatus('Backend offline')
      })

    return () => {
      active = false
    }
  }, [location.pathname])

  const title = PAGE_TITLES[location.pathname] || 'Enterprise Knowledge Assistant'

  return (
    <header className="topbar">
      <div className="topbar__left">
        <button className="menu-button" onClick={onMenuClick} aria-label="Open navigation menu">
          <Menu size={18} />
        </button>
        <div>
          <p className="topbar__eyebrow">Secure enterprise AI</p>
          <h1>{title}</h1>
        </div>
      </div>

      <div className="topbar__right">
        <div className="status-pill">
          <Shield size={14} />
          <span>{roleMeta?.securityLevel || 'Standard'} access</span>
        </div>
        <div className={`status-pill ${backendStatus === 'Connected' ? 'status-pill--success' : ''}`}>
          <Wifi size={14} />
          <span>{backendStatus}</span>
        </div>
      </div>
    </header>
  )
}
