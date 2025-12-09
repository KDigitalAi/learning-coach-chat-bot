import { useState } from 'react'
import './OnboardingModal.css'

function OnboardingModal({ onConsent }) {
  const [step, setStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    learningLevel: '',
    interests: '',
    goals: '',
    preferredStyle: '',
    consent: false
  })

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleNext = () => {
    if (step < 5) {
      setStep(step + 1)
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  const handleSubmit = async () => {
    if (isSubmitting) {
      console.log('Already submitting, ignoring click')
      return // Prevent double submission
    }
    
    console.log('🚀 handleSubmit called with formData:', formData)
    setIsSubmitting(true)
    
    try {
      // Send onboarding data to backend
      console.log('📤 Calling onConsent with:', { consent: formData.consent, onboardingData: formData })
      await onConsent(formData.consent, formData)
      console.log('✅ onConsent completed successfully')
      // onConsent will handle closing the modal via setShowOnboarding(false)
    } catch (error) {
      console.error('❌ Error in handleSubmit:', error)
      // Still close modal even if there's an error
      try {
        await onConsent(formData.consent || false, formData)
        console.log('✅ Modal closed despite error')
      } catch (e) {
        console.error('❌ Error closing modal:', e)
        // Force close by calling onConsent with minimal data
        onConsent(false, {})
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const isStepValid = () => {
    switch(step) {
      case 1: return formData.learningLevel !== ''
      case 2: return formData.interests.trim() !== ''
      case 3: return formData.goals.trim() !== ''
      case 4: return formData.preferredStyle !== ''
      case 5: return true // Step 5 is always valid (consent is optional)
      default: return true
    }
  }

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-modal">
        <div className="onboarding-header">
          <h1>Welcome to Learning Coach!</h1>
          <p className="subtitle">Let's personalize your learning experience</p>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${(step / 5) * 100}%` }}></div>
          </div>
          <p className="step-indicator">Step {step} of 5</p>
        </div>
        
        <div className="onboarding-content">
          {step === 1 && (
            <div className="onboarding-step">
              <h2>What's your current learning level?</h2>
              <p className="step-description">This helps me understand your background and adapt my teaching style.</p>
              <div className="option-group">
                {['Beginner', 'Intermediate', 'Advanced'].map(level => (
                  <button
                    key={level}
                    className={`option-btn ${formData.learningLevel === level ? 'selected' : ''}`}
                    onClick={() => handleInputChange('learningLevel', level)}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="onboarding-step">
              <h2>What topics are you interested in learning?</h2>
              <p className="step-description">Tell me about subjects, skills, or areas you'd like to explore.</p>
              <textarea
                className="onboarding-input"
                placeholder="e.g., Python programming, data science, web development, machine learning..."
                value={formData.interests}
                onChange={(e) => handleInputChange('interests', e.target.value)}
                rows={4}
              />
            </div>
          )}

          {step === 3 && (
            <div className="onboarding-step">
              <h2>What are your learning goals?</h2>
              <p className="step-description">What do you hope to achieve or build? This helps me guide you better.</p>
              <textarea
                className="onboarding-input"
                placeholder="e.g., Build a web app, understand algorithms, learn a new programming language..."
                value={formData.goals}
                onChange={(e) => handleInputChange('goals', e.target.value)}
                rows={4}
              />
            </div>
          )}

          {step === 4 && (
            <div className="onboarding-step">
              <h2>How do you prefer to learn?</h2>
              <p className="step-description">This helps me choose the best approach for you.</p>
              <div className="option-group">
                {[
                  { value: 'visual', label: '🎨 Visual - I learn by seeing examples and diagrams' },
                  { value: 'hands-on', label: '✋ Hands-on - I learn by doing and practicing' },
                  { value: 'theoretical', label: '📚 Theoretical - I like understanding concepts first' },
                  { value: 'mixed', label: '🔄 Mixed - A combination works best for me' }
                ].map(style => (
                  <button
                    key={style.value}
                    className={`option-btn-large ${formData.preferredStyle === style.value ? 'selected' : ''}`}
                    onClick={() => handleInputChange('preferredStyle', style.value)}
                  >
                    {style.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="onboarding-step">
              <h2>Almost done! 🎉</h2>
              <p className="step-description">To provide the best personalized learning experience, I can remember our conversation during this session.</p>
              
              <div className="consent-section">
                <div className="consent-checkbox">
                  <input
                    type="checkbox"
                    id="consent"
                    checked={formData.consent}
                    onChange={(e) => handleInputChange('consent', e.target.checked)}
                  />
                  <label htmlFor="consent">
                    <strong>Yes, remember our conversation</strong><br />
                    <span className="consent-subtext">This helps me understand your learning journey and provide better, contextual responses. Your conversation is stored only for this session.</span>
                  </label>
                </div>
                <p className="consent-note" style={{ marginTop: '15px', fontSize: '0.9rem', color: '#666', fontStyle: 'italic' }}>
                  Note: You can still use Learning Coach without checking this, but responses won't be personalized based on your conversation history.
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="onboarding-footer">
          {step > 1 && (
            <button className="btn btn-secondary" onClick={handleBack}>
              ← Back
            </button>
          )}
          <div style={{ flex: 1 }}></div>
          {step < 5 ? (
            <button 
              className="btn btn-primary" 
              onClick={handleNext}
              disabled={!isStepValid()}
            >
              Next →
            </button>
          ) : (
            <button 
              className="btn btn-primary" 
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                console.log('🔘 "Start Learning!" button clicked!')
                handleSubmit()
              }}
              disabled={isSubmitting}
              type="button"
            >
              {isSubmitting ? 'Starting...' : 'Start Learning! 🚀'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default OnboardingModal


