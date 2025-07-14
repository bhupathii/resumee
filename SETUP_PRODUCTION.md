# TailorCV Production Setup Guide

This comprehensive guide will walk you through deploying TailorCV to production using **100% free** cloud services.

## 🎯 Architecture Overview

```
Frontend (Vercel) ←→ Backend (Railway) ←→ Database (Supabase)
                                    ↓
                              AI (OpenRouter)
                                    ↓
                            Email (FormSubmit)
```

## 📋 Prerequisites

Before starting, create accounts on these **free** platforms:

- [GitHub](https://github.com) - Code repository
- [Vercel](https://vercel.com) - Frontend hosting
- [Railway](https://railway.app) - Backend hosting  
- [Supabase](https://supabase.com) - Database & storage
- [OpenRouter](https://openrouter.ai) - AI API

## 🗄️ Step 1: Database Setup (Supabase)

### 1.1 Create Supabase Project

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Click **"New Project"**
3. Choose your organization
4. Fill in project details:
   - **Name**: `tailorcv-prod`
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your users
5. Click **"Create new project"**
6. Wait 2-3 minutes for setup to complete

### 1.2 Set Up Database Schema

1. In Supabase dashboard, go to **"SQL Editor"**
2. Click **"New Query"**
3. Copy the entire content from `tailorcv-backend/database/schema.sql`
4. Paste it in the SQL editor
5. Click **"Run"** button
6. You should see **"Success. No rows returned"**

### 1.3 Create Storage Buckets

1. Go to **"Storage"** in the sidebar
2. Click **"Create bucket"**
3. Create first bucket:
   - **Name**: `resumes`
   - **Public bucket**: ✅ **Enabled**
   - Click **"Create bucket"**
4. Create second bucket:
   - **Name**: `payments`
   - **Public bucket**: ❌ **Disabled**
   - Click **"Create bucket"**

### 1.4 Set Storage Policies

1. Go back to **"SQL Editor"**
2. Run this SQL to set up storage policies:

```sql
-- Resumes bucket policies (public access)
CREATE POLICY "Allow public access to resumes" ON storage.objects
    FOR SELECT USING (bucket_id = 'resumes');

CREATE POLICY "Allow service role to upload resumes" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'resumes');

CREATE POLICY "Allow service role to delete resumes" ON storage.objects
    FOR DELETE USING (bucket_id = 'resumes');

-- Payments bucket policies (private access)
CREATE POLICY "Service role can manage payments" ON storage.objects
    FOR ALL USING (bucket_id = 'payments' AND auth.role() = 'service_role');
```

### 1.5 Get API Credentials

1. Go to **"Settings"** → **"API"**
2. Copy and save these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (keep secret!)

## 🤖 Step 2: AI API Setup (OpenRouter)

### 2.1 Create OpenRouter Account

1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Sign up with your email
3. Verify your email address

### 2.2 Get API Key

1. Go to **"Keys"** in the dashboard
2. Click **"Create Key"**
3. Name it: `tailorcv-production`
4. Copy and save the API key: `sk-or-v1-xxxxx`

### 2.3 Add Credits

1. Go to **"Credits"** tab
2. Add $5-10 for testing (DeepSeek model is very cheap: ~$0.0014 per 1k tokens)
3. You can start with the free tier if available

## 🚀 Step 3: Backend Deployment (Railway)

### 3.1 Prepare Repository

1. **Push your code to GitHub**:
```bash
cd /Users/karthikmac/Downloads/test-proj-1
git init
git add .
git commit -m "Initial commit: TailorCV application"
git branch -M main
git remote add origin https://github.com/yourusername/tailorcv.git
git push -u origin main
```

### 3.2 Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"New Project"**
4. Choose **"Deploy from GitHub repo"**
5. Select your `tailorcv` repository
6. Railway will auto-detect the Dockerfile

### 3.3 Configure Environment Variables

1. In Railway dashboard, go to your project
2. Click **"Variables"** tab
3. Add these environment variables:

```env
# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Supabase Configuration  
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Email Configuration
ADMIN_EMAIL=admin@yourdomain.com

# Application Configuration
DEBUG=False
PORT=5000
FLASK_ENV=production

# Security Configuration
MAX_REQUESTS_PER_HOUR=5
PREMIUM_MAX_REQUESTS_PER_HOUR=50
MAX_FILE_SIZE_MB=10
```

### 3.4 Deploy and Get URL

1. Railway will automatically deploy
2. Wait for deployment to complete (5-10 minutes)
3. Click **"View Deployment"** to get your backend URL
4. Save this URL: `https://tailorcv-backend-production.railway.app`

### 3.5 Test Backend

1. Test health endpoint:
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

## 🌐 Step 4: Frontend Deployment (Vercel)

### 4.1 Prepare Frontend

1. **Update API URL** in frontend:
```bash
cd tailorcv-frontend
echo "REACT_APP_API_URL=https://your-backend-url.railway.app" > .env.production
```

### 4.2 Deploy to Vercel

1. Go to [Vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click **"New Project"**
4. Import your GitHub repository
5. Configure project:
   - **Framework Preset**: Create React App
   - **Root Directory**: `tailorcv-frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

### 4.3 Set Environment Variables

1. In Vercel dashboard, go to **"Settings"** → **"Environment Variables"**
2. Add these variables:

```env
REACT_APP_API_URL=https://your-backend-url.railway.app
REACT_APP_SITE_URL=https://your-frontend-url.vercel.app
REACT_APP_ENVIRONMENT=production
```

### 4.4 Deploy and Get URL

1. Click **"Deploy"**
2. Wait for deployment (3-5 minutes)
3. Get your frontend URL: `https://tailorcv.vercel.app`

## 🔧 Step 5: Final Configuration

### 5.1 Update Backend CORS

1. Go to Railway dashboard
2. Update `CORS_ORIGINS` environment variable:
```env
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

### 5.2 Update Frontend API Calls

The frontend should already be configured to use `process.env.REACT_APP_API_URL`, but verify in:
- `src/pages/ResumeGenerator.tsx`
- `src/pages/PaymentPage.tsx`

### 5.3 Set Up Custom Domain (Optional)

#### For Frontend (Vercel):
1. Go to Vercel dashboard → **"Domains"**
2. Add your domain: `tailorcv.com`
3. Configure DNS records as shown
4. Update environment variables with new domain

#### For Backend (Railway):
1. Go to Railway dashboard → **"Settings"**
2. Add custom domain: `api.tailorcv.com`
3. Configure DNS records
4. Update frontend API URL

## 📧 Step 6: Email Setup (FormSubmit)

### 6.1 Configure FormSubmit

FormSubmit requires no setup - it works with any email address. Update your admin email:

1. In Railway, set environment variable:
```env
ADMIN_EMAIL=admin@yourdomain.com
```

### 6.2 Test Email Notifications

The system will automatically send emails when:
- Users generate resumes (if email provided)
- Payment screenshots are uploaded
- Payments are approved

## 🛡️ Step 7: Security & Monitoring

### 7.1 Security Checklist

- [ ] All API keys are in environment variables (not in code)
- [ ] Supabase RLS policies are enabled
- [ ] CORS is configured for production domains only
- [ ] Rate limiting is active
- [ ] File upload limits are enforced
- [ ] Database has proper indexes

### 7.2 Set Up Monitoring

#### Railway Monitoring:
- Go to **"Metrics"** tab to monitor CPU, memory, requests
- Set up **"Alerts"** for high usage

#### Vercel Analytics:
- Enable Vercel Analytics in project settings
- Monitor page views and performance

#### Supabase Monitoring:
- Monitor database usage in Supabase dashboard
- Set up alerts for storage limits

## 🧪 Step 8: Testing Production

### 8.1 End-to-End Testing

1. **Visit your frontend URL**
2. **Test resume generation**:
   - Try LinkedIn URL input
   - Try PDF upload
   - Verify PDF download works
3. **Test payment flow**:
   - Upload payment screenshot
   - Check admin receives email notification
4. **Test admin panel**:
```bash
cd tailorcv-backend
python admin/admin_panel.py
```

### 8.2 Performance Testing

Test your backend performance:
```bash
# Install Apache Bench
brew install httpie  # macOS
# or
sudo apt install apache2-utils  # Ubuntu

# Test health endpoint
ab -n 100 -c 10 https://your-backend-url.railway.app/api/health
```

### 8.3 Load Testing

Use your free tier limits wisely:
- **Railway**: 500 hours/month, 1GB RAM
- **Vercel**: 100GB bandwidth/month
- **Supabase**: 500MB database, 1GB storage

## 📊 Step 9: Analytics & Business Intelligence

### 9.1 Set Up Analytics Queries

In Supabase SQL Editor, create views for business metrics:

```sql
-- Daily signups
CREATE VIEW daily_signups AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as new_users
FROM users 
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Conversion funnel
CREATE VIEW conversion_funnel AS
SELECT 
    COUNT(DISTINCT users.id) as total_users,
    COUNT(DISTINCT CASE WHEN payments.status = 'approved' THEN users.id END) as premium_users,
    ROUND(
        COUNT(DISTINCT CASE WHEN payments.status = 'approved' THEN users.id END) * 100.0 / 
        COUNT(DISTINCT users.id), 2
    ) as conversion_rate
FROM users 
LEFT JOIN payments ON users.email = payments.email;

-- Revenue tracking
CREATE VIEW revenue_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as payments_count,
    SUM(amount) as daily_revenue,
    AVG(amount) as avg_payment
FROM payments 
WHERE status = 'approved'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### 9.2 Monitor Key Metrics

Track these important metrics:
- **Daily Active Users** (DAU)
- **Resume Generation Rate**
- **Payment Conversion Rate**
- **Customer Acquisition Cost** (if running ads)
- **Monthly Recurring Revenue** (if implementing subscriptions)

## 🚨 Step 10: Troubleshooting Production Issues

### 10.1 Common Production Issues

#### 1. CORS Errors
**Symptoms**: Frontend can't reach backend
**Solution**: 
```bash
# Check Railway environment variables
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

#### 2. Database Connection Issues
**Symptoms**: 500 errors from backend
**Solution**: Verify Supabase credentials and RLS policies

#### 3. LaTeX Compilation Failures
**Symptoms**: PDF generation fails
**Solution**: Check Railway logs for LaTeX errors

#### 4. File Upload Issues
**Symptoms**: Resume/payment uploads fail
**Solution**: Verify Supabase storage bucket permissions

### 10.2 Debug Production Issues

#### Check Railway Logs:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and view logs
railway login
railway logs
```

#### Check Vercel Logs:
```bash
# Install Vercel CLI
npm install -g vercel

# View logs
vercel logs https://your-app.vercel.app
```

#### Monitor Database:
- Use Supabase dashboard → "Logs" section
- Check for failed queries or connection issues

### 10.3 Performance Optimization

#### Backend Optimization:
1. **Add Redis caching** (Railway Redis addon)
2. **Optimize database queries** with proper indexes
3. **Use background jobs** for heavy tasks
4. **Implement request queuing** for AI calls

#### Frontend Optimization:
1. **Enable Vercel Edge Network**
2. **Optimize images** and compress assets
3. **Use React.lazy** for code splitting
4. **Implement service workers** for caching

## 💰 Step 11: Monetization & Scaling

### 11.1 Pricing Strategy

Current setup supports:
- **Free Tier**: 5 resumes/hour with watermark
- **Premium**: ₹299 one-time for unlimited + no watermark

### 11.2 Payment Processing

The current UPI system with manual verification works for India. To scale globally:

1. **Add Stripe integration** for international payments
2. **Implement subscription billing** for recurring revenue
3. **Add PayPal** for additional payment options

### 11.3 Scaling Considerations

#### When you reach free tier limits:

**Railway Scaling**:
- Upgrade to **Hobby Plan** ($5/month)
- Add **Redis addon** for caching
- Scale to multiple instances

**Vercel Scaling**:
- **Pro Plan** ($20/month) for team features
- Add **Vercel Analytics** for detailed insights

**Supabase Scaling**:
- **Pro Plan** ($25/month) for larger database
- Add **Point-in-time recovery**
- Scale read replicas

## 📈 Step 12: Marketing & Launch

### 12.1 Pre-Launch Checklist

- [ ] All features working in production
- [ ] Payment flow tested end-to-end
- [ ] Admin panel accessible and working
- [ ] Email notifications functioning
- [ ] Error handling and user feedback
- [ ] Mobile responsiveness verified
- [ ] SEO optimization (meta tags, sitemap)
- [ ] Privacy policy and terms of service
- [ ] Google Analytics setup (optional)

### 12.2 Launch Strategy

1. **Soft Launch**: Share with friends and collect feedback
2. **Product Hunt**: Submit for wider visibility
3. **Social Media**: Share on Twitter, LinkedIn
4. **Content Marketing**: Write about AI resume optimization
5. **SEO**: Target keywords like "ATS-friendly resume generator"

### 12.3 Success Metrics

Track these KPIs post-launch:
- **User acquisition rate**
- **Resume generation volume**
- **Premium conversion rate**
- **User retention**
- **Customer support tickets**

## 🔄 Step 13: Maintenance & Updates

### 13.1 Regular Maintenance Tasks

**Weekly**:
- Review payment approval queue
- Monitor error rates and performance
- Check free tier usage limits

**Monthly**:
- Review user feedback and feature requests
- Update AI prompts based on user success
- Analyze conversion funnel and optimize

**Quarterly**:
- Security audit and dependency updates
- Performance optimization review
- Infrastructure cost analysis

### 13.2 Feature Roadmap

Potential features to add:
1. **Multiple resume templates**
2. **Cover letter generation**
3. **LinkedIn profile optimization**
4. **Job application tracking**
5. **Interview preparation AI**
6. **Resume scoring and feedback**

## 📞 Step 14: Support & Community

### 14.1 Customer Support

Set up support channels:
- **Email**: admin@yourdomain.com
- **Help documentation**: Create a knowledge base
- **FAQ section**: Address common questions
- **Status page**: For service updates

### 14.2 Legal Considerations

Important legal documents to create:
- **Privacy Policy**: How you handle user data
- **Terms of Service**: Usage rules and limitations
- **Refund Policy**: For premium payments
- **Cookie Policy**: If using analytics

## 🎉 Congratulations!

You now have a fully functional, production-ready TailorCV application running on free cloud infrastructure!

Your architecture:
- ✅ **Frontend**: Deployed on Vercel
- ✅ **Backend**: Running on Railway
- ✅ **Database**: Hosted on Supabase
- ✅ **AI**: Powered by OpenRouter
- ✅ **Payments**: UPI with manual verification
- ✅ **Email**: FormSubmit notifications
- ✅ **Monitoring**: Built-in dashboards

## 🆘 Need Help?

If you encounter issues:

1. **Check the logs** in Railway and Vercel dashboards
2. **Verify environment variables** are set correctly
3. **Test each service individually** (database, AI, email)
4. **Review the troubleshooting sections** above
5. **Check GitHub issues** for similar problems

Remember: You're running entirely on free tiers, so be mindful of usage limits and scale up when needed!

---

**🚀 Your TailorCV application is now live and ready to help people land their dream jobs!**