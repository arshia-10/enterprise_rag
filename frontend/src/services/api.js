const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  if (!response.ok) {
    const errorText = await response.text()
    let detail = 'The server could not complete the request.'

    try {
      const parsed = JSON.parse(errorText)
      detail = parsed.detail || detail
    } catch {
      if (errorText) {
        detail = errorText
      }
    }

    throw new Error(detail)
  }

  const contentType = response.headers.get('content-type') || ''

  if (contentType.includes('application/json')) {
    return response.json()
  }

  return response.text()
}

export async function healthCheck() {
  return request('/health')
}
export async function getDocuments(role) {
  return request(
    `/documents?role=${encodeURIComponent(role)}`
  )
}

export async function askQuestion(question, role) {
  return request('/ask', {
    method: 'POST',
    body: JSON.stringify({
      question,
      role
    })
  })
}

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const errorText = await response.text()
    let detail = 'Upload failed. Please try a different PDF.'

    try {
      const parsed = JSON.parse(errorText)
      detail = parsed.detail || detail
    } catch {
      if (errorText) {
        detail = errorText
      }
    }

    throw new Error(detail)
  }

  const contentType = response.headers.get('content-type') || ''

  if (contentType.includes('application/json')) {
    return response.json()
  }

  return response.text()
}

export { API_BASE_URL }
