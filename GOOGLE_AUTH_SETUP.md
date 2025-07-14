# Google OAuth Setup Guide for TailorCV

This guide will help you set up Google OAuth authentication for both the frontend and backend of TailorCV.

## Prerequisites

✅ **Dependencies Already Installed:**
- Backend: `google-auth`, `google-auth-oauthlib`, `PyJWT`
- Frontend: `framer-motion`, `lucide-react`

## 1. Google Cloud Console Setup

### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Name your project (e.g., "TailorCV")

### Step 2: Enable Google+ API
1. Go to **APIs & Services** > **Library**
2. Search for "Google+ API" or "Google Identity"
3. Click **Enable**

### Step 3: Create OAuth 2.0 Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen first:
   - Choose **External** for user type
   - Fill in app name: "TailorCV"
   - Add your email as developer contact
   - Add scopes: `email`, `profile`, `openid`

4. Create OAuth client ID:
   - Application type: **Web application**
   - Name: "TailorCV Web Client"
   
5. **Authorized JavaScript origins:**
   ```
   http://localhost:3000
   https://resumee-khaki.vercel.app
   https://your-custom-domain.com
   ```

6. **Authorized redirect URIs:**
   ```
   http://localhost:3000
   https://resumee-khaki.vercel.app
   https://your-custom-domain.com
   ```

7. Click **Create** and copy your **Client ID**

## 2. Environment Variables Setup

### Backend Environment Variables (Railway)
Add these environment variables to your Railway deployment:

```env
GOOGLE_CLIENT_ID=your_google_client_id_here.googleusercontent.com
JWT_SECRET=your_super_secret_jwt_key_here_make_it_long_and_random
```

### Frontend Environment Variables (Vercel)
Add these environment variables to your Vercel deployment:

```env
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id_here.googleusercontent.com
REACT_APP_API_URL=https://your-railway-backend-url.railway.app
```

## 3. Local Development Setup

### For Local Testing:
Create `.env` files:

**tailorcv-backend/.env:**
```env
GOOGLE_CLIENT_ID=your_google_client_id_here.googleusercontent.com
JWT_SECRET=your_super_secret_jwt_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENROUTER_API_KEY=your_openrouter_key
```

**tailorcv-frontend/.env:**
```env
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id_here.googleusercontent.com
REACT_APP_API_URL=http://localhost:5000
```

## 4. Database Schema

The authentication system requires these tables in Supabase (already created):

```sql
-- Users table (enhanced)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  google_id TEXT UNIQUE,
  name TEXT,
  email TEXT UNIQUE,
  google_email TEXT,
  profile_picture TEXT,
  is_premium BOOLEAN DEFAULT FALSE,
  generation_count INTEGER DEFAULT 0,
  last_generated TIMESTAMP,
  upgraded_at TIMESTAMP,
  ip TEXT,
  auth_provider TEXT DEFAULT 'google',
  last_login TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- User sessions table
CREATE TABLE user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  session_token TEXT UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  last_accessed TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);

-- User preferences table
CREATE TABLE user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  theme TEXT DEFAULT 'light',
  email_notifications BOOLEAN DEFAULT TRUE,
  preferred_template TEXT DEFAULT 'professional',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## 5. Testing the Authentication

### Frontend Testing:
1. Navigate to your deployed frontend
2. Click the Google Sign-In button
3. Complete Google OAuth flow
4. Verify user profile appears in navigation

### Backend Testing:
Test the auth endpoints:

```bash
# Test Google Auth (replace with actual Google token)
curl -X POST https://your-backend.railway.app/api/auth/google \
  -H "Content-Type: application/json" \
  -d '{"token": "your_google_id_token"}'

# Test session verification
curl -X GET https://your-backend.railway.app/api/auth/me \
  -H "Authorization: Bearer your_session_token"

# Test logout
curl -X POST https://your-backend.railway.app/api/auth/logout \
  -H "Authorization: Bearer your_session_token"
```

## 6. Common Issues & Troubleshooting

### Issue 1: "Google Sign-In button not appearing"
**Causes:**
- Missing `REACT_APP_GOOGLE_CLIENT_ID` environment variable
- Google script failed to load
- Console errors blocking execution

**Solutions:**
- Verify environment variables in Vercel
- Check browser console for errors
- Ensure Google Client ID is correct

### Issue 2: "Invalid Google token" error
**Causes:**
- Backend `GOOGLE_CLIENT_ID` doesn't match frontend
- Token expired or malformed
- Clock skew between client and server

**Solutions:**
- Ensure both frontend and backend use same Google Client ID
- Check that Google Cloud project is properly configured
- Verify authorized domains are correct

### Issue 3: "Authentication failed" error
**Causes:**
- Database connection issues
- Missing environment variables
- CORS issues

**Solutions:**
- Check Supabase connection
- Verify all environment variables are set
- Ensure CORS is configured for your frontend domain

### Issue 4: Session not persisting
**Causes:**
- JWT secret not set
- Session token not being stored
- LocalStorage being cleared

**Solutions:**
- Set `JWT_SECRET` environment variable
- Check browser developer tools > Application > LocalStorage
- Verify session token is being returned from backend

## 7. Security Considerations

✅ **Implemented Security Features:**
- Secure session tokens using `secrets.token_urlsafe(64)`
- 7-day session expiration
- Automatic expired session cleanup
- JWT secret for additional security
- Google token verification server-side

⚠️ **Additional Recommendations:**
- Use HTTPS in production (already configured)
- Regularly rotate JWT secrets
- Implement rate limiting on auth endpoints
- Monitor for suspicious authentication attempts

## 8. Authentication Flow Summary

1. **User clicks Google Sign-In** → Frontend loads Google script
2. **Google OAuth popup** → User authenticates with Google
3. **Google returns token** → Frontend receives ID token
4. **Frontend sends token to backend** → `/api/auth/google`
5. **Backend verifies token** → Validates with Google servers
6. **Backend creates/updates user** → Stores in Supabase
7. **Backend creates session** → Returns session token
8. **Frontend stores session** → LocalStorage + state management
9. **Subsequent requests** → Include session token in Authorization header

## 9. Deployment Checklist

### Vercel (Frontend):
- [ ] Environment variables set (`REACT_APP_GOOGLE_CLIENT_ID`, `REACT_APP_API_URL`)
- [ ] Domain added to Google Cloud Console authorized origins
- [ ] Build successful
- [ ] Google Sign-In button visible

### Railway (Backend):
- [ ] Environment variables set (`GOOGLE_CLIENT_ID`, `JWT_SECRET`, etc.)
- [ ] Database schema applied
- [ ] Health check endpoint responding
- [ ] Auth endpoints responding correctly

### Google Cloud Console:
- [ ] OAuth consent screen configured
- [ ] Authorized domains added (both localhost and production)
- [ ] API quotas sufficient
- [ ] Client ID copied to both environments

## Support

If you encounter issues:
1. Check browser console for JavaScript errors
2. Check backend logs for authentication errors
3. Verify all environment variables are set correctly
4. Test with different browsers/incognito mode
5. Check Google Cloud Console for any API errors

The authentication system is fully implemented and should work once properly configured with Google Cloud Console credentials. 