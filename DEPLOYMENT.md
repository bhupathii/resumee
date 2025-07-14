# TailorCV Deployment Guide

This guide covers deploying TailorCV to free-tier cloud services.

## 🎯 Overview

- **Frontend**: Vercel (free tier)
- **Backend**: Railway (free tier)
- **Database**: Supabase (free tier)
- **AI Service**: OpenRouter (free tier)
- **Email**: FormSubmit (free tier)

## 📋 Prerequisites

- GitHub account
- Vercel account
- Railway account
- Supabase account
- OpenRouter API key

## 🗄️ Database Setup (Supabase)

### Step 1: Create Project

1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Choose a region close to your users
4. Wait for project setup to complete

### Step 2: Set Up Database

1. Navigate to "SQL Editor"
2. Copy and paste the contents of `tailorcv-backend/database/schema.sql`
3. Click "Run" to create tables and policies

### Step 3: Configure Storage

1. Go to "Storage" in the sidebar
2. Create two buckets:
   - `resumes` (public) - for generated PDFs
   - `payments` (private) - for payment screenshots

3. Set up storage policies by running this SQL:

```sql
-- Resumes bucket policies
CREATE POLICY "Allow public access to resumes" ON storage.objects
    FOR SELECT USING (bucket_id = 'resumes');

CREATE POLICY "Allow service role to upload resumes" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'resumes');

-- Payments bucket policies
CREATE POLICY "Service role can manage payments" ON storage.objects
    FOR ALL USING (bucket_id = 'payments' AND auth.role() = 'service_role');
```

### Step 4: Get API Credentials

1. Go to "Settings" → "API"
2. Copy these values:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`

## 🚀 Backend Deployment (Railway)

### Step 1: Prepare Repository

1. Push your code to GitHub
2. Make sure `tailorcv-backend/` is in the repository root

### Step 2: Deploy to Railway

1. Go to [Railway](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Select the root directory (where `tailorcv-backend/` is located)

### Step 3: Configure Environment Variables

In Railway dashboard, add these environment variables:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
ADMIN_EMAIL=admin@yourdomain.com
DEBUG=False
PORT=5000
FLASK_ENV=production
```

### Step 4: Configure Build

1. Railway should auto-detect the Dockerfile
2. If not, set build command: `docker build -t tailorcv-backend .`
3. Set start command: `python app.py`

### Step 5: Get Backend URL

1. Once deployed, Railway will provide a URL like: `https://your-app-name.railway.app`
2. Save this URL for frontend configuration

## 🌐 Frontend Deployment (Vercel)

### Step 1: Prepare Repository

1. Ensure `tailorcv-frontend/` contains your React app
2. Verify `package.json` and `vercel.json` are present

### Step 2: Deploy to Vercel

1. Go to [Vercel](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Set root directory to `tailorcv-frontend/`
5. Vercel will auto-detect React settings

### Step 3: Configure Environment Variables

In Vercel dashboard, add:

```env
REACT_APP_API_URL=https://your-backend-url.railway.app
REACT_APP_SITE_URL=https://your-frontend-url.vercel.app
REACT_APP_ENVIRONMENT=production
```

### Step 4: Configure Build Settings

- Build Command: `npm run build`
- Output Directory: `build`
- Install Command: `npm install`

## 🔑 API Keys Setup

### OpenRouter API Key

1. Go to [OpenRouter](https://openrouter.ai)
2. Create an account
3. Generate an API key
4. Add credits (they offer free tier)

### FormSubmit Setup

1. Go to [FormSubmit](https://formsubmit.co)
2. No registration required
3. Use your admin email in the service configuration

## 🔧 Configuration Updates

### Update Frontend API URL

In `tailorcv-frontend/src/pages/ResumeGenerator.tsx`, update the API call:

```typescript
const response = await fetch(`${process.env.REACT_APP_API_URL}/api/generate-resume`, {
  method: 'POST',
  body: formData,
});
```

### Update Backend CORS

In `tailorcv-backend/app.py`, update CORS settings:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://your-frontend-url.vercel.app'])
```

## 📊 Monitoring Setup

### Railway Monitoring

1. Check Railway dashboard for:
   - Build logs
   - Runtime logs
   - Memory usage
   - CPU usage

### Vercel Analytics

1. Enable Vercel Analytics in project settings
2. Monitor:
   - Page views
   - Performance metrics
   - Error rates

### Supabase Monitoring

1. Use Supabase dashboard to monitor:
   - Database queries
   - Storage usage
   - API requests

## 🛡️ Security Checklist

- [ ] Environment variables are set correctly
- [ ] Supabase RLS policies are enabled
- [ ] CORS is configured for production domains
- [ ] API keys are kept secret
- [ ] Database has proper indexes
- [ ] File upload limits are enforced
- [ ] Rate limiting is active

## 🔍 Testing Deployment

### Backend Health Check

```bash
curl https://your-backend-url.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Frontend Test

1. Visit your Vercel URL
2. Try generating a resume
3. Test payment flow
4. Verify email notifications

### Database Test

```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Test user creation
INSERT INTO users (email, ip) VALUES ('test@example.com', '127.0.0.1');
```

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Check backend CORS configuration
   - Verify frontend is calling correct API URL

2. **Database Connection Failures**:
   - Verify Supabase credentials
   - Check RLS policies
   - Ensure tables exist

3. **LaTeX Compilation Errors**:
   - Check if LaTeX is installed in Docker image
   - Verify template syntax
   - Check file permissions

4. **File Upload Issues**:
   - Verify storage bucket configuration
   - Check file size limits
   - Ensure correct bucket policies

### Debug Commands

```bash
# Check backend logs
railway logs

# Check frontend build logs
vercel --logs

# Test database connection
psql -h your-db-host -p 5432 -U your-username your-database
```

## 📈 Scaling Considerations

### Free Tier Limits

- **Railway**: 500 hours/month, 1GB RAM, 1GB storage
- **Vercel**: 100GB bandwidth, 1000 serverless functions
- **Supabase**: 500MB database, 1GB storage, 50MB file uploads

### Performance Optimization

1. **Frontend**:
   - Enable Vercel's Edge Network
   - Optimize images and assets
   - Use React.lazy for code splitting

2. **Backend**:
   - Add Redis for caching
   - Optimize database queries
   - Use background jobs for heavy tasks

3. **Database**:
   - Add indexes for frequently queried columns
   - Use database functions for complex operations
   - Archive old data regularly

## 🔄 CI/CD Pipeline

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          working-directory: ./tailorcv-frontend
```

## 📞 Support

If you encounter issues during deployment:

1. Check the logs in your deployment platforms
2. Verify all environment variables are set
3. Test each component separately
4. Review the troubleshooting section

For additional help, create an issue in the GitHub repository.

---

**Happy Deploying! 🚀**