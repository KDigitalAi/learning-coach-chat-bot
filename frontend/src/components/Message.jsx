import './Message.css'
import MessageOptions from './MessageOptions'

function Message({ message, onOptionSelect }) {
  const isUser = message.role === 'user'
  const isStreaming = message.isStreaming
  const isOnboardingQuestion = message.isOnboardingQuestion
  const options = message.options

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'}`}>
      <div className="message-content">
        <div className="message-avatar">
          {isUser ? '🧑' : '💡'}
        </div>
        <div className="message-bubble">
          <p className="message-text">
            {message.content}
            {isStreaming && <span className="cursor">|</span>}
          </p>
          {options && onOptionSelect && (
            <MessageOptions 
              options={options} 
              onSelect={onOptionSelect}
              questionType={message.questionType || 'choice'}
            />
          )}
          <span className="message-time">
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </span>
        </div>
      </div>
    </div>
  )
}

export default Message


