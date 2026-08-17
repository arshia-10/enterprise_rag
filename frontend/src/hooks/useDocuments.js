import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { getDocuments } from '../services/api'

export function useDocuments() {
  const { currentUserRole } = useAuth()

  const [documents, setDocuments] = useState([])

  useEffect(() => {
    async function fetchDocuments() {
      if (!currentUserRole) {
        return
      }

      try {
        const data = await getDocuments(currentUserRole)

        setDocuments(data.documents)
      } catch (error) {
        console.error('Failed to load documents:', error)
        setDocuments([])
      }
    }

    fetchDocuments()
  }, [currentUserRole])

  return {
    documents
  }
}