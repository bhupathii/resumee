# 🎯 FINAL Google OAuth Fix - Step by Step

## 🚨 Issues Found by Debugging

1. ❌ **Supabase ANON_KEY missing** - This is why authentication fails
2. ❌ **Backend not running** - Need to start with proper dependencies  
3. ⚠️ **Database schema might not be applied**
4. ⚠️ **Need your actual Google Client ID** (currently using sample)

## ✅ Complete Fix - Follow These Exact Steps

### Step 1: Get Your Credentials

#### A. Get Google Client ID from Google Cloud Console
From your screenshot, copy the **Client ID** (the long string ending in `.googleusercontent.com`)

#### B. Get Supabase Credentials
1. Go to your **Supabase project dashboard**
2. Go to **Settings** → **API**
3. Copy:
   - **Project URL** (looks like: `https://abcdefghijk.supabase.co`)
   - **anon public key** (long JWT token starting with `eyJ`)

### Step 2: Update Environment Files

#### Backend Environment (`tailorcv-backend/.env`)
Replace the entire file content with:
```bash
# Replace these with your actual values
GOOGLE_CLIENT_ID=YOUR_ACTUAL_GOOGLE_CLIENT_ID.googleusercontent.com
JWT_SECRET=a_very_long_random_secret_key_at_least_32_characters_long_for_security
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=YOUR_ACTUAL_SUPABASE_ANON_KEY_JWT_TOKEN
OPENROUTER_API_KEY=your-openrouter-api-key
DEBUG=True
PORT=5000
```

#### Frontend Environment (`tailorcv-frontend/.env`)
Replace the entire file content with:
```bash
# Replace with your actual Google Client ID
REACT_APP_GOOGLE_CLIENT_ID=YOUR_ACTUAL_GOOGLE_CLIENT_ID.googleusercontent.com
REACT_APP_API_URL=http://localhost:5000
REACT_APP_SITE_URL=http://localhost:3000
```

### Step 3: Set Up Supabase Database

1. **Go to your Supabase project**
2. **Click on "SQL Editor"**
3. **Copy and run this SQL script**:

```sql
-- Create users table if it doesn't exist
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

-- Add Google OAuth columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id TEXT UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS name TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_picture TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_email TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider TEXT DEFAULT 'guest';

-- Create user sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user preferences table
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

-- Create other tables if they don't exist
CREATE TABLE IF NOT EXISTS generations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT,
    ip TEXT,
    job_description_snippet TEXT,
    resume_url TEXT,
    is_premium BOOLEAN DEFAULT FALSE,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT,
    screenshot_url TEXT,
    timestamp TEXT,
    status TEXT DEFAULT 'pending',
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

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
```

4. **Click "RUN"** to execute the script

### Step 4: Install Dependencies and Start Backend

```bash
# Navigate to backend directory
cd tailorcv-backend

# Install dependencies
pip install -r requirements.txt

# If you get errors, try:
pip install flask flask-cors python-dotenv requests PyPDF2 supabase python-multipart werkzeug jinja2 google-auth google-auth-oauthlib google-auth-httplib2 PyJWT reportlab

# Start the backend
python app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 5: Start Frontend

Open a **new terminal** and run:
```bash
# Navigate to frontend directory
cd tailorcv-frontend

# Install dependencies (if not already done)
npm install

# Start the frontend
npm start
```

**Expected output:**
```
Local:            http://localhost:3000
```

### Step 6: Test the Fix

1. **Open browser**: http://localhost:3000
2. **Should redirect to signin page**
3. **Click "Sign in with Google"**
4. **Should open Google OAuth popup**
5. **Complete authentication**
6. **Should redirect to dashboard**

## 🔍 If It Still Doesn't Work

### Check Backend Logs
Look for these specific errors in the backend terminal:

- `Google Client ID not configured` → Update GOOGLE_CLIENT_ID
- `Supabase connection failed` → Update SUPABASE_URL and SUPABASE_ANON_KEY  
- `Database table does not exist` → Run the SQL script above

### Check Frontend Console
Open browser developer tools (F12) and look for:

- `API URL not configured` → Update REACT_APP_API_URL
- `Google script failed to load` → Check REACT_APP_GOOGLE_CLIENT_ID
- `Network error` → Make sure backend is running

## 🎯 The Key Missing Pieces

Based on the debugging, you're missing:

1. **Your actual Supabase ANON_KEY** (most important!)
2. **Your actual Google Client ID** (replace the sample one)
3. **Database tables created in Supabase**
4. **Backend running with correct dependencies**

Once you have these four things, Google OAuth will work perfectly! 🚀

## 📋 Quick Checklist

- [ ] Copied Google Client ID from Google Cloud Console
- [ ] Copied Supabase URL and ANON_KEY from Supabase dashboard
- [ ] Updated both .env files with real credentials
- [ ] Ran SQL script in Supabase
- [ ] Started backend (python app.py)
- [ ] Started frontend (npm start)
- [ ] Tested Google sign-in flow

After completing all these steps, the "Invalid Google token or authentication failed" error will be resolved!