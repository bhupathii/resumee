# TailorCV Backend Production Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - build-essential: For building Python packages
# - curl: For healthchecks
# - libjpeg-dev, zlib1g-dev: For Pillow image processing
# - texlive packages: For LaTeX PDF generation
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libjpeg-dev \
    zlib1g-dev \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY tailorcv-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application code
COPY tailorcv-backend/ ./

# Set environment variables for the container
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
# The PORT variable is set by Railway, but we provide a default
ENV PORT=5000

# Expose the port the app runs on
EXPOSE 5000

# Health check with a more generous startup period
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start the application using Gunicorn (production server)
# Railway will pass the correct $PORT. We use 2 workers.
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2", "app:app"]