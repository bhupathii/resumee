# Supabase Database Setup Instructions

## Prerequisites
- Supabase account (free tier is sufficient)
- Project created in Supabase dashboard

## Step 1: Create Database Tables

1. Go to your Supabase dashboard
2. Navigate to "SQL Editor"
3. Copy and paste the content from `schema.sql`
4. Click "Run" to execute the SQL commands

## Step 2: Set Up Storage Buckets

1. Navigate to "Storage" in the Supabase dashboard
2. Click "Create bucket"
3. Create two buckets:
   - **resumes**: Set as public (for generated resume PDFs)
   - **payments**: Set as private (for payment screenshots)

## Step 3: Configure Storage Policies

Run these commands in the SQL Editor:

```sql
-- Create storage policies for resumes bucket
CREATE POLICY "Allow public access to resumes" ON storage.objects
    FOR SELECT USING (bucket_id = 'resumes');

CREATE POLICY "Allow authenticated users to upload resumes" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'resumes');

-- Create storage policies for payments bucket (private)
CREATE POLICY "Only service role can access payments" ON storage.objects
    FOR ALL USING (bucket_id = 'payments' AND auth.role() = 'service_role');
```

## Step 4: Get API Keys

1. Go to "Settings" → "API"
2. Copy the following values:
   - **URL**: This is your `SUPABASE_URL`
   - **anon public key**: This is your `SUPABASE_ANON_KEY`
   - **service_role key**: This is your `SUPABASE_SERVICE_KEY` (keep this secret!)

## Step 5: Update Environment Variables

Update your `.env` file with:

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

## Step 6: Test the Connection

Run this Python script to test the connection:

```python
from supabase import create_client, Client

url = "your_supabase_url"
key = "your_supabase_anon_key"

supabase: Client = create_client(url, key)

# Test connection
try:
    result = supabase.table('users').select('count').execute()
    print("✅ Supabase connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Database Schema Overview

### Tables Created:

1. **users**: Store user information and premium status
2. **payments**: Track payment records and verification status
3. **generations**: Log all resume generation events
4. **feedback**: Store user feedback (optional)

### Storage Buckets:

1. **resumes**: Public bucket for generated PDF files
2. **payments**: Private bucket for payment screenshots

### Security:

- Row Level Security (RLS) enabled
- Policies restrict access to user's own data
- Service role has full access for backend operations

## Admin Functions

To approve a payment manually:

```sql
-- Update payment status
UPDATE payments 
SET status = 'approved', updated_at = NOW() 
WHERE id = 'payment_id_here';

-- Update user to premium
UPDATE users 
SET is_premium = true, upgraded_at = NOW() 
WHERE email = 'user_email_here';
```

## Monitoring Queries

```sql
-- Check pending payments
SELECT * FROM payments WHERE status = 'pending' ORDER BY created_at DESC;

-- View user statistics
SELECT * FROM user_stats;

-- View payment statistics
SELECT * FROM payment_stats;

-- View daily activity
SELECT * FROM daily_activity LIMIT 30;
```

## Backup Considerations

Supabase automatically backs up your database. For additional security:

1. Enable point-in-time recovery in your Supabase project settings
2. Consider periodic manual backups of critical data
3. Set up monitoring alerts for important events

## Troubleshooting

### Common Issues:

1. **RLS Policies**: Make sure your policies allow the service role to perform operations
2. **Storage Permissions**: Ensure buckets have correct public/private settings
3. **API Keys**: Double-check that you're using the correct keys in your environment

### Testing Commands:

```sql
-- Test user creation
INSERT INTO users (email, ip) VALUES ('test@example.com', '127.0.0.1');

-- Test payment creation
INSERT INTO payments (email, screenshot_url) VALUES ('test@example.com', 'https://example.com/test.jpg');

-- Test generation logging
INSERT INTO generations (email, ip, job_description_snippet) VALUES ('test@example.com', '127.0.0.1', 'Software Engineer position...');
```