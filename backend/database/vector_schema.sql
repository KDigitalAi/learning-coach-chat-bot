-- Vector Storage Schema for Learning Styles using Supabase pgvector
-- This enables vector embeddings storage directly in PostgreSQL

-- Enable pgvector extension (run this first in Supabase SQL Editor)
CREATE EXTENSION IF NOT EXISTS vector;

-- Table for storing learning style vectors
CREATE TABLE IF NOT EXISTS learning_style_vectors (
    session_id VARCHAR(255) PRIMARY KEY REFERENCES user_sessions(session_id) ON DELETE CASCADE,
    learning_level VARCHAR(50),
    interests TEXT,
    goals TEXT,
    preferred_style VARCHAR(50),
    style_text TEXT,  -- Full text representation of learning style
    embedding vector(1536),  -- OpenAI text-embedding-3-small produces 1536-dimensional vectors
    onboarding_data JSONB,  -- Store full onboarding data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_learning_style_vectors_embedding 
ON learning_style_vectors 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for faster lookups by session_id
CREATE INDEX IF NOT EXISTS idx_learning_style_vectors_session 
ON learning_style_vectors(session_id);

-- Index for filtering by learning style
CREATE INDEX IF NOT EXISTS idx_learning_style_vectors_style 
ON learning_style_vectors(preferred_style);

