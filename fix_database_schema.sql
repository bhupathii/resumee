-- TailorCV Database Schema Fix
-- Run this script in your Supabase SQL Editor to fix the column errors

-- First, let's check what tables exist and their structure
-- This script will safely add missing columns and create missing tables

-- 1. Create users table if it doesn't exist (basic structure first)
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT UNIQUE,
    ip TEXT,
    is_premium BOOLEAN DEFAULT FALSE,
    generation_count INTEGER DEFAULT 0,
    last_generated TIMESTAMP WITH TIME ZONE,
    upgraded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Add Google OAuth columns to users table (safe additions)
DO $$ 
BEGIN
    -- Add google_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='google_id') THEN
        ALTER TABLE users ADD COLUMN google_id TEXT UNIQUE;
    END IF;

    -- Add name column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='name') THEN
        ALTER TABLE users ADD COLUMN name TEXT;
    END IF;

    -- Add profile_picture column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='profile_picture') THEN
        ALTER TABLE users ADD COLUMN profile_picture TEXT;
    END IF;

    -- Add google_email column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='google_email') THEN
        ALTER TABLE users ADD COLUMN google_email TEXT;
    END IF;

    -- Add last_login column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='last_login') THEN
        ALTER TABLE users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
    END IF;

    -- Add auth_provider column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='auth_provider') THEN
        ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'guest';
    END IF;
END $$;

-- 3. Create user_sessions table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create user_preferences table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'light',
    email_notifications BOOLEAN DEFAULT TRUE,
    marketing_emails BOOLEAN DEFAULT FALSE,
    preferred_template TEXT DEFAULT 'professional',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Handle generations table (add user_id if it doesn't exist)
DO $$ 
BEGIN
    -- Check if generations table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='generations') THEN
        -- Add user_id column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='generations' AND column_name='user_id') THEN
            ALTER TABLE generations ADD COLUMN user_id UUID REFERENCES users(id);
        END IF;
    ELSE
        -- Create generations table if it doesn't exist
        CREATE TABLE generations (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            email TEXT,
            ip TEXT,
            job_description_snippet TEXT,
            resume_url TEXT,
            is_premium BOOLEAN DEFAULT FALSE,
            user_id UUID REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    END IF;
END $$;

-- 6. Handle payments table (add user_id if it doesn't exist)
DO $$ 
BEGIN
    -- Check if payments table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='payments') THEN
        -- Add user_id column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='payments' AND column_name='user_id') THEN
            ALTER TABLE payments ADD COLUMN user_id UUID REFERENCES users(id);
        END IF;
        
        -- Add updated_at column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='payments' AND column_name='updated_at') THEN
            ALTER TABLE payments ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        END IF;
    ELSE
        -- Create payments table if it doesn't exist
        CREATE TABLE payments (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            email TEXT,
            screenshot_url TEXT,
            timestamp TEXT,
            status TEXT DEFAULT 'pending',
            user_id UUID REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    END IF;
END $$;

-- 7. Create indexes for performance (safe - will only create if they don't exist)
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id);
CREATE INDEX IF NOT EXISTS idx_users_google_email ON users (google_email);
CREATE INDEX IF NOT EXISTS idx_users_auth_provider ON users (auth_provider);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions (session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions (expires_at);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences (user_id);
CREATE INDEX IF NOT EXISTS idx_generations_user_id ON generations (user_id);
CREATE INDEX IF NOT EXISTS idx_generations_email ON generations (email);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments (user_id);
CREATE INDEX IF NOT EXISTS idx_payments_email ON payments (email);

-- 8. Create a trigger function for updating updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 9. Create triggers for updated_at (safe - will replace if exists)
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_payments_updated_at ON payments;
CREATE TRIGGER update_payments_updated_at 
    BEFORE UPDATE ON payments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 10. Enable Row Level Security (RLS) for authentication tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- 11. Create RLS policies for secure access
-- Users can view and update their own data
DROP POLICY IF EXISTS "Users can view own data" ON users;
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (id::text = auth.uid()::text);

DROP POLICY IF EXISTS "Users can update own data" ON users;
CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (id::text = auth.uid()::text);

-- Service role can manage all data
DROP POLICY IF EXISTS "Service role can manage users" ON users;
CREATE POLICY "Service role can manage users" ON users
    FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role can manage sessions" ON user_sessions;
CREATE POLICY "Service role can manage sessions" ON user_sessions
    FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role can manage preferences" ON user_preferences;
CREATE POLICY "Service role can manage preferences" ON user_preferences
    FOR ALL USING (auth.role() = 'service_role');

-- 12. Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Success message
SELECT 'Database schema updated successfully! All tables and columns are now properly configured.' AS result;