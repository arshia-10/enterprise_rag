import { useState } from 'react'
import { ArrowRight, Lock, ShieldCheck } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth, ROLE_META } from '../context/AuthContext'

const roles = Object.entries(ROLE_META)

export default function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [selectedRole, setSelectedRole] = useState('employee')

  const handleSelectRole = (roleKey) => {
    setSelectedRole(roleKey)
  }

  const handleContinue = () => {
    login(selectedRole)
    navigate('/chat')
  }

  const selectedMeta = ROLE_META[selectedRole]

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <div className="brand brand--centered">
            <div className="brand__mark">
              <Lock size={18} />
            </div>
            <div>
              <p className="brand__eyebrow">Enterprise Security</p>
              <h1>Enterprise Knowledge Assistant</h1>
            </div>
          </div>
          <p className="subtitle">Secure • Role-Aware • Grounded RAG</p>
        </div>

        <div className="role-grid">
          {roles.map(([key, meta]) => (
            <button
              key={key}
              className={`role-card ${selectedRole === key ? 'role-card--selected' : ''}`}
              onClick={() => handleSelectRole(key)}
              type="button"
              aria-pressed={selectedRole === key}
            >
              <div className="role-card__header">
                <span className="role-card__name">{meta.label}</span>
                <ShieldCheck size={18} className="role-card__icon" />
              </div>
              <p className="role-card__level">Access Level: {meta.accessLevel}</p>
              <p className="role-card__desc">{meta.description}</p>
            </button>
          ))}
        </div>

        <div className="login-footer">
          <div className="role-preview">
            <span className="label">Selected Role</span>
            <strong>{selectedMeta.label}</strong>
          </div>
          <div className="role-preview">
            <span className="label">Security Level</span>
            <strong>{selectedMeta.securityLevel}</strong>
          </div>
          <button className="primary-button" type="button" onClick={handleContinue}>
            Continue
            <ArrowRight size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
