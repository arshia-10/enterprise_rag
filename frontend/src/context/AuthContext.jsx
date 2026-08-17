import { createContext, useContext, useEffect, useMemo, useState } from 'react'

export const ROLE_META = {
  employee: {
    label: 'Employee',
    accessLevel: 'Standard',
    securityLevel: 'Standard',
    badge: 'AUTHORIZED',
    description: 'Access to routine internal documents.'
  },
  hr: {
    label: 'HR',
    accessLevel: 'Restricted HR',
    securityLevel: 'Restricted',
    badge: 'RESTRICTED',
    description: 'Access to personnel and policy records.'
  },
  manager: {
    label: 'Manager',
    accessLevel: 'Operational',
    securityLevel: 'Controlled',
    badge: 'AUTHORIZED',
    description: 'Access to team-facing business records.'
  },
  admin: {
    label: 'Admin',
    accessLevel: 'Full Administrative',
    securityLevel: 'Full',
    badge: 'SECURE',
    description: 'Administrative access for system oversight.'
  }
}

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [currentUserRole, setCurrentUserRole] = useState(() => {
    const saved = localStorage.getItem('enterprise-role')
    return saved || null
  })

  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return Boolean(localStorage.getItem('enterprise-role'))
  })

  useEffect(() => {
    if (currentUserRole) {
      localStorage.setItem('enterprise-role', currentUserRole)
      setIsAuthenticated(true)
    } else {
      localStorage.removeItem('enterprise-role')
      setIsAuthenticated(false)
    }
  }, [currentUserRole])

  const value = useMemo(
    () => ({
      currentUserRole,
      isAuthenticated,
      login: (role) => {
        setCurrentUserRole(role)
      },
      logout: () => {
        setCurrentUserRole(null)
      },
      roleMeta: currentUserRole ? ROLE_META[currentUserRole] : null
    }),
    [currentUserRole, isAuthenticated]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }

  return context
}

export default AuthContext
