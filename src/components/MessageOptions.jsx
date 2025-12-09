import './MessageOptions.css'

function MessageOptions({ options, onSelect, questionType }) {
  if (!options || options.length === 0 || !onSelect) {
    return null
  }

  const handleClick = (option) => {
    // Pass the value (for learningLevel) or value (for preferredStyle/interests)
    const optionValue = typeof option === 'string' ? option : option.value
    onSelect(optionValue)
  }

  return (
    <div className="message-options">
      <div className="options-label">Suggestions:</div>
      <div className="options-grid">
        {options.map((option, index) => {
          const optionValue = typeof option === 'string' ? option : option.value
          const optionLabel = typeof option === 'string' ? option : option.label

          return (
            <button
              key={index}
              className="message-option-btn"
              onClick={() => handleClick(option)}
            >
              {optionLabel}
            </button>
          )
        })}
      </div>
      {(questionType === 'choice-with-text' || questionType === 'choice-with-text-dynamic') && (
        <div className="options-hint">💡 Or type your own answer below</div>
      )}
    </div>
  )
}

export default MessageOptions

