# TailorCV - AI-Powered Resume Generator

TailorCV is a complete, production-ready web application that generates tailored, ATS-friendly resumes using AI. Users can input their LinkedIn profile or upload a resume, paste a job description, and get a professionally formatted PDF resume optimized for that specific job.

## 🚀 Features

- **AI-Powered Resume Optimization**: Uses OpenRouter API with DeepSeek/Mistral models
- **ATS-Friendly Templates**: Professional LaTeX templates that pass Applicant Tracking Systems
- **Multiple Input Methods**: LinkedIn URL or PDF resume upload
- **Premium Features**: Watermark-free resumes, premium templates, unlimited generations
- **UPI Payment System**: Manual verification via screenshot upload
- **Email Notifications**: Automated email delivery using FormSubmit
- **Rate Limiting**: Prevents abuse with IP-based rate limiting
- **Mobile Responsive**: Works perfectly on all devices

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **React Router** for navigation
- **Lucide React** for icons

### Backend
- **Flask** Python web framework
- **OpenRouter API** for AI resume optimization
- **Supabase** for database and storage
- **LaTeX** for PDF generation
- **FormSubmit** for email notifications

### Infrastructure
- **Frontend**: Vercel (free tier)
- **Backend**: Railway (free tier)
- **Database**: Supabase (free tier)
- **Storage**: Supabase Storage (free tier)
- **AI**: OpenRouter (free tier)

## 📋 Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- LaTeX distribution (TeX Live or MiKTeX)
- Supabase account
- OpenRouter API key

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/tailorcv.git
cd tailorcv
```

### 2. Set Up Frontend

```bash
cd tailorcv-frontend
npm install
```

### 3. Set Up Backend

```bash
cd ../tailorcv-backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables

#### Backend (.env)
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
ADMIN_EMAIL=admin@tailorcv.com
DEBUG=False
PORT=5000
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:5000
```

### 5. Set Up Database

1. Create a Supabase project
2. Run the SQL commands from `tailorcv-backend/database/schema.sql`
3. Create storage buckets: `resumes` (public) and `payments` (private)
4. Follow the setup instructions in `tailorcv-backend/database/setup_instructions.md`

### 6. Install LaTeX

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra texlive-xetex
```

**macOS:**
```bash
brew install --cask mactex
```

**Windows:**
Download and install MiKTeX from https://miktex.org/

## 🚀 Running the Application

### Development Mode

#### Backend
```bash
cd tailorcv-backend
python app.py
```

#### Frontend
```bash
cd tailorcv-frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

### Production Mode

#### Backend
```bash
cd tailorcv-backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Frontend
```bash
cd tailorcv-frontend
npm run build
```

## 🌐 Deployment

### Frontend (Vercel)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set environment variables in Vercel dashboard:
   - `REACT_APP_API_URL=https://your-backend-url.com`
4. Deploy

### Backend (Railway)

1. Push your code to GitHub
2. Connect your repository to Railway
3. Set environment variables in Railway dashboard
4. Deploy

### Database (Supabase)

1. Create a Supabase project
2. Run the database schema
3. Configure storage buckets
4. Set up RLS policies

## 📊 Usage

### For Users

1. **Generate Resume**: 
   - Visit the website
   - Choose LinkedIn URL or upload PDF
   - Paste job description
   - Click "Generate Resume"

2. **Upgrade to Premium**:
   - Go to payment page
   - Pay ₹299 via UPI
   - Upload payment screenshot
   - Wait for manual verification (24 hours)

### For Admins

1. **Payment Verification**:
   - Check email notifications for new payments
   - Review payment screenshots
   - Update payment status in Supabase dashboard

2. **User Management**:
   - View user statistics in Supabase
   - Monitor generation counts
   - Handle premium upgrades

## 🎨 Customization

### Adding New Templates

1. Create a new LaTeX template in `tailorcv-backend/templates/`
2. Update the `LaTeXService` to include the new template
3. Add template selection logic in the frontend

### Modifying AI Prompts

Edit the prompts in `tailorcv-backend/services/openrouter_service.py` to customize how the AI optimizes resumes.

### Styling Changes

Modify the Tailwind classes in the React components to change the appearance.

## 🔒 Security Features

- **Rate Limiting**: Prevents abuse with IP-based limits
- **Input Validation**: Sanitizes all user inputs
- **File Upload Security**: Validates file types and sizes
- **Row Level Security**: Supabase RLS policies protect user data
- **Environment Variables**: Sensitive data stored securely

## 📈 Monitoring

### Key Metrics

- Daily active users
- Resume generation counts
- Payment conversion rates
- System performance metrics

### Database Queries

```sql
-- View user statistics
SELECT * FROM user_stats;

-- View payment statistics
SELECT * FROM payment_stats;

-- View daily activity
SELECT * FROM daily_activity LIMIT 30;
```

## 🐛 Troubleshooting

### Common Issues

1. **LaTeX Compilation Errors**:
   - Ensure LaTeX is properly installed
   - Check template syntax
   - Verify file permissions

2. **API Rate Limits**:
   - Monitor OpenRouter usage
   - Implement request queuing if needed

3. **Database Connection Issues**:
   - Verify Supabase credentials
   - Check network connectivity
   - Review RLS policies

### Debug Mode

Enable debug mode in the backend:
```env
DEBUG=True
```

### Log Files

Check application logs for detailed error information:
```bash
tail -f /var/log/tailorcv/app.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenRouter for AI API access
- Supabase for backend infrastructure
- Vercel for frontend hosting
- Railway for backend hosting
- LaTeX community for templating

## 📞 Support

For support, email admin@tailorcv.com or create an issue in the GitHub repository.

---

**Built with ❤️ by the TailorCV Team**# resumee
