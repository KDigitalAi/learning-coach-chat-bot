-- RPC Functions for Vector Storage Operations
-- Run this in Supabase SQL Editor after creating the vector_schema.sql tables

-- Function to store learning style vector
CREATE OR REPLACE FUNCTION store_learning_style_vector(
    p_session_id VARCHAR(255),
    p_learning_level VARCHAR(50),
    p_interests TEXT,
    p_goals TEXT,
    p_preferred_style VARCHAR(50),
    p_style_text TEXT,
    p_embedding vector(1536),
    p_onboarding_data JSONB
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO learning_style_vectors (
        session_id,
        learning_level,
        interests,
        goals,
        preferred_style,
        style_text,
        embedding,
        onboarding_data,
        updated_at
    )
    VALUES (
        p_session_id,
        p_learning_level,
        p_interests,
        p_goals,
        p_preferred_style,
        p_style_text,
        p_embedding,
        p_onboarding_data,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (session_id)
    DO UPDATE SET
        learning_level = EXCLUDED.learning_level,
        interests = EXCLUDED.interests,
        goals = EXCLUDED.goals,
        preferred_style = EXCLUDED.preferred_style,
        style_text = EXCLUDED.style_text,
        embedding = EXCLUDED.embedding,
        onboarding_data = EXCLUDED.onboarding_data,
        updated_at = CURRENT_TIMESTAMP;
END;
$$;

-- Function to search similar learning styles using vector similarity
CREATE OR REPLACE FUNCTION search_similar_learning_styles(
    p_query_embedding vector(1536),
    p_limit INTEGER DEFAULT 3
)
RETURNS TABLE (
    session_id VARCHAR(255),
    learning_level VARCHAR(50),
    interests TEXT,
    goals TEXT,
    preferred_style VARCHAR(50),
    style_text TEXT,
    similarity_score FLOAT,
    onboarding_data JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        lsv.session_id,
        lsv.learning_level,
        lsv.interests,
        lsv.goals,
        lsv.preferred_style,
        lsv.style_text,
        1 - (lsv.embedding <=> p_query_embedding) AS similarity_score,
        lsv.onboarding_data
    FROM learning_style_vectors lsv
    ORDER BY lsv.embedding <=> p_query_embedding
    LIMIT p_limit;
END;
$$;

