#!/bin/bash

# TailorCV Setup Script
echo "🚀 Setting up TailorCV..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📦 Installing frontend dependencies..."
cd tailorcv-frontend
npm install
cd ..

echo "🐍 Installing backend dependencies..."
cd tailorcv-backend
pip install -r requirements.txt
cd ..

echo "📋 Setting up environment files..."
if [ ! -f "tailorcv-backend/.env" ]; then
    cp tailorcv-backend/.env.example tailorcv-backend/.env
    echo "✅ Created backend .env file - please edit it with your credentials"
fi

if [ ! -f "tailorcv-frontend/.env" ]; then
    cp tailorcv-frontend/.env.example tailorcv-frontend/.env
    echo "✅ Created frontend .env file - please edit it with your API URL"
fi

echo "🔧 Checking LaTeX installation..."
if command -v pdflatex &> /dev/null; then
    echo "✅ LaTeX is installed"
else
    echo "❌ LaTeX is not installed"
    echo "Please install LaTeX:"
    echo "  Ubuntu/Debian: sudo apt-get install texlive-latex-base texlive-latex-recommended texlive-latex-extra"
    echo "  macOS: brew install --cask mactex"
    echo "  Windows: Download and install MiKTeX from https://miktex.org/"
fi

echo "📝 Next steps:"
echo "1. Edit tailorcv-backend/.env with your API keys"
echo "2. Edit tailorcv-frontend/.env with your backend URL"
echo "3. Set up your Supabase database (see database/setup_instructions.md)"
echo "4. Run the backend: cd tailorcv-backend && python app.py"
echo "5. Run the frontend: cd tailorcv-frontend && npm start"

echo "✅ Setup complete!"
echo "📖 Check README.md for detailed instructions"