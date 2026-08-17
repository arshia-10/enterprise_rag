import { useCallback, useState } from 'react'
import { askQuestion } from '../services/api'

const REFUSAL_TEXT = 'I could not find this information in the authorized documents.'

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const appendMessage = useCallback((message) => {
    setMessages((current) => [...current, message])
  }, [])

  const sendMessage = useCallback(async (question, role) => {
    const trimmedQuestion = question.trim()

    if (!trimmedQuestion) {
      setError('Please enter a question before sending.')
      return null
    }

    setError('')
    setIsLoading(true)

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmedQuestion,
      timestamp: new Date().toISOString()
    }

    appendMessage(userMessage)

    try {
      const result = await askQuestion(trimmedQuestion, role)

      const isSecurityRefusal =
        typeof result?.answer === 'string' &&
        result.answer.includes(REFUSAL_TEXT)

      const assistantMessage = {
        id: `assistant-${Date.now()}-${Math.random()}`,
        role: 'assistant',
        content: result.answer,
        sources: Array.isArray(result.sources) ? result.sources : [],
        isSecurityRefusal,
        question: result.question || trimmedQuestion,
        roleInfo: result.role || role,
        timestamp: new Date().toISOString()
      }

      appendMessage(assistantMessage)
      setIsLoading(false)
      return assistantMessage
    } catch (err) {
      const message = err?.message || 'The system could not answer that question.'
      setError(message)
      setIsLoading(false)
      return null
    }
  }, [appendMessage])

  const clearChat = useCallback(() => {
    setMessages([])
    setError('')
  }, [])

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
    setError
  }
}
