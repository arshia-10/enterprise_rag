import UploadPanel from '../components/documents/UploadPanel'
import { useDocuments } from '../hooks/useDocuments'
import SecurityBadge from '../components/common/SecurityBadge'

export default function DocumentsPage() {
  const { documents } = useDocuments()

  return (
    <div className="page-stack">
      <section className="panel">
        <div className="section-header">
          <div>
            <p className="eyebrow">Document Index</p>
            <h2>Enterprise Documents</h2>
          </div>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Document</th>
                <th>Classification</th>
                <th>Status</th>
                <th>Access</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.filename}</td>
                  <td>{doc.classification}</td>
                  <td><SecurityBadge status="SECURE" /></td>
                  <td>{doc.access}</td>
                  <td>
                    <button type="button" className="link-button">Review</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <UploadPanel />
    </div>
  )
}
