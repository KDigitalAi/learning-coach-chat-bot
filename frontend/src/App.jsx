import { useState, useEffect, useRef } from 'react'
import ChatInterface from './components/ChatInterface'
import OnboardingModal from './components/OnboardingModal'
import './App.css'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

const buildApiUrl = (path) => `${API_BASE}${path}`

function App() {
  const [sessionId, setSessionId] = useState(null)
  const [hasConsent, setHasConsent] = useState(false)
  const [showOnboarding, setShowOnboarding] = useState(true)
  const [forceUpdate, setForceUpdate] = useState(0)

  const updateConsent = async (sessionId, consent, onboardingData = null) => {
    try {
      const response = await fetch(buildApiUrl('/api/onboarding/consent'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          consent: consent,
          session_id: sessionId,
          onboarding_data: onboardingData,
        }),
      })
      const data = await response.json()
      if (data.success) {
        setHasConsent(consent)
        localStorage.setItem('learning_coach_consent', String(consent))
      }
    } catch (error) {
      console.error('Error updating consent:', error)
    }
  }

  useEffect(() => {
    // Get or create session ID from localStorage
    let storedSessionId = localStorage.getItem('learning_coach_session_id')
    if (!storedSessionId) {
      storedSessionId = crypto.randomUUID()
      localStorage.setItem('learning_coach_session_id', storedSessionId)
    }
    setSessionId(storedSessionId)

    // Check if user has already completed onboarding
    // Only skip onboarding if BOTH consent AND onboarding data exist
    const consent = localStorage.getItem('learning_coach_consent')
    const onboardingData = localStorage.getItem('learning_coach_onboarding_data')
    
    if (consent === 'true' && onboardingData) {
      // User has completed onboarding - skip it
      try {
        const parsedData = JSON.parse(onboardingData)
        if (parsedData.learningLevel && parsedData.preferredStyle) {
          setHasConsent(true)
          setShowOnboarding(false)
          // Update consent on server
          updateConsent(storedSessionId, true, parsedData)
          return
        }
      } catch (e) {
        console.error('Error parsing onboarding data:', e)
      }
    }
    
    // If no valid onboarding data, show onboarding
    setShowOnboarding(true)
  }, [])

  const handleConsent = async (consent, onboardingData) => {
    console.log('🔵 handleConsent called:', { consent, onboardingData, currentSessionId: sessionId })
    
    try {
      // Ensure we have a session ID
      let currentSessionId = sessionId
      if (!currentSessionId) {
        currentSessionId = localStorage.getItem('learning_coach_session_id')
        if (!currentSessionId) {
          currentSessionId = crypto.randomUUID()
          localStorage.setItem('learning_coach_session_id', currentSessionId)
          console.log('📝 Created new sessionId:', currentSessionId)
        }
        setSessionId(currentSessionId)
      }
      
      console.log('📤 Calling updateConsent API with:', { sessionId: currentSessionId, consent, onboardingData })
      
      // Update consent on server (fire and forget - don't block UI)
      updateConsent(currentSessionId, consent, onboardingData).catch(err => {
        console.error('API error (non-blocking):', err)
      })
      
      console.log('✅ API call initiated, updating state IMMEDIATELY...')
      
      // IMMEDIATELY close onboarding - don't wait for API
      // This ensures the UI updates right away
      setShowOnboarding(false)
      setHasConsent(consent || false)
      
      // Also save to localStorage immediately
      localStorage.setItem('learning_coach_consent', String(consent))
      
      // Save onboarding data to localStorage so we know it's completed
      if (onboardingData && onboardingData.learningLevel) {
        localStorage.setItem('learning_coach_onboarding_data', JSON.stringify(onboardingData))
      }
      
      // Force a re-render
      setForceUpdate(prev => prev + 1)
      
      console.log('✅ State updated IMMEDIATELY - showOnboarding=false')
      console.log('✅ Chat interface should now be visible')
    } catch (error) {
      console.error('❌ Error in handleConsent:', error)
      console.error('Error details:', error.message, error.stack)
      // Still close onboarding even if there's an error
      console.log('⚠️ Closing onboarding despite error')
      setShowOnboarding(false)
      setHasConsent(consent || false)
      localStorage.setItem('learning_coach_consent', String(consent))
      
      // Save onboarding data to localStorage
      if (onboardingData && onboardingData.learningLevel) {
        localStorage.setItem('learning_coach_onboarding_data', JSON.stringify(onboardingData))
      }
      
      setForceUpdate(prev => prev + 1)
      console.log('✅ Onboarding closed despite error')
    }
  }

  // Always show chat interface - onboarding is now integrated into chat
  if (!sessionId) {
    // Try to get from localStorage
    const storedSessionId = localStorage.getItem('learning_coach_session_id')
    if (storedSessionId) {
      setSessionId(storedSessionId)
      return <div className="app" style={{ padding: '20px', textAlign: 'center', color: '#ffffff' }}>Loading...</div>
    }
    return <div className="app" style={{ padding: '20px', textAlign: 'center', color: '#ffffff' }}>Loading...</div>
  }
  
  return (
    <div className="app" key={forceUpdate}>
      <ChatInterface sessionId={sessionId} />
    </div>
  )
}

export default App


