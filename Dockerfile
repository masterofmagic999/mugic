# Dockerfile for easy deployment to any platform
FROM python:3.11-slim

# Set debian frontend to noninteractive to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including Java for Audiveris
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libsndfile1 \
    ffmpeg \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install OpenJDK (required for Audiveris OMR)
# Try multiple versions: 21 (latest in Debian Trixie), 17, or 11
RUN apt-get update && \
    (apt-get install -y --no-install-recommends openjdk-21-jre-headless || \
     apt-get install -y --no-install-recommends openjdk-17-jre-headless || \
     apt-get install -y --no-install-recommends openjdk-11-jre-headless) && \
    rm -rf /var/lib/apt/lists/* && \
    java -version

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-flask.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-flask.txt gunicorn

# Install OEMER without dependencies to avoid onnxruntime-gpu requirement
RUN pip install --no-cache-dir --no-deps oemer==0.1.8

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads recordings

# Download Audiveris (optional - can be mounted as volume)
# Uncomment and modify if you want Audiveris bundled
# RUN wget https://github.com/Audiveris/audiveris/releases/download/5.3.1/Audiveris-5.3.1.tar.gz && \
#     tar -xzf Audiveris-5.3.1.tar.gz && \
#     mv Audiveris-5.3.1 /opt/audiveris && \
#     rm Audiveris-5.3.1.tar.gz

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Health check (using the dedicated /health endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
