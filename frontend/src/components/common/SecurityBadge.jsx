const BADGE_VARIANTS = {
  AUTHORIZED: { className: 'badge badge--success', label: 'AUTHORIZED' },
  RESTRICTED: { className: 'badge badge--warning', label: 'RESTRICTED' },
  BLOCKED: { className: 'badge badge--danger', label: 'BLOCKED' },
  SECURE: { className: 'badge badge--info', label: 'SECURE' },
  CONNECTED: { className: 'badge badge--info', label: 'CONNECTED' },
  ERROR: { className: 'badge badge--danger', label: 'ERROR' }
}

export default function SecurityBadge({ status, className = '' }) {
  const config = BADGE_VARIANTS[status] || BADGE_VARIANTS.AUTHORIZED

  return <span className={`${config.className} ${className}`.trim()}>{config.label}</span>
}
