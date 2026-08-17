import { X } from 'lucide-react'

const pipeline = [
  { step: 'Query', description: 'User question is submitted for retrieval.' },
  { step: 'Embedding', description: 'Text is converted into vector embeddings for semantic matching.' },
  { step: 'FAISS Search', description: 'Finds semantically similar document chunks.' },
  { step: 'Similarity Filtering', description: 'Removes weak or irrelevant matches before generation.' },
  { step: 'Role Authorization', description: 'Removes documents the current user is not authorized to access.' },
  { step: 'Duplicate Removal', description: 'Reduces repeated information from overlapping sources.' },
  { step: 'MMR', description: 'Reduces duplicate information while preserving diversity.' },
  { step: 'Cross-Encoder', description: 'Re-ranks retrieved chunks according to query relevance.' },
  { step: 'Generation Gate', description: 'Prevents weakly relevant context from reaching the language model.' },
  { step: 'Llama', description: 'Generates the final answer from authorized context.' },
  { step: 'Grounded Answer', description: 'Returns a response tied to retrieved enterprise documents.' }
]

export default function ExplainabilityDrawer({ isOpen, onClose, answer }) {
  if (!isOpen || !answer) return null

  return (
    <div className="drawer-overlay" role="dialog" aria-modal="true" aria-label="Why this answer?">
      <aside className="drawer">
        <div className="drawer__header">
          <div>
            <p className="eyebrow">Explainability</p>
            <h3>Why this answer?</h3>
          </div>
          <button className="icon-button" onClick={onClose} aria-label="Close explainability panel">
            <X size={18} />
          </button>
        </div>

        <div className="drawer__section">
          <div className="info-row">
            <span>User Role</span>
            <strong>{answer.roleInfo || 'employee'}</strong>
          </div>
          <div className="info-row">
            <span>Authorization Status</span>
            <strong>{answer.isSecurityRefusal ? 'Blocked' : 'Authorized'}</strong>
          </div>
        </div>

        <div className="drawer__section">
          <h4>Retrieved Sources</h4>
          {answer.sources && answer.sources.length > 0 ? (
            <ul className="source-list">
              {answer.sources.map((source, index) => (
                <li key={`${source.source}-${index}`}>
                  {source.source} · Page {source.page}
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">No authorized sources were returned for this response.</p>
          )}
        </div>

        <div className="drawer__section">
          <h4>Retrieval Pipeline</h4>
          <div className="pipeline">
            {pipeline.map((item, index) => (
              <div className="pipeline__step" key={item.step}>
                <div className="pipeline__index">{index + 1}</div>
                <div>
                  <strong>{item.step}</strong>
                  <p>{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </aside>
    </div>
  )
}
