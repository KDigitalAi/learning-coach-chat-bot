// API Configuration
// For local development: use FastAPI server on port 8000
// For production/Vercel: use same origin
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : window.location.origin;

// Session Management
let sessionId = null;
let onboardingData = {
    learningLevel: '',
    interests: '',
    goals: '',
    preferredStyle: '',
    consent: false
};
let currentOnboardingStep = 0;
let onboardingComplete = false;
let isProcessingOnboarding = false;

// Onboarding Questions
const ONBOARDING_QUESTIONS = [
    {
        question: "What's your current learning level?",
        field: 'learningLevel',
        expectedAnswers: ['beginner', 'intermediate', 'advanced'],
        suggestions: ['Beginner', 'Intermediate', 'Advanced']
    },
    {
        question: "What topics are you interested in learning?",
        field: 'interests',
        suggestions: ['Python Programming', 'Web Development', 'Data Science', 'Machine Learning', 'FastAPI', 'JavaScript']
    },
    {
        question: "What are your learning goals?",
        field: 'goals',
        suggestions: ['Build web applications', 'Learn programming fundamentals', 'Master a specific framework', 'Prepare for interviews', 'Build a portfolio project']
    },
    {
        question: "How do you prefer to learn?",
        field: 'preferredStyle',
        expectedAnswers: ['hands-on', 'theoretical', 'mixed'],
        suggestions: ['Hands-on (learning by doing)', 'Theoretical (understanding concepts first)', 'Mixed (combination of both)']
    },
    {
        question: "To provide the best personalized learning experience, I can remember our conversation during this session. Would you like me to remember our conversation?",
        field: 'consent',
        expectedAnswers: ['yes', 'no'],
        suggestions: ['Yes - Remember our conversation', 'No - Don\'t remember']
    }
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeSession();
    setupEventListeners();
    checkBackendConnection();
    checkOnboardingStatus();
});

// Check Backend Connection
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            console.log('✅ Backend is connected');
        } else {
            console.warn('⚠️ Backend health check failed');
        }
    } catch (error) {
        console.error('❌ Backend is not running. Please start it with: cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload');
        // Don't show error to user yet - they might start it later
    }
}

// Initialize Session
function initializeSession() {
    sessionId = localStorage.getItem('learning_coach_session_id');
    if (!sessionId) {
        sessionId = crypto.randomUUID();
        localStorage.setItem('learning_coach_session_id', sessionId);
    }
}

// Check if onboarding is already completed
function checkOnboardingStatus() {
    const consent = localStorage.getItem('learning_coach_consent');
    const storedData = localStorage.getItem('learning_coach_onboarding_data');
    
    if (consent === 'true' && storedData) {
        try {
            const parsedData = JSON.parse(storedData);
            if (parsedData.learningLevel && parsedData.preferredStyle) {
                onboardingData = parsedData;
                onboardingComplete = true;
                showChatInterface();
                addWelcomeMessage();
                return;
            }
        } catch (e) {
            console.error('Error parsing stored data:', e);
        }
    }
    
    // Show chat interface and start onboarding
    showChatInterface();
    startOnboarding();
}

// Show Chat Interface
function showChatInterface() {
    const onboardingSection = document.getElementById('onboarding-section');
    const chatSection = document.getElementById('chat-section');
    
    if (onboardingSection) {
        onboardingSection.style.display = 'none';
    }
    if (chatSection) {
        chatSection.style.display = 'block';
    }
}

// Start Onboarding in Chat
function startOnboarding() {
    if (currentOnboardingStep >= ONBOARDING_QUESTIONS.length) {
        completeOnboarding();
        return;
    }
    
    const question = ONBOARDING_QUESTIONS[currentOnboardingStep];
    let questionText = question.question;
    
    if (currentOnboardingStep === 0) {
        questionText = "Hello! I'm your Learning Coach. I'm here to help you truly understand concepts through thoughtful questions and guidance.\n\n" + questionText;
    }
    
    // Add suggestions if available
    if (question.suggestions && question.suggestions.length > 0) {
        questionText += "\n\nYou can choose from these options or type your own answer:";
    }
    
    const messageId = addMessage('assistant', questionText);
    
    // Add suggestion buttons
    if (question.suggestions && question.suggestions.length > 0) {
        addSuggestionButtons(messageId, question);
    }
    
    isProcessingOnboarding = true;
}

