const stats = [
  { label: 'Documents Indexed', value: '3' },
  { label: 'Vector Chunks', value: '128' },
  { label: 'Queries', value: '245' },
  { label: 'Allowed Queries', value: '219' },
  { label: 'Blocked Queries', value: '26' }
]

const platformStack = [
  { label: 'Embedding', value: 'all-MiniLM-L6-v2' },
  { label: 'Vector Store', value: 'FAISS' },
  { label: 'Reranker', value: 'Cross-Encoder' },
  { label: 'LLM', value: 'Llama 3.2' }
]

export default function DashboardPage() {
  return (
    <div className="page-stack">
      <div className="stats-grid">
        {stats.map((item) => (
          <div key={item.label} className="stat-card">
            <p>{item.label}</p>
            <h3>{item.value}</h3>
          </div>
        ))}
      </div>

      <section className="panel">
        <div className="section-header">
          <div>
            <p className="eyebrow">System Configuration</p>
            <h2>RAG System</h2>
          </div>
        </div>

        <div className="stack-grid">
          {platformStack.map((item) => (
            <div key={item.label} className="stack-item">
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="section-header">
          <div>
            <p className="eyebrow">Security Architecture</p>
            <h2>Pipeline</h2>
          </div>
        </div>

        <div className="pipeline-visual">
          <span>Query</span>
          <span>↓</span>
          <span>Retrieval</span>
          <span>↓</span>
          <span>Authorization</span>
          <span>↓</span>
          <span>Reranking</span>
          <span>↓</span>
          <span>Generation Gate</span>
          <span>↓</span>
          <span>LLM</span>
          <span>↓</span>
          <span>Answer</span>
        </div>
      </section>
    </div>
  )
}
