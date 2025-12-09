/**
 * Generate personalized learning suggestions based on onboarding data
 */
export function getLearningSuggestions(interests, goals, learningLevel) {
  const interest = (interests || '').toLowerCase()
  const goal = (goals || '').toLowerCase()
  const level = learningLevel || 'Beginner'
  
  const suggestions = []
  
  // Python Programming suggestions
  if (interest.includes('python')) {
    if (goal.includes('api') || goal.includes('web application')) {
      suggestions.push(
        'Let\'s explore REST APIs and how they work',
        'We could start with Flask or FastAPI frameworks',
        'We might begin with setting up your development environment',
        'Let\'s learn about HTTP methods and request/response handling'
      )
    } else if (goal.includes('data analysis') || goal.includes('data')) {
      suggestions.push(
        'Let\'s start with pandas for data manipulation',
        'We could explore data visualization with matplotlib',
        'We might begin with reading and analyzing CSV files',
        'Let\'s learn about data cleaning and preprocessing'
      )
    } else if (goal.includes('automation')) {
      suggestions.push(
        'Let\'s start with file operations and system automation',
        'We could explore web scraping with BeautifulSoup',
        'We might begin with scheduling tasks',
        'Let\'s learn about working with APIs for automation'
      )
    } else {
      suggestions.push(
        'Let\'s start with Python basics: variables, data types, and functions',
        'We could explore object-oriented programming concepts',
        'We might begin with understanding control flow and loops',
        'Let\'s learn about working with Python libraries and packages'
      )
    }
  }
  
  // Machine Learning/AI suggestions
  if (interest.includes('machine learning') || interest.includes('ai') || interest.includes('ml')) {
    if (goal.includes('model') || goal.includes('neural network')) {
      suggestions.push(
        'Let\'s start with understanding supervised vs unsupervised learning',
        'We could explore linear regression and classification',
        'We might begin with data preprocessing for ML',
        'Let\'s learn about training and testing machine learning models'
      )
    } else if (goal.includes('chatbot') || goal.includes('nlp')) {
      suggestions.push(
        'Let\'s start with natural language processing basics',
        'We could explore text preprocessing and tokenization',
        'We might begin with understanding language models',
        'Let\'s learn about building conversational AI'
      )
    } else if (goal.includes('computer vision') || goal.includes('vision')) {
      suggestions.push(
        'Let\'s start with image processing fundamentals',
        'We could explore convolutional neural networks (CNNs)',
        'We might begin with image classification',
        'Let\'s learn about object detection and recognition'
      )
    } else {
      suggestions.push(
        'Let\'s start with understanding what machine learning is',
        'We could explore different types of ML algorithms',
        'We might begin with data preparation for ML',
        'Let\'s learn about evaluating model performance'
      )
    }
  }
  
  // JavaScript/Web Development suggestions
  if (interest.includes('javascript') || interest.includes('web development')) {
    if (goal.includes('full-stack') || goal.includes('web application')) {
      suggestions.push(
        'Let\'s start with understanding frontend vs backend',
        'We could explore React or Vue.js for frontend',
        'We might begin with Node.js and Express for backend',
        'Let\'s learn about connecting frontend to backend'
      )
    } else if (goal.includes('api') || goal.includes('rest')) {
      suggestions.push(
        'Let\'s start with understanding REST API principles',
        'We could explore Express.js for building APIs',
        'We might begin with HTTP methods and routing',
        'Let\'s learn about API authentication and security'
      )
    } else {
      suggestions.push(
        'Let\'s start with JavaScript fundamentals: variables, functions, and objects',
        'We could explore DOM manipulation',
        'We might begin with async programming and promises',
        'Let\'s learn about modern JavaScript features (ES6+)'
      )
    }
  }
  
  // Data Science suggestions
  if (interest.includes('data science')) {
    if (goal.includes('analysis') || goal.includes('insights')) {
      suggestions.push(
        'Let\'s start with exploratory data analysis',
        'We could explore statistical concepts and hypothesis testing',
        'We might begin with data cleaning and preprocessing',
        'Let\'s learn about data visualization techniques'
      )
    } else if (goal.includes('model') || goal.includes('predictive')) {
      suggestions.push(
        'Let\'s start with building predictive models',
        'We could explore regression and classification techniques',
        'We might begin with feature engineering',
        'Let\'s learn about model evaluation metrics'
      )
    } else {
      suggestions.push(
        'Let\'s start with understanding the data science workflow',
        'We could explore data collection and preparation',
        'We might begin with statistical analysis',
        'Let\'s learn about data visualization and storytelling'
      )
    }
  }
  
  // Default suggestions if no specific match
  if (suggestions.length === 0) {
    if (level === 'Beginner') {
      suggestions.push(
        'Let\'s start with the fundamentals and basic concepts',
        'We could explore simple examples to build understanding',
        'We might begin with setting up your learning environment',
        'Let\'s learn about the core principles step by step'
      )
    } else if (level === 'Intermediate') {
      suggestions.push(
        'Let\'s build on your existing knowledge',
        'We could explore more advanced concepts',
        'We might begin with practical projects',
        'Let\'s learn about best practices and patterns'
      )
    } else {
      suggestions.push(
        'Let\'s dive into advanced topics',
        'We could explore complex concepts and architectures',
        'We might begin with optimization and performance',
        'Let\'s learn about industry best practices'
      )
    }
  }
  
  // Return 3-4 suggestions
  return suggestions.slice(0, 4)
}


