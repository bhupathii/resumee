-- TailorCV Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Users table
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT,
    ip TEXT NOT NULL,
    is_premium BOOLEAN DEFAULT FALSE,
    generation_count INTEGER DEFAULT 0,
    last_generated TIMESTAMP WITH TIME ZONE,
    upgraded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payments table
CREATE TABLE payments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT NOT NULL,
    screenshot_url TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    amount DECIMAL(10, 2) DEFAULT 299.00,
    payment_method TEXT DEFAULT 'upi',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generations table (for logging resume generations)
CREATE TABLE generations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT,
    ip TEXT NOT NULL,
    job_description_snippet TEXT,
    resume_url TEXT,
    is_premium BOOLEAN DEFAULT FALSE,
    processing_time_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feedback table (optional)
CREATE TABLE feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_ip ON users (ip);
CREATE INDEX idx_users_is_premium ON users (is_premium);
CREATE INDEX idx_payments_email ON payments (email);
CREATE INDEX idx_payments_status ON payments (status);
CREATE INDEX idx_payments_created_at ON payments (created_at);
CREATE INDEX idx_generations_email ON generations (email);
CREATE INDEX idx_generations_ip ON generations (ip);
CREATE INDEX idx_generations_created_at ON generations (created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at 
    BEFORE UPDATE ON payments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Create policies for RLS
-- Users can only see their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text OR email = auth.email());

-- Payments can be viewed by the user who made them
CREATE POLICY "Users can view own payments" ON payments
    FOR SELECT USING (email = auth.email());

-- Allow anonymous users to insert generations (for API usage)
CREATE POLICY "Allow anonymous generations" ON generations
    FOR INSERT WITH CHECK (true);

-- Allow anonymous users to insert feedback
CREATE POLICY "Allow anonymous feedback" ON feedback
    FOR INSERT WITH CHECK (true);

-- Allow service role to manage all data (for backend API)
CREATE POLICY "Service role can manage all data" ON users
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage payments" ON payments
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage generations" ON generations
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage feedback" ON feedback
    FOR ALL USING (auth.role() = 'service_role');

-- Create storage buckets
-- Run these commands in the Supabase Storage section:

-- INSERT INTO storage.buckets (id, name, public) VALUES ('resumes', 'resumes', true);
-- INSERT INTO storage.buckets (id, name, public) VALUES ('payments', 'payments', false);

-- Storage policies for resumes bucket
-- CREATE POLICY "Allow public access to resumes" ON storage.objects
--     FOR SELECT USING (bucket_id = 'resumes');

-- CREATE POLICY "Allow authenticated users to upload resumes" ON storage.objects
--     FOR INSERT WITH CHECK (bucket_id = 'resumes');

-- Storage policies for payments bucket (private)
-- CREATE POLICY "Only service role can access payments" ON storage.objects
--     FOR ALL USING (bucket_id = 'payments' AND auth.role() = 'service_role');

-- Insert some sample data (optional)
-- INSERT INTO users (email, ip, is_premium, generation_count) VALUES
--     ('test@example.com', '192.168.1.1', false, 1),
--     ('premium@example.com', '192.168.1.2', true, 5);

-- Insert sample payment (optional)
-- INSERT INTO payments (email, screenshot_url, status) VALUES
--     ('premium@example.com', 'https://example.com/screenshot.jpg', 'approved');

-- Views for analytics (optional)
CREATE VIEW user_stats AS
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN is_premium = true THEN 1 END) as premium_users,
    COUNT(CASE WHEN is_premium = false THEN 1 END) as free_users,
    AVG(generation_count) as avg_generations_per_user,
    SUM(generation_count) as total_generations
FROM users;

CREATE VIEW payment_stats AS
SELECT 
    COUNT(*) as total_payments,
    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_payments,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_payments,
    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_payments,
    SUM(CASE WHEN status = 'approved' THEN amount ELSE 0 END) as total_revenue
FROM payments;

CREATE VIEW daily_activity AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as generations,
    COUNT(DISTINCT ip) as unique_users,
    COUNT(CASE WHEN is_premium = true THEN 1 END) as premium_generations
FROM generations
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Grant permissions for views
GRANT SELECT ON user_stats TO anon, authenticated;
GRANT SELECT ON payment_stats TO anon, authenticated;
GRANT SELECT ON daily_activity TO anon, authenticated;