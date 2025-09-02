-- CodeCrafts MVP Database Initialization Script
-- This script sets up the initial database configuration for production

-- Create database if it doesn't exist (handled by Docker environment variables)
-- CREATE DATABASE codecrafts_prod;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('student', 'instructor', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE lesson_status AS ENUM ('draft', 'published', 'archived');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE progress_status AS ENUM ('not_started', 'in_progress', 'completed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE question_type AS ENUM ('mcq', 'fill_blank', 'code', 'flashcard');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE duel_status AS ENUM ('pending', 'active', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create functions for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create function to calculate user level from XP
CREATE OR REPLACE FUNCTION calculate_level(total_xp INTEGER)
RETURNS INTEGER AS $$
BEGIN
    -- Level calculation: 250 XP per level
    RETURN GREATEST(1, (total_xp / 250) + 1);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create function to update user level when XP changes
CREATE OR REPLACE FUNCTION update_user_level()
RETURNS TRIGGER AS $$
BEGIN
    NEW.level = calculate_level(NEW.total_xp);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create function for full-text search
CREATE OR REPLACE FUNCTION create_search_vector(title TEXT, description TEXT, content JSONB)
RETURNS tsvector AS $$
BEGIN
    RETURN to_tsvector('english', 
        COALESCE(title, '') || ' ' || 
        COALESCE(description, '') || ' ' ||
        COALESCE(content->>'theory', '') || ' ' ||
        COALESCE(array_to_string(ARRAY(SELECT jsonb_array_elements_text(content->'examples')), ' '), '')
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Performance optimization settings
-- These will be applied when the database starts

-- Logging configuration for production
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';

-- Memory and performance settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Connection settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';

-- Enable query statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Create indexes that will be used frequently
-- Note: These will be created by Alembic migrations, but we ensure they exist

-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_email_unique ON users(email) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_users_username_unique ON users(username) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_users_total_xp ON users(total_xp DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_users_level ON users(level DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Lesson indexes
CREATE INDEX IF NOT EXISTS idx_lessons_language ON lessons(language) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS idx_lessons_difficulty ON lessons(difficulty) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS idx_lessons_language_difficulty ON lessons(language, difficulty) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS idx_lessons_created_at ON lessons(created_at);

-- Question indexes
CREATE INDEX IF NOT EXISTS idx_questions_lesson_id ON questions(lesson_id);
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(type);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);

-- Progress indexes
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_lesson_id ON user_progress(lesson_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_status ON user_progress(status);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_lesson ON user_progress(user_id, lesson_id);

-- Question attempts indexes
CREATE INDEX IF NOT EXISTS idx_question_attempts_user_id ON question_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_question_attempts_question_id ON question_attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_question_attempts_created_at ON question_attempts(created_at);
CREATE INDEX IF NOT EXISTS idx_question_attempts_user_question ON question_attempts(user_id, question_id);

-- Achievement indexes
CREATE INDEX IF NOT EXISTS idx_achievements_user_id ON achievements(user_id);
CREATE INDEX IF NOT EXISTS idx_achievements_category ON achievements(category);
CREATE INDEX IF NOT EXISTS idx_achievements_unlocked_at ON achievements(unlocked_at);

-- Duel indexes
CREATE INDEX IF NOT EXISTS idx_duels_challenger_id ON duels(challenger_id);
CREATE INDEX IF NOT EXISTS idx_duels_opponent_id ON duels(opponent_id);
CREATE INDEX IF NOT EXISTS idx_duels_status ON duels(status);
CREATE INDEX IF NOT EXISTS idx_duels_created_at ON duels(created_at);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_lessons_search ON lessons USING gin(to_tsvector('english', title || ' ' || description));

-- Partial indexes for better performance
CREATE INDEX IF NOT EXISTS idx_active_users ON users(id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_published_lessons ON lessons(id) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS idx_completed_progress ON user_progress(user_id, completed_at) WHERE status = 'completed';

-- Create materialized view for leaderboard (for better performance)
CREATE MATERIALIZED VIEW IF NOT EXISTS leaderboard AS
SELECT 
    u.id,
    u.username,
    u.total_xp,
    u.level,
    u.streak,
    ROW_NUMBER() OVER (ORDER BY u.total_xp DESC, u.created_at ASC) as rank
FROM users u
WHERE u.is_active = true
ORDER BY u.total_xp DESC, u.created_at ASC;

-- Create unique index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_leaderboard_id ON leaderboard(id);
CREATE INDEX IF NOT EXISTS idx_leaderboard_rank ON leaderboard(rank);

-- Create function to refresh leaderboard
CREATE OR REPLACE FUNCTION refresh_leaderboard()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY leaderboard;
END;
$$ LANGUAGE plpgsql;

-- Create view for user statistics
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    u.total_xp,
    u.level,
    u.streak,
    COUNT(DISTINCT up.lesson_id) FILTER (WHERE up.status = 'completed') as lessons_completed,
    COUNT(DISTINCT qa.question_id) as questions_answered,
    COUNT(DISTINCT qa.question_id) FILTER (WHERE qa.is_correct = true) as correct_answers,
    CASE 
        WHEN COUNT(DISTINCT qa.question_id) > 0 
        THEN ROUND((COUNT(DISTINCT qa.question_id) FILTER (WHERE qa.is_correct = true)::numeric / COUNT(DISTINCT qa.question_id)) * 100, 1)
        ELSE 0 
    END as accuracy_percentage,
    COUNT(DISTINCT a.id) as achievements_unlocked,
    u.created_at as joined_date,
    MAX(GREATEST(up.updated_at, qa.created_at)) as last_activity
FROM users u
LEFT JOIN user_progress up ON u.id = up.user_id
LEFT JOIN question_attempts qa ON u.id = qa.user_id
LEFT JOIN achievements a ON u.id = a.user_id
WHERE u.is_active = true
GROUP BY u.id, u.username, u.total_xp, u.level, u.streak, u.created_at;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO codecrafts;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO codecrafts;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO codecrafts;

-- Insert initial configuration data
INSERT INTO public.configuration (key, value, description) VALUES
('app_version', '1.0.0', 'Application version'),
('maintenance_mode', 'false', 'Enable/disable maintenance mode'),
('registration_enabled', 'true', 'Enable/disable user registration'),
('max_file_upload_size', '10485760', 'Maximum file upload size in bytes (10MB)'),
('session_timeout', '3600', 'Session timeout in seconds'),
('rate_limit_requests', '60', 'Rate limit requests per minute'),
('xp_per_level', '250', 'XP required per level'),
('daily_streak_bonus', '10', 'Bonus XP for daily streak')
ON CONFLICT (key) DO NOTHING;

-- Create audit log table for tracking important changes
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    user_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);

-- Create function for audit logging
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, old_values, user_id)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), OLD.user_id);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, old_values, new_values, user_id)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), NEW.user_id);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, new_values, user_id)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW), NEW.user_id);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply configuration changes
SELECT pg_reload_conf();

-- Log initialization completion
DO $$
BEGIN
    RAISE NOTICE 'CodeCrafts database initialization completed successfully';
    RAISE NOTICE 'Database version: %', version();
    RAISE NOTICE 'Extensions installed: uuid-ossp, pg_trgm, pg_stat_statements';
    RAISE NOTICE 'Performance optimizations applied';
    RAISE NOTICE 'Indexes and views created';
END $$;