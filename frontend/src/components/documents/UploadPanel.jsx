import { useRef, useState } from 'react'
import { FileUp, CheckCircle2, LoaderCircle, AlertCircle } from 'lucide-react'
import { uploadDocument } from '../../services/api'

const PROCESS_STEPS = [
  'Uploading PDF...',
  'Processing document...',
  'Extracting text...',
  'Creating chunks...',
  'Generating embeddings...',
  'Updating vector store...',
  'Document indexed successfully.'
]

export default function UploadPanel() {
  const inputRef = useRef(null)
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadState, setUploadState] = useState('idle')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleFile = async (file) => {
    if (!file) return

    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      setUploadState('error')
      setError('Only PDF files are supported.')
      return
    }

    setSelectedFile(file)
    setError('')
    setMessage('Document uploaded successfully.')
    setUploadState('uploading')
    setIsUploading(true)

    try {
      await uploadDocument(file)
      setUploadState('success')
      setMessage('Document indexed successfully.')
      setIsUploading(false)
    } catch (uploadError) {
      setUploadState('error')
      setError(uploadError.message || 'Upload failed.')
      setIsUploading(false)
    }
  }

  const onBrowse = (event) => {
    const file = event.target.files?.[0]
    handleFile(file)
    event.target.value = ''
  }

  const onDrop = (event) => {
    event.preventDefault()
    setDragActive(false)
    const file = event.dataTransfer.files?.[0]
    handleFile(file)
  }

  return (
    <div className="upload-panel">
      <div
        className={`upload-dropzone ${dragActive ? 'upload-dropzone--active' : ''}`}
        onDragOver={(event) => {
          event.preventDefault()
          setDragActive(true)
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={onDrop}
      >
        <input ref={inputRef} type="file" accept="application/pdf" onChange={onBrowse} aria-label="Upload PDF document" />
        <FileUp size={26} />
        <h3>Upload PDF</h3>
        <p>Drag and drop a PDF or browse from your device.</p>
        <button type="button" className="primary-button" onClick={() => inputRef.current?.click()}>
          Browse files
        </button>
      </div>

      {selectedFile && (
        <div className="upload-status">
          <div className="upload-status__header">
            <span className="upload-status__name">{selectedFile.name}</span>
            {uploadState === 'success' ? (
              <CheckCircle2 size={18} color="#22C55E" />
            ) : uploadState === 'error' ? (
              <AlertCircle size={18} color="#EF4444" />
            ) : (
              <LoaderCircle size={18} className="spin" />
            )}
          </div>

          <div className="upload-steps">
            {PROCESS_STEPS.map((step, index) => {
              const active =
                uploadState === 'success' && index < PROCESS_STEPS.length
                || uploadState === 'uploading' && index <= 5
                || uploadState === 'error' && index === 0

              return (
                <div key={step} className={`upload-step ${active ? 'upload-step--active' : ''}`}>
                  {step}
                </div>
              )
            })}
          </div>

          {message && <p className="success-text">{message}</p>}
          {error && <p className="error-text">{error}</p>}
        </div>
      )}
    </div>
  )
}
