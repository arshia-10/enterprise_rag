const securityEvents = [
  {
    role: 'Employee',
    query: 'What is the confidential HR information?',
    decision: 'BLOCKED',
    unauthorized: 'NO',
    sources: 0,
    status: 'ERROR',
    timestamp: '2026-08-17 09:13:20'
  },
  {
    role: 'Employee',
    query: 'What are the standard working hours?',
    decision: 'ALLOWED',
    unauthorized: 'NO',
    sources: 2,
    status: 'AUTHORIZED',
    timestamp: '2026-08-17 09:16:40'
  },
  {
    role: 'HR',
    query: 'What confidential information is contained in the HR records?',
    decision: 'ALLOWED',
    unauthorized: 'NO',
    sources: 3,
    status: 'SECURE',
    timestamp: '2026-08-17 09:20:15'
  }
]

export default function SecurityPage() {
  return (
    <div className="page-stack">
      <section className="panel">
        <div className="section-header">
          <div>
            <p className="eyebrow">Security Monitoring</p>
            <h2>Security Audit</h2>
          </div>
        </div>

        <div className="audit-grid">
          {securityEvents.map((event) => (
            <article key={event.query} className="audit-card">
              <div className="audit-card__header">
                <span className="section-pill">SECURITY EVENT</span>
                <span className={`badge badge--${event.status === 'AUTHORIZED' ? 'success' : event.status === 'SECURE' ? 'info' : 'danger'}`}>
                  {event.decision}
                </span>
              </div>

              <div className="audit-card__content">
                <div className="audit-row">
                  <span>Role</span>
                  <strong>{event.role}</strong>
                </div>
                <div className="audit-row">
                  <span>Query</span>
                  <strong>{event.query}</strong>
                </div>
                <div className="audit-row">
                  <span>Decision</span>
                  <strong>{event.decision}</strong>
                </div>
                <div className="audit-row">
                  <span>Unauthorized info exposed</span>
                  <strong>{event.unauthorized}</strong>
                </div>
                <div className="audit-row">
                  <span>Sources returned</span>
                  <strong>{event.sources}</strong>
                </div>
                <div className="audit-row">
                  <span>Timestamp</span>
                  <strong>{event.timestamp}</strong>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
