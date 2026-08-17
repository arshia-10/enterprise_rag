import { useEffect, useMemo, useRef, useState } from 'react'
import { SendHorizonal, RefreshCcw, ShieldAlert, LoaderCircle, Sparkles, MessageSquareText } from 'lucide-react'
import ExplainabilityDrawer from '../components/chat/ExplainabilityDrawer'
import SourceCard from '../components/chat/SourceCard'
import { useAuth } from '../context/AuthContext'
import { useChat } from '../hooks/useChat'

const emptyStateMessage = 'Ask a question about authorized enterprise documents.'

export default function ChatPage() {
  const { currentUserRole } = useAuth()
  const { messages, isLoading, error, sendMessage, clearChat } = useChat()
  const [draft, setDraft] = useState('')
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const messageEndRef = useRef(null)

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const displayedMessages = useMemo(() => {
    if (messages.length === 0) {
      return []
    }

    return messages
  }, [messages])

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!draft.trim()) return

    const message = await sendMessage(draft, currentUserRole)
    if (message) {
      setSelectedAnswer(message)
    }
    setDraft('')
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSubmit(event)
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-shell">
        <div className="chat-header">
          <div>
            <p className="eyebrow">Knowledge Retrieval</p>
            <h2>Secure Query Workspace</h2>
          </div>
          <button type="button" className="secondary-button" onClick={clearChat}>
            <RefreshCcw size={16} />
            New Chat
          </button>
        </div>

        <div className="chat-thread" role="log" aria-live="polite">
          {displayedMessages.length === 0 ? (
            <div className="empty-state">
              <MessageSquareText size={28} />
              <h3>Ready for authorized queries</h3>
              <p>{emptyStateMessage}</p>
            </div>
          ) : (
            displayedMessages.map((message) => (
              <div key={message.id} className={`message-row message-row--${message.role}`}>
                <div className={`message-bubble ${message.isSecurityRefusal ? 'refusal-bubble' : ''}`}>
                  {message.isSecurityRefusal && (
                    <div className="refusal-header">
                      <ShieldAlert size={16} />
                      <span>Information Not Available</span>
                    </div>
                  )}
                  <p>{message.content}</p>
                  {message.role === 'assistant' && message.sources?.length > 0 && (
                    <div className="source-list-wrapper">
                      {message.sources.map((source, index) => (
                        <SourceCard key={`${source.source}-${index}`} source={source} />
                      ))}
                    </div>
                  )}

                  {message.role === 'assistant' && (
                    <button
                      type="button"
                      className="text-button"
                      onClick={() => setSelectedAnswer(message)}
                    >
                      [ Why this answer? ]
                    </button>
                  )}
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="message-row message-row--assistant">
              <div className="message-bubble message-bubble--loading">
                <div className="typing-indicator" aria-label="Loading answer">
                  <span /><span /><span />
                </div>
                <p>Thinking... Searching authorized documents... Generating answer...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="status-banner status-banner--error">
              <ShieldAlert size={16} />
              <span>{error}</span>
            </div>
          )}

          <div ref={messageEndRef} />
        </div>

        <form className="composer" onSubmit={handleSubmit}>
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            placeholder="Ask about enterprise documents..."
            aria-label="Ask a question"
          />
          <button type="submit" className="primary-button" disabled={isLoading || !draft.trim()}>
            {isLoading ? <LoaderCircle size={16} className="spin" /> : <SendHorizonal size={16} />}
            Send
          </button>
        </form>
      </div>

      <ExplainabilityDrawer isOpen={Boolean(selectedAnswer)} onClose={() => setSelectedAnswer(null)} answer={selectedAnswer} />
    </div>
  )
}
