import { useState, useEffect, useRef } from 'react'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import { getLearningSuggestions } from '../utils/onboardingSuggestions'
import './ChatInterface.css'

const ONBOARDING_QUESTIONS = [
  {
    id: 'onboarding-1',
    question: "What's your current learning level?",
    description: "This helps me understand your background and adapt my teaching style.",
    type: 'choice',
    options: ['Beginner', 'Intermediate', 'Advanced'],
    field: 'learningLevel'
  },
  {
    id: 'onboarding-2',
    question: "What topics are you interested in learning?",
    description: "Tell me about subjects, skills, or areas you'd like to explore. You can click a suggestion or type your own.",
    type: 'choice-with-text',
    options: [
      'Python Programming',
      'JavaScript/Web Development',
      'Data Science',
      'Machine Learning/AI',
      'Mobile App Development',
      'Cybersecurity',
      'Cloud Computing',
      'Software Engineering'
    ],
    placeholder: "Or type your own interests...",
    field: 'interests'
  },
  {
    id: 'onboarding-3',
    question: "What are your learning goals?",
    description: "What do you hope to achieve or build? This helps me guide you better. You can click a suggestion or type your own.",
    type: 'choice-with-text-dynamic',
    placeholder: "Or type your own goals...",
    field: 'goals',
    getOptions: (interests) => {
      // Generate suggestions based on selected interest
      const interest = interests?.toLowerCase() || ''
      
      if (interest.includes('python')) {
        return [
          'Build a Python web application',
          'Learn data analysis with Python',
          'Create automation scripts',
          'Build a machine learning project',
          'Master Python fundamentals',
          'Develop a Python API',
          'Create a data visualization tool'
        ]
      } else if (interest.includes('javascript') || interest.includes('web development')) {
        return [
          'Build a full-stack web application',
          'Create a responsive website',
          'Learn React or Vue.js',
          'Build a REST API',
          'Create a portfolio website',
          'Develop a real-time chat app',
          'Master frontend frameworks'
        ]
      } else if (interest.includes('data science')) {
        return [
          'Analyze datasets and find insights',
          'Build predictive models',
          'Create data visualizations',
          'Learn statistical analysis',
          'Work with large datasets',
          'Build a data pipeline',
          'Master data analysis tools'
        ]
      } else if (interest.includes('machine learning') || interest.includes('ai')) {
        return [
          'Build a machine learning model',
          'Create a neural network',
          'Learn deep learning',
          'Build an AI chatbot',
          'Work on computer vision',
          'Develop NLP applications',
          'Master ML algorithms'
        ]
      } else if (interest.includes('mobile app')) {
        return [
          'Build a mobile app for iOS/Android',
          'Create a cross-platform app',
          'Learn React Native or Flutter',
          'Develop a mobile game',
          'Build a mobile UI/UX',
          'Create a mobile backend',
          'Master mobile development'
        ]
      } else if (interest.includes('cybersecurity')) {
        return [
          'Learn ethical hacking',
          'Understand network security',
          'Master penetration testing',
          'Build secure applications',
          'Learn cryptography',
          'Develop security protocols',
          'Master security best practices'
        ]
      } else if (interest.includes('cloud')) {
        return [
          'Deploy applications to cloud',
          'Learn AWS, Azure, or GCP',
          'Build scalable cloud infrastructure',
          'Master containerization',
          'Learn serverless architecture',
          'Create cloud-native apps',
          'Master DevOps practices'
        ]
      } else if (interest.includes('software engineering')) {
        return [
          'Build scalable software systems',
          'Master software architecture',
          'Learn design patterns',
          'Develop clean code practices',
          'Build a software project',
          'Master version control',
          'Learn software testing'
        ]
      } else {
        // Default suggestions
        return [
          'Build a complete project',
          'Master the fundamentals',
          'Create a portfolio',
          'Get job-ready skills',
          'Understand core concepts',
          'Build real-world applications',
          'Learn best practices'
        ]
      }
    }
  },
  {
    id: 'onboarding-4',
    question: "How do you prefer to learn?",
    description: "This helps me choose the best approach for you.",
    type: 'choice',
    options: [
      { value: 'hands-on', label: '✋ Hands-on - I learn by doing and practicing' },
      { value: 'theoretical', label: '📚 Theoretical - I like understanding concepts first' },
      { value: 'mixed', label: '🔄 Mixed - A combination works best for me' }
    ],
    field: 'preferredStyle'
  },
  {
    id: 'onboarding-5',
    question: "Almost done! To provide the best personalized learning experience, I can remember our conversation during this session.",
    description: "Would you like me to remember our conversation?",
    type: 'choice',
    options: [
      { value: true, label: 'Yes - Remember our conversation' },
      { value: false, label: 'No - Don\'t remember' }
    ],
    field: 'consent'
  }
]

