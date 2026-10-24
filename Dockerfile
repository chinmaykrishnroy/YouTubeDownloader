# =============================================================================
# Production Dockerfile for YouTube Downloader
# =============================================================================
FROM python:3.11-slim-bookworm

# Install FFmpeg (required for high quality video/audio muxing and MP3 encoding)
# and curl (for container health checking)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cache dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create downloads directory
RUN mkdir -p /app/downloads

# Verify mandatory dependencies and build-time components
RUN python scripts/preflight_check.py --build-time

# Expose default port
EXPOSE 8000

# Periodic health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/system-status || exit 1

# Pre-flight check on start: verify yt-dlp and network connectivity before launching server
CMD ["sh", "-c", "python scripts/preflight_check.py --skip-network && python main.py"]