// Setup Event Listeners
function setupEventListeners() {
    const sendButton = document.getElementById('send-button');
    const messageInput = document.getElementById('message-input');
    
    if (sendButton) {
        sendButton.addEventListener('click', handleSendMessage);
    }
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });
    }
}

// Handle Send Message
async function handleSendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (!message || messageInput.disabled) return;
    
    // Add user message
    addMessage('user', message);
    messageInput.value = '';
    messageInput.disabled = true;
    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        sendButton.disabled = true;
    }
    
    // Handle onboarding
    if (isProcessingOnboarding && !onboardingComplete) {
        handleOnboardingAnswer(message);
        messageInput.disabled = false;
        if (sendButton) {
            sendButton.disabled = false;
        }
        return;
    }
    
    // Show typing indicator
    const typingId = addMessage('assistant', '...', true);
    
    try {
        // Send message to API
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        if (!response.ok) {
            // Check if response is HTML (error page)
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('text/html')) {
                const htmlText = await response.text();
                console.error('Server returned HTML:', htmlText.substring(0, 500));
                throw new Error('Server returned HTML instead of JSON. The API endpoint may not be configured correctly. Check Vercel deployment.');
            }
            
            // Try to get error message from response
            let errorMessage = `Failed to get response: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.json();
                if (errorData.error || errorData.message) {
                    errorMessage = errorData.error || errorData.message;
                }
            } catch (e) {
                // Response is not JSON, use status text
            }
            throw new Error(errorMessage);
        }
        
        // Remove typing indicator
        removeMessage(typingId);
        
        // Handle SSE streaming
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedResponse = '';
        const assistantMessageId = addMessage('assistant', '');
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        // Response complete
                        updateMessage(assistantMessageId, accumulatedResponse);
                        messageInput.disabled = false;
                        if (sendButton) {
                            sendButton.disabled = false;
                        }
                        messageInput.focus();
                        return;
                    } else if (data) {
                        accumulatedResponse += data;
                        updateMessage(assistantMessageId, accumulatedResponse);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error:', error);
        removeMessage(typingId);
        
        // Better error messages
        let errorMessage = "I'm sorry, I encountered an error. ";
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMessage += "I can't connect to the server. Please make sure the backend is running on http://localhost:8000";
        } else {
            errorMessage += error.message;
        }
        errorMessage += " Please try again.";
        
        addMessage('assistant', errorMessage);
        messageInput.disabled = false;
        if (sendButton) {
            sendButton.disabled = false;
        }
    }
}

// Handle Onboarding Answer
function handleOnboardingAnswer(answer) {
    const question = ONBOARDING_QUESTIONS[currentOnboardingStep];
    let processedAnswer = answer.trim().toLowerCase();
    
    // Process answer based on question type
    if (question.expectedAnswers) {
        // Check if answer matches expected values
        const matched = question.expectedAnswers.find(exp => 
            processedAnswer.includes(exp) || exp.includes(processedAnswer)
        );
        if (matched) {
            processedAnswer = matched;
        }
    }
    
    // Special handling for consent
    if (question.field === 'consent') {
        processedAnswer = processedAnswer.includes('yes') || processedAnswer.includes('y');
    }
    
    // Special handling for learning level
    if (question.field === 'learningLevel') {
        if (processedAnswer.includes('beginner')) {
            processedAnswer = 'Beginner';
        } else if (processedAnswer.includes('intermediate')) {
            processedAnswer = 'Intermediate';
        } else if (processedAnswer.includes('advanced')) {
            processedAnswer = 'Advanced';
        } else {
            processedAnswer = 'Beginner'; // Default
        }
    }
    
    // Special handling for preferred style
    if (question.field === 'preferredStyle') {
        if (processedAnswer.includes('hands-on') || processedAnswer.includes('hands on')) {
            processedAnswer = 'hands-on';
        } else if (processedAnswer.includes('theoretical') || processedAnswer.includes('theory')) {
            processedAnswer = 'theoretical';
        } else if (processedAnswer.includes('mixed')) {
            processedAnswer = 'mixed';
        } else {
            processedAnswer = 'mixed'; // Default
        }
    }
    
    onboardingData[question.field] = processedAnswer;
    currentOnboardingStep++;
    
    if (currentOnboardingStep < ONBOARDING_QUESTIONS.length) {
        // Ask next question
        const nextQuestion = ONBOARDING_QUESTIONS[currentOnboardingStep];
        let nextQuestionText = nextQuestion.question;
        
        // Add suggestions if available
        if (nextQuestion.suggestions && nextQuestion.suggestions.length > 0) {
            nextQuestionText += "\n\nYou can choose from these options or type your own answer:";
        }
        
        const messageId = addMessage('assistant', nextQuestionText);
        
        // Add suggestion buttons
        if (nextQuestion.suggestions && nextQuestion.suggestions.length > 0) {
            addSuggestionButtons(messageId, nextQuestion);
        }
    } else {
        // Complete onboarding
        completeOnboarding();
    }
}

// Complete Onboarding
async function completeOnboarding() {
    isProcessingOnboarding = false;
    onboardingComplete = true;
    
    // Display onboarding summary in chat
    displayOnboardingSummary();
    
    // Create personalized welcome message based on their interests and goals
    let welcomeMessage = 'Perfect! I\'ve saved your preferences. ';
    
    if (onboardingData.interests) {
        welcomeMessage += `I see you're interested in ${onboardingData.interests}. `;
    }
    
    if (onboardingData.goals) {
        welcomeMessage += `Your goal is to ${onboardingData.goals.toLowerCase()}. `;
    }
    
    // Add learning style specific message
    if (onboardingData.preferredStyle === 'hands-on') {
        welcomeMessage += 'Since you prefer hands-on learning, I\'ll provide plenty of practice exercises and encourage you to try things yourself. ';
    } else if (onboardingData.preferredStyle === 'theoretical') {
        welcomeMessage += 'Since you prefer understanding concepts first, I\'ll explain the principles before diving into examples. ';
    } else if (onboardingData.preferredStyle === 'mixed') {
        welcomeMessage += 'I\'ll combine explanations, examples, and practice to match your mixed learning style. ';
    }
    
    welcomeMessage += 'Ready to start learning? Just ask me anything!';
    
    const welcomeMessageId = addMessage('assistant', welcomeMessage);
    
    // Add topic suggestions based on interests and goals - with delay to ensure message is rendered
    setTimeout(() => {
        addTopicSuggestions(welcomeMessageId);
    }, 300);
    
    try {
        // Save onboarding data to backend
        // IMPORTANT: Save onboarding data even if consent is false (we just won't save conversation history)
        const response = await fetch(`${API_BASE}/api/onboarding/consent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                consent: onboardingData.consent || false,
                onboarding_data: onboardingData
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                console.log('✅ Onboarding data saved successfully:', data);
                // Save to localStorage
                localStorage.setItem('learning_coach_consent', String(onboardingData.consent || false));
                localStorage.setItem('learning_coach_onboarding_data', JSON.stringify(onboardingData));
            } else {
                console.warn('⚠️ Onboarding save returned success=false:', data);
            }
        } else {
            // Try to get error message
            let errorText = `Failed to save: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.json();
                errorText = errorData.detail || errorData.error || errorText;
            } catch (e) {
                // Response is not JSON
            }
            console.error('❌ Error saving onboarding data:', errorText);
            addMessage('assistant', 'Note: Your preferences were saved locally. Some features may be limited.');
        }
    } catch (error) {
        console.error('❌ Error saving onboarding data:', error);
        addMessage('assistant', 'Note: Your preferences were saved locally. Some features may be limited.');
        // Save to localStorage anyway
        localStorage.setItem('learning_coach_consent', String(onboardingData.consent || false));
        localStorage.setItem('learning_coach_onboarding_data', JSON.stringify(onboardingData));
    }
}

