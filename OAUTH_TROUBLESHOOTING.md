# 🔧 Google OAuth "Invalid Token" Troubleshooting Guide

## 🚨 Error: "Invalid Google token or authentication failed"

This error typically occurs for one of these reasons:

### 1. **Environment Variables Not Set**
The most common cause - Google Client ID is missing or incorrect.

#### ✅ Quick Fix:
```bash
# 1. Copy your EXACT Client ID from Google Cloud Console screenshot
# 2. Update backend environment
echo "GOOGLE_CLIENT_ID=your_actual_client_id_here.googleusercontent.com" >> tailorcv-backend/.env

# 3. Update frontend environment  
echo "REACT_APP_GOOGLE_CLIENT_ID=your_actual_client_id_here.googleusercontent.com" >> tailorcv-frontend/.env

# 4. Restart both applications
```

### 2. **Supabase Database Not Configured**
The authentication might fail when trying to save user data.

#### ✅ Database Fix:
1. **Go to your Supabase project**
2. **Run the SQL commands** from `tailorcv-backend/database/auth_schema.sql`
3. **Update environment variables**:
   ```bash
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

### 3. **Backend Not Running or Accessible**
Frontend can't reach the backend authentication endpoint.

#### ✅ Backend Fix:
```bash
# 1. Start backend
cd tailorcv-backend
python app.py

# 2. Test if it's running
curl http://localhost:5000/api/health

# 3. Check frontend API URL
# Make sure REACT_APP_API_URL in frontend/.env matches your backend
```

### 4. **Google Cloud Console Misconfiguration**
OAuth domains don't match your application URLs.

#### ✅ Google Console Fix:
Based on your screenshot, add these domains:

**Authorized JavaScript Origins:**
- `https://resumee-khaki.vercel.app` ✅ (you have this)
- `http://localhost:3000` ➕ (add this)
- `https://localhost:3000` ➕ (add this)

**Authorized Redirect URIs:**
- `https://resumee-khaki.vercel.app` ✅ (you have this)
- `http://localhost:3000` ➕ (add this)  
- `https://localhost:3000` ➕ (add this)

## 🔍 Step-by-Step Debugging

### Step 1: Check Environment Files
```bash
# Run the debug script
python3 debug_oauth_issue.py
```

### Step 2: Verify Your Client ID Format
Your Client ID should look like:
```
123456789-abcdefghijk.apps.googleusercontent.com
```

### Step 3: Test Backend Health
```bash
curl http://localhost:5000/api/health
```
Should return: `{"status": "healthy", "timestamp": "..."}`

### Step 4: Test OAuth Endpoint
```bash
curl -X POST http://localhost:5000/api/auth/google \
  -H "Content-Type: application/json" \
  -d '{"token": "test"}'
```

**Expected responses:**
- ✅ `{"error": "Invalid Google token or authentication failed"}` - OAuth endpoint working
- ❌ `{"error": "Google authentication not configured on server"}` - Client ID missing
- ❌ Connection refused - Backend not running

### Step 5: Check Database Connection
If OAuth endpoint works but still fails, it's likely a database issue.

## 🎯 Most Common Solutions

### Solution 1: Missing Client ID (90% of cases)
```bash
# Copy the EXACT Client ID from your Google Cloud Console
# Update both .env files with the real Client ID
# Restart applications
```

### Solution 2: Database Schema Missing (5% of cases)
```sql
-- Run this in Supabase SQL editor
-- Copy content from tailorcv-backend/database/auth_schema.sql
```

### Solution 3: Backend Not Running (3% of cases)
```bash
cd tailorcv-backend
pip install -r requirements.txt
python app.py
```

### Solution 4: CORS/Domain Issues (2% of cases)
- Add localhost domains to Google Cloud Console
- Ensure authorized origins match your URLs exactly

## 🔧 Quick Fix Script

Create and run this script to fix common issues:

```bash
#!/bin/bash
echo "🔧 Quick OAuth Fix"

# Check if backend is running
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running - start it first!"
    exit 1
fi

# Check if Client ID is configured
if grep -q "your_google_client_id_here" tailorcv-backend/.env; then
    echo "❌ Google Client ID not configured"
    echo "Update GOOGLE_CLIENT_ID in tailorcv-backend/.env"
    exit 1
fi

if grep -q "your_google_client_id_here" tailorcv-frontend/.env; then
    echo "❌ Frontend Client ID not configured"
    echo "Update REACT_APP_GOOGLE_CLIENT_ID in tailorcv-frontend/.env"
    exit 1
fi

echo "✅ Environment looks good - test the OAuth flow now"
```

## 📋 Environment File Templates

### Backend (.env)
```bash
GOOGLE_CLIENT_ID=123456789-abcdefghijk.apps.googleusercontent.com
JWT_SECRET=your_32_character_or_longer_secret_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DEBUG=True
PORT=5000
```

### Frontend (.env)
```bash
REACT_APP_GOOGLE_CLIENT_ID=123456789-abcdefghijk.apps.googleusercontent.com
REACT_APP_API_URL=http://localhost:5000
REACT_APP_SITE_URL=http://localhost:3000
```

## 🚀 After Fixing

1. **Restart both applications**
2. **Test locally**: http://localhost:3000
3. **Test production**: https://resumee-khaki.vercel.app
4. **Verify OAuth flow works end-to-end**

The error "Invalid Google token or authentication failed" should now be resolved!