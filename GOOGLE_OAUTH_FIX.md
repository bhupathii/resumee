# 🔧 Google OAuth Authentication Fix

## 🚨 Current Issue
**Error Message**: "Invalid Google token or authentication failed"

**Root Cause**: Missing Google OAuth credentials in environment variables

## ✅ Step-by-Step Fix

### Step 1: Google Cloud Console Setup

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create or Select Project**: Choose existing project or create "TailorCV"
3. **Enable Google+ API**:
   - Go to **APIs & Services** → **Library**
   - Search for "Google+ API" or "Google Identity"
   - Click **Enable**

4. **Create OAuth 2.0 Credentials**:
   - Go to **APIs & Services** → **Credentials** 
   - Click **+ CREATE CREDENTIALS** → **OAuth client ID**
   - If prompted, configure OAuth consent screen first

5. **OAuth Consent Screen Setup**:
   - Choose **External** user type
   - App name: "TailorCV"
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add `email`, `profile`, `openid`
   - Test users: Add your email

6. **Create OAuth Client ID**:
   - Application type: **Web application**
   - Name: "TailorCV Web Client"
   - **Authorized JavaScript origins**:
     ```
     http://localhost:3000
     https://resumee-khaki.vercel.app
     https://your-production-domain.com
     ```
   - **Authorized redirect URIs**:
     ```
     http://localhost:3000
     https://resumee-khaki.vercel.app
     https://your-production-domain.com
     ```

7. **Copy Client ID**: Save the Client ID (ends with `.googleusercontent.com`)

### Step 2: Configure Environment Variables

#### Frontend (.env)
```bash
# Edit tailorcv-frontend/.env
REACT_APP_GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
REACT_APP_API_URL=http://localhost:5000
REACT_APP_SITE_URL=http://localhost:3000
```

#### Backend (.env)
```bash
# Edit tailorcv-backend/.env
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
JWT_SECRET=your_long_random_secret_key_here_at_least_32_characters
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
OPENROUTER_API_KEY=your_openrouter_key
```

### Step 3: Update Production Environment Variables

#### Vercel (Frontend)
```bash
vercel env add REACT_APP_GOOGLE_CLIENT_ID
# Enter your Google Client ID when prompted

vercel env add REACT_APP_API_URL
# Enter your Railway backend URL
```

#### Railway (Backend)
```bash
# In Railway dashboard, add environment variables:
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
JWT_SECRET=your_long_random_secret_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
OPENROUTER_API_KEY=your_openrouter_key
```

### Step 4: Test the Fix

1. **Restart both applications**:
   ```bash
   # Backend
   cd tailorcv-backend
   python app.py
   
   # Frontend (new terminal)
   cd tailorcv-frontend
   npm start
   ```

2. **Test Google OAuth**:
   - Go to http://localhost:3000
   - Should redirect to signin page
   - Click "Sign in with Google"
   - Should open Google OAuth popup
   - After successful auth, should redirect to dashboard

### Step 5: Production Deployment

1. **Deploy to Railway** (Backend):
   - Push code to GitHub
   - Railway will auto-deploy
   - Verify environment variables are set

2. **Deploy to Vercel** (Frontend):
   - Push code to GitHub  
   - Vercel will auto-deploy
   - Verify environment variables are set

## 🔍 Troubleshooting

### Error: "Invalid Google token"
- **Check**: Frontend and backend use the same Google Client ID
- **Check**: Google Cloud Console authorized domains match your URLs
- **Check**: OAuth consent screen is properly configured

### Error: "API URL not configured"
- **Check**: `REACT_APP_API_URL` is set in frontend .env
- **Check**: Backend is running and accessible
- **Check**: CORS is configured properly

### Error: "Authentication failed"
- **Check**: `GOOGLE_CLIENT_ID` is set in backend .env
- **Check**: JWT_SECRET is set and long enough
- **Check**: Supabase connection is working

### Error: "Google Sign-In button not appearing"
- **Check**: `REACT_APP_GOOGLE_CLIENT_ID` is set
- **Check**: Google script is loading (check browser console)
- **Check**: No JavaScript errors in console

## 📋 Quick Fix Checklist

- [ ] Google Cloud Console project created
- [ ] OAuth 2.0 credentials created
- [ ] Authorized origins and redirect URIs added
- [ ] Frontend .env file has `REACT_APP_GOOGLE_CLIENT_ID`
- [ ] Backend .env file has `GOOGLE_CLIENT_ID`
- [ ] Both frontend and backend use the same Client ID
- [ ] Production environment variables set
- [ ] Applications restarted after env changes
- [ ] OAuth consent screen configured
- [ ] Test users added (if needed)

## 🎯 Expected Result After Fix

1. **Visit site** → Redirects to professional signin page
2. **Click "Sign in with Google"** → Opens Google OAuth popup
3. **Complete Google authentication** → Redirects to dashboard
4. **See user profile** → Name, email, and profile picture displayed
5. **Access protected features** → Generate resume, dashboard, etc.

## 🔗 Helpful Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)

The main issue is that Google OAuth credentials are missing from the environment configuration. Follow this guide to set them up properly!