// Display Onboarding Summary
function displayOnboardingSummary() {
    const messagesContainer = document.getElementById('messages-container');
    if (!messagesContainer) return;
    
    const messageId = 'msg-' + Date.now() + '-' + Math.random();
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = 'message assistant';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content onboarding-summary';
    contentDiv.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    contentDiv.style.color = 'white';
    contentDiv.style.padding = '1.5rem';
    contentDiv.style.borderRadius = '12px';
    contentDiv.style.maxWidth = '85%';
    
    let summaryHTML = '<div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">';
    summaryHTML += '<span>📋</span><span>Your Learning Profile</span></div>';
    summaryHTML += '<div style="background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 8px; display: flex; flex-direction: column; gap: 0.75rem;">';
    
    if (onboardingData.learningLevel) {
        summaryHTML += `<div style="display: flex; align-items: center; gap: 0.5rem;"><span style="font-weight: 600;">🎯 Level:</span><span>${onboardingData.learningLevel}</span></div>`;
    }
    
    if (onboardingData.interests) {
        summaryHTML += `<div style="display: flex; align-items: center; gap: 0.5rem;"><span style="font-weight: 600;">💡 Interests:</span><span>${onboardingData.interests}</span></div>`;
    }
    
    if (onboardingData.goals) {
        summaryHTML += `<div style="display: flex; align-items: center; gap: 0.5rem;"><span style="font-weight: 600;">🎓 Goals:</span><span>${onboardingData.goals}</span></div>`;
    }
    
    if (onboardingData.preferredStyle) {
        const styleLabels = {
            'hands-on': 'Hands-on (Learning by doing)',
            'theoretical': 'Theoretical (Understanding concepts first)',
            'mixed': 'Mixed (Combination of both)'
        };
        const styleLabel = styleLabels[onboardingData.preferredStyle] || onboardingData.preferredStyle;
        summaryHTML += `<div style="display: flex; align-items: center; gap: 0.5rem;"><span style="font-weight: 600;">✨ Style:</span><span>${styleLabel}</span></div>`;
    }
    
    if (onboardingData.consent !== undefined) {
        summaryHTML += `<div style="display: flex; align-items: center; gap: 0.5rem;"><span style="font-weight: 600;">💾 Memory:</span><span>${onboardingData.consent ? 'Enabled' : 'Disabled'}</span></div>`;
    }
    
    summaryHTML += '</div>';
    summaryHTML += '<div style="margin-top: 1rem; font-style: italic; opacity: 0.9;">I\'ll use this to personalize your learning experience!</div>';
    
    contentDiv.innerHTML = summaryHTML;
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Add Welcome Message
function addWelcomeMessage() {
    let welcomeText = "Hello! I'm your Learning Coach. I'm here to help you truly understand concepts through thoughtful questions and guidance.";
    
    if (onboardingData.interests) {
        welcomeText += ` I see you're interested in ${onboardingData.interests}.`;
    }
    if (onboardingData.goals) {
        welcomeText += ` Your goal is to ${onboardingData.goals.toLowerCase()}.`;
    }
    
    welcomeText += " What would you like to learn about today?";
    
    addMessage('assistant', welcomeText);
}

// Format inline markdown (bold, italic, etc.)
function formatInlineMarkdown(text) {
    if (!text) return '';
    
    let formatted = String(text);
    
    // Convert **bold** to <strong> (handle multiple occurrences)
    formatted = formatted.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *italic* to <em> (but not if it's part of **bold**)
    formatted = formatted.replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '<em>$1</em>');
    
    return formatted;
}

// Format message content (convert markdown-like formatting to HTML)
function formatMessageContent(content) {
    if (!content) return '';
    
    let text = String(content);
    
    // First, handle numbered lists that might be concatenated without proper spacing
    // Pattern: "text1. item2. item3. item" -> split into separate lines
    // This handles cases like "steps:1. Planning2. Design" etc.
    text = text.replace(/([^0-9])(\d+)\.\s*([A-Z][^0-9]+?)(?=\d+\.|$)/g, (match, before, num, item) => {
        // If there's text before, keep it, then add newline before the list item
        return before + '\n' + num + '. ' + item.trim();
    });
    
    // Also handle cases where list starts immediately after colon or period
    text = text.replace(/([:.])\s*(\d+)\.\s*([A-Z][^0-9]+?)(?=\d+\.|$)/g, (match, punct, num, item) => {
        return punct + '\n' + num + '. ' + item.trim();
    });
    
    const lines = text.split('\n');
    const processedLines = [];
    let inList = false;
    let listItems = [];
    let consecutiveEmptyLines = 0;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmedLine = line.trim();
        
        // Check if this is a numbered list item (1. 2. 3. etc.)
        // Match pattern: number followed by period, optional space, then content
        const listMatch = trimmedLine.match(/^(\d+)\.\s*(.+)$/);
        
        if (listMatch) {
            // If we were in a list, continue it
            if (!inList) {
                inList = true;
                listItems = [];
            }
            listItems.push(listMatch[2].trim());
            consecutiveEmptyLines = 0;
        } else {
            // If we were in a list, close it
            if (inList && listItems.length > 0) {
                const listHtml = '<ol>' + listItems.map(item => `<li>${formatInlineMarkdown(item)}</li>`).join('') + '</ol>';
                processedLines.push(listHtml);
                listItems = [];
                inList = false;
            }
            
            // Process regular line
            if (trimmedLine) {
                // Add spacing based on previous empty lines
                if (consecutiveEmptyLines > 0) {
                    // Multiple empty lines = paragraph break (more spacing)
                    processedLines.push('<br>');
                }
                processedLines.push(formatInlineMarkdown(trimmedLine));
                consecutiveEmptyLines = 0;
            } else {
                // Track consecutive empty lines for dynamic spacing
                consecutiveEmptyLines++;
                // Add spacing for empty lines (but not at the very end)
                if (i < lines.length - 1) {
                    // Single empty line = line break, multiple = paragraph break
                    if (consecutiveEmptyLines === 1) {
                        processedLines.push('<br>');
                    }
                }
            }
        }
    }
    
    // Close any remaining list
    if (inList && listItems.length > 0) {
        const listHtml = '<ol>' + listItems.map(item => `<li>${formatInlineMarkdown(item)}</li>`).join('') + '</ol>';
        processedLines.push(listHtml);
    }
    
    return processedLines.join('');
}

