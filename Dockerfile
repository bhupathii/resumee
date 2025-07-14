# TailorCV Backend Dockerfile - Minimal Version
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for LaTeX and other tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY tailorcv-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY tailorcv-backend ./

# Create directory for temporary files
RUN mkdir -p /tmp/tailorcv

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Expose port
EXPOSE 5000

# Health check with longer timeout and more retries
HEALTHCHECK --interval=30s --timeout=15s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Use the minimal app that handles missing dependencies gracefully
CMD ["python", "app_minimal.py"]