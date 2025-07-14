-- Additional Authentication Schema for TailorCV
-- Run this after the main schema.sql

-- Update users table to support Google OAuth
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id TEXT UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS name TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_email TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider TEXT DEFAULT 'guest';

-- Create user sessions table
CREATE TABLE user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user preferences table
CREATE TABLE user_preferences (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'light',
    email_notifications BOOLEAN DEFAULT TRUE,
    marketing_emails BOOLEAN DEFAULT FALSE,
    preferred_template TEXT DEFAULT 'professional',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Update generations table to link to authenticated users
ALTER TABLE generations ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- Update payments table to link to authenticated users  
ALTER TABLE payments ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users (google_id);
CREATE INDEX IF NOT EXISTS idx_users_google_email ON users (google_email);
CREATE INDEX IF NOT EXISTS idx_users_auth_provider ON users (auth_provider);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions (session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions (expires_at);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences (user_id);
CREATE INDEX IF NOT EXISTS idx_generations_user_id ON generations (user_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments (user_id);

-- Update triggers for user_preferences
CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update RLS policies for new tables
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- User sessions policies
CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT USING (user_id::text = auth.uid()::text);

CREATE POLICY "Service role can manage sessions" ON user_sessions
    FOR ALL USING (auth.role() = 'service_role');

-- User preferences policies  
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING (user_id::text = auth.uid()::text);

CREATE POLICY "Users can update own preferences" ON user_preferences
    FOR UPDATE USING (user_id::text = auth.uid()::text);

CREATE POLICY "Service role can manage preferences" ON user_preferences
    FOR ALL USING (auth.role() = 'service_role');

-- Clean up expired sessions function
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM user_sessions WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to clean up expired sessions (optional)
-- SELECT cron.schedule('cleanup-sessions', '0 */6 * * *', 'SELECT cleanup_expired_sessions();');

-- Create view for active user statistics
CREATE VIEW active_users AS
SELECT 
    COUNT(DISTINCT us.user_id) as active_users_24h,
    COUNT(DISTINCT CASE WHEN us.last_accessed > NOW() - INTERVAL '1 hour' THEN us.user_id END) as active_users_1h,
    COUNT(DISTINCT CASE WHEN u.auth_provider = 'google' THEN u.id END) as google_users,
    COUNT(DISTINCT CASE WHEN u.auth_provider = 'guest' THEN u.id END) as guest_users
FROM user_sessions us
JOIN users u ON us.user_id = u.id
WHERE us.last_accessed > NOW() - INTERVAL '24 hours';

-- Grant permissions
GRANT SELECT ON active_users TO anon, authenticated;

-- Sample data for testing (optional)
-- INSERT INTO users (email, google_id, name, google_email, auth_provider, is_premium) VALUES
--     ('test@gmail.com', '123456789', 'Test User', 'test@gmail.com', 'google', false); 