// Add Message
function addMessage(role, content, isTyping = false) {
    const messagesContainer = document.getElementById('messages-container');
    if (!messagesContainer) return null;
    
    const messageId = 'msg-' + Date.now() + '-' + Math.random();
    
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `message ${role} ${isTyping ? 'typing' : ''}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Format and set content
    if (isTyping) {
        contentDiv.textContent = content;
    } else {
        // Format markdown-like content
        const formattedContent = formatMessageContent(content);
        contentDiv.innerHTML = formattedContent;
    }
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageId;
}

// Update Message
function updateMessage(messageId, content) {
    const messageDiv = document.getElementById(messageId);
    if (messageDiv) {
        const contentDiv = messageDiv.querySelector('.message-content');
        if (contentDiv) {
            // Format markdown-like content
            const formattedContent = formatMessageContent(content);
            contentDiv.innerHTML = formattedContent;
            // Scroll to bottom
            const messagesContainer = document.getElementById('messages-container');
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }
    }
}

// Remove Message
function removeMessage(messageId) {
    const messageDiv = document.getElementById(messageId);
    if (messageDiv) {
        messageDiv.remove();
    }
}

// Add Topic Suggestions based on interests and goals
function addTopicSuggestions(messageId) {
    const messageDiv = document.getElementById(messageId);
    if (!messageDiv) {
        console.warn('Message div not found:', messageId);
        return;
    }
    
    // Find the message-content div
    const contentDiv = messageDiv.querySelector('.message-content');
    if (!contentDiv) {
        console.warn('Message content div not found in:', messageId);
        return;
    }
    
    // Generate suggestions based on interests and goals
    const suggestions = generateTopicSuggestions();
    
    if (suggestions.length === 0) {
        console.log('No suggestions generated for interests:', onboardingData.interests, 'goals:', onboardingData.goals);
        return;
    }
    
    console.log('Adding topic suggestions:', suggestions);
    
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'topic-suggestions-container';
    
    // Add header
    const header = document.createElement('div');
    header.style.marginBottom = '10px';
    header.style.fontSize = '0.85rem';
    header.style.color = '#888';
    header.style.fontWeight = '500';
    header.textContent = '💡 Suggested topics to explore:';
    suggestionsContainer.appendChild(header);
    
    // Create button container
    const buttonsContainer = document.createElement('div');
    buttonsContainer.style.display = 'flex';
    buttonsContainer.style.flexWrap = 'wrap';
    buttonsContainer.style.gap = '8px';
    
    suggestions.forEach((suggestion) => {
        const button = document.createElement('button');
        button.className = 'topic-suggestion-button';
        button.textContent = suggestion;
        button.type = 'button';
        
        // Click handler - send the suggestion as a message
        button.onclick = () => {
            const messageInput = document.getElementById('message-input');
            if (messageInput) {
                messageInput.value = suggestion;
                // Trigger send
                handleSendMessage();
            }
        };
        
        buttonsContainer.appendChild(button);
    });
    
    suggestionsContainer.appendChild(buttonsContainer);
    contentDiv.appendChild(suggestionsContainer);
    
    console.log('✅ Topic suggestions added to message:', messageId);
    
    // Scroll to bottom
    const messagesContainer = document.getElementById('messages-container');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Generate topic suggestions based on interests and goals
function generateTopicSuggestions() {
    const suggestions = [];
    const interests = (onboardingData.interests || '').toLowerCase();
    const goals = (onboardingData.goals || '').toLowerCase();
    
    // Data Science suggestions
    if (interests.includes('data science') || interests.includes('data') || interests.includes('science')) {
        suggestions.push('What is data science?');
        suggestions.push('How to analyze data with Python?');
        suggestions.push('Introduction to machine learning');
        suggestions.push('Data visualization basics');
    }
    
    // Web Development suggestions
    if (interests.includes('web') || interests.includes('development') || goals.includes('web') || goals.includes('application')) {
        suggestions.push('How to build a web application?');
        suggestions.push('What is FastAPI?');
        suggestions.push('Frontend vs Backend explained');
        suggestions.push('REST API basics');
    }
    
    // Python suggestions
    if (interests.includes('python') || goals.includes('python')) {
        suggestions.push('Python fundamentals');
        suggestions.push('How do Python functions work?');
        suggestions.push('Object-oriented programming in Python');
    }
    
    // JavaScript suggestions
    if (interests.includes('javascript') || interests.includes('js')) {
        suggestions.push('JavaScript basics');
        suggestions.push('How does async/await work?');
        suggestions.push('DOM manipulation explained');
    }
    
    // General programming suggestions if no specific match
    if (suggestions.length === 0) {
        if (onboardingData.learningLevel === 'Beginner') {
            suggestions.push('What is programming?');
            suggestions.push('How do variables work?');
            suggestions.push('Understanding functions');
        } else {
            suggestions.push('How to build a project?');
            suggestions.push('Best practices in coding');
            suggestions.push('Understanding design patterns');
        }
    }
    
    // Limit to 4 suggestions
    return suggestions.slice(0, 4);
}

// Add Suggestion Buttons
function addSuggestionButtons(messageId, question) {
    if (!question.suggestions || question.suggestions.length === 0) {
        console.warn('No suggestions for question:', question.field);
        return;
    }
    
    // Use setTimeout to ensure the message is fully rendered
    setTimeout(() => {
        const messageDiv = document.getElementById(messageId);
        if (!messageDiv) {
            console.error('Message div not found:', messageId);
            return;
        }
        
        console.log('Adding suggestion buttons for:', question.field, question.suggestions);
        
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'suggestions-container';
        suggestionsContainer.style.marginTop = '10px';
        suggestionsContainer.style.display = 'flex';
        suggestionsContainer.style.flexWrap = 'wrap';
        suggestionsContainer.style.gap = '8px';
        
        question.suggestions.forEach((suggestion, index) => {
            const button = document.createElement('button');
            button.className = 'suggestion-button';
            button.textContent = suggestion;
            button.type = 'button'; // Prevent form submission
            button.style.padding = '8px 16px';
            button.style.border = '1px solid #ddd';
            button.style.borderRadius = '20px';
            button.style.backgroundColor = '#f5f5f5';
            button.style.cursor = 'pointer';
            button.style.fontSize = '14px';
            button.style.color = '#333';
            button.style.transition = 'all 0.2s ease';
            button.style.fontFamily = 'inherit';
            
            // Hover effect
            button.onmouseenter = () => {
                button.style.backgroundColor = '#667eea';
                button.style.color = 'white';
                button.style.borderColor = '#667eea';
            };
            button.onmouseleave = () => {
                button.style.backgroundColor = '#f5f5f5';
                button.style.color = '#333';
                button.style.borderColor = '#ddd';
            };
            
            // Click handler
            button.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // Extract the actual value from the suggestion text
                let value = suggestion;
                
                // For learning level
                if (question.field === 'learningLevel') {
                    if (suggestion.includes('Beginner')) value = 'Beginner';
                    else if (suggestion.includes('Intermediate')) value = 'Intermediate';
                    else if (suggestion.includes('Advanced')) value = 'Advanced';
                }
                
                // For preferred style
                if (question.field === 'preferredStyle') {
                    if (suggestion.toLowerCase().includes('hands-on')) value = 'hands-on';
                    else if (suggestion.toLowerCase().includes('theoretical')) value = 'theoretical';
                    else if (suggestion.toLowerCase().includes('mixed')) value = 'mixed';
                }
                
                // For consent
                if (question.field === 'consent') {
                    value = suggestion.toLowerCase().includes('yes') ? 'yes' : 'no';
                }
                
                // Fill in the input and trigger send
                const messageInput = document.getElementById('message-input');
                if (messageInput) {
                    messageInput.value = value;
                    // Remove all suggestion buttons after selection
                    const containers = document.querySelectorAll('.suggestions-container');
                    containers.forEach(container => container.remove());
                    // Auto-submit
                    handleOnboardingAnswer(value);
                }
            };
            
            suggestionsContainer.appendChild(button);
        });
        
        // Append to message content div (inside the message bubble)
        const contentDiv = messageDiv.querySelector('.message-content');
        if (contentDiv) {
            contentDiv.appendChild(suggestionsContainer);
            console.log('Suggestion buttons added to message:', messageId);
        } else {
            console.error('Message content div not found for:', messageId);
            // Fallback: append to message div
            messageDiv.appendChild(suggestionsContainer);
        }
        
        // Scroll to bottom
        const messagesContainer = document.getElementById('messages-container');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }, 50); // Small delay to ensure DOM is ready
}
