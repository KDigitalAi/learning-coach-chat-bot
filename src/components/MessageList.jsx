import Message from './Message'
import './MessageList.css'

function MessageList({ messages, currentResponse, isLoading, messagesEndRef, onOptionSelect }) {
  return (
    <div className="message-list">
      <div className="messages-container">
        {messages.map((message) => (
          <Message 
            key={message.id} 
            message={message} 
            onOptionSelect={onOptionSelect}
          />
        ))}
        {isLoading && currentResponse && (
          <Message 
            message={{
              id: 'streaming',
              role: 'assistant',
              content: currentResponse,
              timestamp: new Date(),
              isStreaming: true
            }}
            onOptionSelect={onOptionSelect}
          />
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}

export default MessageList