function ChatInterface({ sessionId }) {
  const [messages, setMessages] = useState([])
  const [onboardingData, setOnboardingData] = useState({
    learningLevel: '',
    interests: '',
    goals: '',
    preferredStyle: '',
    consent: false
  })
  const [currentOnboardingStep, setCurrentOnboardingStep] = useState(0)
  const [onboardingComplete, setOnboardingComplete] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [currentResponse, setCurrentResponse] = useState('')
  const messagesEndRef = useRef(null)

  // Initialize onboarding on mount
  useEffect(() => {
    // Check if onboarding already completed for THIS session
    const completed = localStorage.getItem('learning_coach_onboarding_complete')
    const storedData = localStorage.getItem('learning_coach_onboarding_data')
    const storedSessionId = localStorage.getItem('learning_coach_session_id')
    
    // Only skip onboarding if:
    // 1. Onboarding is marked complete
    // 2. Onboarding data exists
    // 3. Session ID matches (same session)
    if (completed === 'true' && storedData && storedSessionId === sessionId) {
      try {
        const parsedData = JSON.parse(storedData)
        // Verify data is complete (has required fields)
        if (parsedData.learningLevel && parsedData.preferredStyle) {
          setOnboardingData(parsedData)
          setOnboardingComplete(true)
          setCurrentOnboardingStep(ONBOARDING_QUESTIONS.length)
          
          // Start with welcome message
          const welcomeMessage = {
            id: 1,
            role: 'assistant',
            content: "Hello! I'm your Learning Coach. I'm here to help you truly understand concepts through thoughtful questions and guidance. What would you like to learn about today?",
            timestamp: new Date()
          }
          setMessages([welcomeMessage])
          return
        }
      } catch (e) {
        console.error('Error parsing stored onboarding data:', e)
        // If parsing fails, show onboarding
      }
    }
    
    // If we reach here, show onboarding (new session or incomplete data)
    
    // Start onboarding - show first question
    const firstQuestion = ONBOARDING_QUESTIONS[0]
    const welcomeMsg = {
      id: 1,
      role: 'assistant',
      content: "Hello! I'm your Learning Coach. Before we start, let me get to know you better so I can personalize your learning experience.",
      timestamp: new Date()
    }
    let questionContent = `${firstQuestion.question}\n\n${firstQuestion.description}`
    // Don't add numbered list for choice questions - buttons will show
    
    // Get options for first question
    let firstQuestionOptions = null
    if (firstQuestion.type === 'choice' || firstQuestion.type === 'choice-with-text') {
      firstQuestionOptions = firstQuestion.options
    } else if (firstQuestion.type === 'choice-with-text-dynamic' && firstQuestion.getOptions) {
      firstQuestionOptions = firstQuestion.getOptions('')
    }
    
    const questionMsg = {
      id: 2,
      role: 'assistant',
      content: questionContent,
      timestamp: new Date(),
      isOnboardingQuestion: true,
      onboardingStep: 0,
      questionType: firstQuestion.type,
      options: firstQuestionOptions
    }
    setMessages([welcomeMsg, questionMsg])
    setCurrentOnboardingStep(0)
    
    // Save initial messages to conversation history
    const saveInitialMessages = async () => {
      try {
        // Save welcome message
        await fetch('http://localhost:8000/api/chat/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            role: 'assistant',
            content: welcomeMsg.content,
            is_onboarding: true
          })
        })
        // Save first question
        await fetch('http://localhost:8000/api/chat/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            role: 'assistant',
            content: questionContent,
            is_onboarding: true
          })
        })
      } catch (e) {
        console.error('Error saving initial messages:', e)
      }
    }
    saveInitialMessages()
  }, [sessionId])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, currentResponse])

  const handleOnboardingAnswer = async (answer) => {
    const currentQuestion = ONBOARDING_QUESTIONS[currentOnboardingStep]
    
    // Handle answer - could be value (from click) or label (from typing)
    let answerValue = answer
    let answerLabel = answer
    
    if (currentQuestion.type === 'choice' || currentQuestion.type === 'choice-with-text' || currentQuestion.type === 'choice-with-text-dynamic') {
      // Find the option that matches
      if (currentQuestion.options) {
        const option = currentQuestion.options.find(opt => {
          if (typeof opt === 'string') {
            return opt.toLowerCase() === answer.toLowerCase()
          } else {
            // Special handling for consent (boolean values)
            if (currentQuestion.field === 'consent' && typeof opt.value === 'boolean') {
              if (typeof answer === 'boolean') {
                return opt.value === answer
              }
              // Check if answer matches label
              const lowerAnswer = answer.toLowerCase()
              const lowerLabel = opt.label.toLowerCase()
              return lowerLabel.includes(lowerAnswer) || 
                     lowerAnswer.includes('yes') && opt.value === true ||
                     lowerAnswer.includes('no') && opt.value === false ||
                     lowerAnswer.includes('y') && opt.value === true ||
                     lowerAnswer.includes('n') && opt.value === false
            }
            // For other options, check value and label
            return opt.value.toLowerCase() === answer.toLowerCase() || 
                   opt.label.toLowerCase() === answer.toLowerCase() ||
                   opt.label === answer ||
                   answer.toLowerCase().includes(opt.label.toLowerCase().split(' ')[0])
          }
        })
        
        if (option) {
          if (typeof option === 'string') {
            answerValue = option
            answerLabel = option
          } else {
            answerValue = option.value
            answerLabel = option.label
          }
        }
      }
      // If no match found and it's choice-with-text or dynamic, use the typed answer as-is
      if ((currentQuestion.type === 'choice-with-text' || currentQuestion.type === 'choice-with-text-dynamic') && answerValue === answer) {
        // User typed something custom, keep it
        answerValue = answer
        answerLabel = answer
      }
      // For consent, handle Yes/No strings if no button was clicked
      if (currentQuestion.field === 'consent' && typeof answerValue === 'string' && answerValue === answer) {
        const lowerAnswer = answer.toLowerCase()
        if (lowerAnswer.includes('yes') || lowerAnswer.includes('ok') || lowerAnswer.includes('y') || lowerAnswer === 'true') {
          answerValue = true
          answerLabel = 'Yes - Remember our conversation'
        } else if (lowerAnswer.includes('no') || lowerAnswer.includes('n') || lowerAnswer === 'false') {
          answerValue = false
          answerLabel = 'No - Don\'t remember'
        }
      }
    }
    
    // Add user's answer as a message (show the label)
    const userAnswer = {
      id: Date.now(),
      role: 'user',
      content: answerLabel,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userAnswer])
    
    // Store answer in onboarding data (use the value)
    const updatedData = { ...onboardingData }
    if (currentQuestion.field === 'preferredStyle') {
      updatedData[currentQuestion.field] = answerValue
    } else if (currentQuestion.field === 'consent') {
      // Handle consent - can be boolean from button click or string from typing
      if (typeof answerValue === 'boolean') {
        updatedData[currentQuestion.field] = answerValue
      } else if (typeof answerValue === 'string') {
        updatedData[currentQuestion.field] = answerValue.toLowerCase().includes('yes') || 
                                             answerValue.toLowerCase().includes('ok') ||
                                             answerValue === 'true'
      } else {
        updatedData[currentQuestion.field] = false
      }
    } else if (currentQuestion.field === 'interests') {
      // For interests, accumulate answers (can select multiple or type custom)
      // But move to next question after first answer (can be improved later for multiple selections)
      updatedData[currentQuestion.field] = answerValue
    } else {
      updatedData[currentQuestion.field] = answerValue
    }
    setOnboardingData(updatedData)
    
    // Save answer to conversation history immediately
    try {
      await fetch('http://localhost:8000/api/chat/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          role: 'user',
          content: answer,
          is_onboarding: true
        })
      })
    } catch (e) {
      console.error('Error saving onboarding answer:', e)
    }
    
    // Also save the question if it's the first question
    if (currentOnboardingStep === 0) {
      const welcomeMsg = messages[0]
      if (welcomeMsg) {
        try {
          await fetch('http://localhost:8000/api/chat/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: sessionId,
              role: 'assistant',
              content: welcomeMsg.content,
              is_onboarding: true
            })
          })
        } catch (e) {
          console.error('Error saving welcome message:', e)
        }
      }
    }
    
    // Save the question message
    const questionMsg = messages[messages.length - 1]
    if (questionMsg && questionMsg.isOnboardingQuestion) {
      try {
        await fetch('http://localhost:8000/api/chat/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            role: 'assistant',
            content: questionMsg.content,
            is_onboarding: true
          })
        })
      } catch (e) {
        console.error('Error saving question message:', e)
      }
    }
    
    // Move to next question or complete onboarding
    const nextStep = currentOnboardingStep + 1
    
    if (nextStep < ONBOARDING_QUESTIONS.length) {
      // Show next question
      const nextQuestion = ONBOARDING_QUESTIONS[nextStep]
      let questionContent = `${nextQuestion.question}\n\n${nextQuestion.description}`
      // Don't add numbered list - buttons will show for choice questions
      
      // Get dynamic options if needed
      let questionOptions = null
      if (nextQuestion.type === 'choice' || nextQuestion.type === 'choice-with-text') {
        questionOptions = nextQuestion.options
      } else if (nextQuestion.type === 'choice-with-text-dynamic' && nextQuestion.getOptions) {
        // Get options based on previous answer (interests)
        const interestsAnswer = updatedData.interests || ''
        questionOptions = nextQuestion.getOptions(interestsAnswer)
      }
      
      const nextQuestionMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: questionContent,
        timestamp: new Date(),
        isOnboardingQuestion: true,
        onboardingStep: nextStep,
        questionType: nextQuestion.type,
        options: questionOptions
      }
      setMessages(prev => [...prev, nextQuestionMsg])
      setCurrentOnboardingStep(nextStep)
      
      // Save question to conversation history
      try {
        await fetch('http://localhost:8000/api/chat/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            role: 'assistant',
            content: questionContent,
            is_onboarding: true
          })
        })
      } catch (e) {
        console.error('Error saving question message:', e)
      }
    } else {
      // Onboarding complete
      setOnboardingComplete(true)
      
      // Save onboarding data to backend
      try {
        await fetch('http://localhost:8000/api/onboarding/consent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            consent: updatedData.consent,
            onboarding_data: updatedData
          })
        })
        
        // Save to localStorage
        localStorage.setItem('learning_coach_onboarding_data', JSON.stringify(updatedData))
        localStorage.setItem('learning_coach_onboarding_complete', 'true')
        localStorage.setItem('learning_coach_consent', String(updatedData.consent))
      } catch (e) {
        console.error('Error saving onboarding data:', e)
      }
      
      // Show personalized welcome message based on onboarding data
      let welcomeContent = "Perfect! Now I understand your learning style and goals. "
      
      // Reference their interests/goals from onboarding
      if (updatedData.interests) {
        welcomeContent += `I see you're interested in ${updatedData.interests}. `
      }
      if (updatedData.goals) {
        welcomeContent += `Your goal is to ${updatedData.goals.toLowerCase()}. `
      }
      
      // Add personalized opening based on their learning style
      if (updatedData.preferredStyle === 'visual') {
        welcomeContent += "Since you prefer visual learning, I'll use examples, diagrams, and visual descriptions to help you understand concepts. "
      } else if (updatedData.preferredStyle === 'hands-on') {
        welcomeContent += "Since you prefer hands-on learning, I'll provide practice exercises and encourage you to try things yourself. "
      } else if (updatedData.preferredStyle === 'theoretical') {
        welcomeContent += "Since you prefer theoretical learning, I'll explain concepts and principles first before diving into examples. "
      } else if (updatedData.preferredStyle === 'mixed') {
        welcomeContent += "Since you prefer a mixed approach, I'll combine visual examples, hands-on practice, and theoretical explanations. "
      }
      
      // Add closing with suggestions
      if (updatedData.interests && updatedData.goals) {
        welcomeContent += `Let's start learning about ${updatedData.interests} and work towards ${updatedData.goals.toLowerCase()}.`
      } else if (updatedData.interests) {
        welcomeContent += `Let's start learning about ${updatedData.interests}.`
      } else if (updatedData.goals) {
        welcomeContent += `Let's work towards ${updatedData.goals.toLowerCase()}.`
      }
      
      // Add suggestions
      const suggestions = getLearningSuggestions(
        updatedData.interests,
        updatedData.goals,
        updatedData.learningLevel
      )
      
      if (suggestions.length > 0) {
        welcomeContent += '\n\nHere are some suggestions to get started:'
      } else {
        welcomeContent += " What would you like to explore first?"
      }
      
      const welcomeMsg = {
        id: Date.now() + 2,
        role: 'assistant',
        content: welcomeContent,
        timestamp: new Date(),
        options: suggestions.length > 0 ? suggestions : null,
        isOnboardingQuestion: false
      }
      setMessages(prev => [...prev, welcomeMsg])
      
      // Save welcome message to history
      try {
        await fetch('http://localhost:8000/api/chat/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            role: 'assistant',
            content: welcomeMsg.content,
            is_onboarding: false
          })
        })
      } catch (e) {
        console.error('Error saving welcome message:', e)
      }
    }
  }

  const handleSendMessage = async (message) => {
    if (!message.trim() || isLoading) return

    // If still in onboarding, handle as onboarding answer
    if (!onboardingComplete && currentOnboardingStep < ONBOARDING_QUESTIONS.length) {
      handleOnboardingAnswer(message)
      return
    }

    // Normal chat flow
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setCurrentResponse('')

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedResponse = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              // Response complete
              if (accumulatedResponse) {
                const assistantMessage = {
                  id: Date.now() + 1,
                  role: 'assistant',
                  content: accumulatedResponse,
                  timestamp: new Date()
                }
                setMessages(prev => [...prev, assistantMessage])
                setCurrentResponse('')
              }
              setIsLoading(false)
              return
            } else if (data) {
              accumulatedResponse += data
              setCurrentResponse(accumulatedResponse)
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error)
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: "I'm sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
      setIsLoading(false)
      setCurrentResponse('')
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="header-content">
          <img src="/sk_logo.png" alt="SK Logo" className="header-logo" />
          <div className="header-text-container">
            <h2>Learning Coach</h2>
            <p className="header-subtitle">Your AI learning companion</p>
          </div>
        </div>
      </div>
      
      <MessageList 
        messages={messages} 
        currentResponse={currentResponse}
        isLoading={isLoading}
        messagesEndRef={messagesEndRef}
        onOptionSelect={!onboardingComplete && currentOnboardingStep < ONBOARDING_QUESTIONS.length 
          ? handleOnboardingAnswer 
          : (option) => handleSendMessage(option)}
      />
      
      <MessageInput 
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        placeholder={
          !onboardingComplete && currentOnboardingStep < ONBOARDING_QUESTIONS.length
            ? (ONBOARDING_QUESTIONS[currentOnboardingStep]?.placeholder || "Type your answer or click options above...")
            : isLoading 
              ? "Learning Coach is thinking..." 
              : "Type your message..."
        }
        disabled={false}
      />
    </div>
  )
}

export default ChatInterface
