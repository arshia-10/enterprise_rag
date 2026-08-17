export default function SourceCard({ source }) {
  const safePage = source?.page ?? 'Unknown'
  const safeSimilarity = source?.similarity ?? 'N/A'
  const safeCrossEncoder = source?.cross_encoder_score ?? 'N/A'

  return (
    <div className="source-card">
      <div className="source-card__header">
        <span className="source-card__title">Source</span>
      </div>
      <div className="source-card__body">
        <p className="source-card__name">{source?.source || 'Unknown source'}</p>
        <p className="source-card__meta">Page {safePage}</p>
        <div className="source-card__scores">
          {safeSimilarity !== 'N/A' && (
            <div>
              <span className="source-card__label">Relevance</span>
              <strong>{Number(safeSimilarity).toFixed(3)}</strong>
            </div>
          )}
          {safeCrossEncoder !== 'N/A' && (
            <div>
              <span className="source-card__label">Cross-Encoder</span>
              <strong>{Number(safeCrossEncoder).toFixed(2)}</strong>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
