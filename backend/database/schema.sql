-- Learning Coach Database Schema for Supabase PostgreSQL
-- This replaces Redis with persistent PostgreSQL storage

-- Table 1: User Sessions
-- Stores session IDs and consent flags
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    has_consent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_created_at ON user_sessions(created_at);

-- Table 2: User Profiles
-- Stores onboarding/profile data
CREATE TABLE IF NOT EXISTS user_profiles (
    session_id VARCHAR(255) PRIMARY KEY REFERENCES user_sessions(session_id) ON DELETE CASCADE,
    learning_level VARCHAR(50),  -- Beginner/Intermediate/Advanced
    interests TEXT,
    goals TEXT,
    preferred_style VARCHAR(50),  -- visual/hands-on/theoretical/mixed
    profile_data JSONB,  -- Store full onboarding data as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_session_id ON user_profiles(session_id);

-- Table 3: Conversation History
-- Stores chat messages
CREATE TABLE IF NOT EXISTS conversation_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES user_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_history(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_conversation_created ON conversation_history(created_at);

-- Table 4: Learning Patterns
-- Stores learning analytics and patterns (NEW feature)
CREATE TABLE IF NOT EXISTS learning_patterns (
    session_id VARCHAR(255) PRIMARY KEY REFERENCES user_sessions(session_id) ON DELETE CASCADE,
    topics_learned JSONB DEFAULT '[]'::jsonb,  -- Array of topics discussed
    learning_pace VARCHAR(20),  -- slow/medium/fast
    strengths JSONB DEFAULT '[]'::jsonb,  -- Topics user excels at
    struggles JSONB DEFAULT '[]'::jsonb,  -- Topics user struggles with
    preferred_question_types JSONB DEFAULT '[]'::jsonb,  -- Types of questions that work best
    interaction_count INTEGER DEFAULT 0,  -- Total number of interactions
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_learning_patterns_session_id ON learning_patterns(session_id);
CREATE INDEX IF NOT EXISTS idx_learning_patterns_last_updated ON learning_patterns(last_updated);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_user_sessions_updated_at BEFORE UPDATE ON user_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_patterns_updated_at BEFORE UPDATE ON learning_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

