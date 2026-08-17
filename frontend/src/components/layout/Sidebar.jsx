import { ShieldCheck, FileText, BarChart3, Lock, MessageSquareText, LogOut, LayoutDashboard } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const NAV_ITEMS = [
  { to: '/chat', label: 'Chat', icon: MessageSquareText },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/security', label: 'Security Audit', icon: ShieldCheck },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard }
]

export default function Sidebar({ isOpen, onClose }) {
  const { currentUserRole, logout, roleMeta } = useAuth()

  return (
    <aside className={`sidebar ${isOpen ? 'sidebar--open' : ''}`} aria-label="Sidebar navigation">
      <div className="sidebar__header">
        <div className="brand">
          <div className="brand__mark">
            <Lock size={16} />
          </div>
          <div>
            <p className="brand__eyebrow">Enterprise</p>
            <h2>Knowledge Assistant</h2>
          </div>
        </div>
        <button className="close-button" onClick={onClose} aria-label="Close sidebar">
          ×
        </button>
      </div>

      <nav className="sidebar__nav" aria-label="Main navigation">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `nav-item ${isActive ? 'nav-item--active' : ''}`}
            onClick={onClose}
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar__footer">
        <div className="user-card">
          <p className="user-card__label">Current role</p>
          <p className="user-card__name">{roleMeta?.label || 'Role'}</p>
          <span className="user-card__level">{roleMeta?.accessLevel || 'Access Level'}</span>
        </div>

        <button className="logout-button" onClick={logout} type="button">
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </aside>
  )
}
