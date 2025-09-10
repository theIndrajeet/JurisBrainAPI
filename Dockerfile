# JurisBrain Legal Knowledge API - Docker Configuration
# Multi-stage build for optimized production image

# =============================================================================
# Build Stage
# =============================================================================
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Add metadata
LABEL maintainer="JurisBrain Team <support@jurisbrain.com>" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="JurisBrain Legal Knowledge API" \
      org.label-schema.description="Free and open-source Legal Knowledge API" \
      org.label-schema.url="https://github.com/theIndrajeet/JurisBrainAPI" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/theIndrajeet/JurisBrainAPI" \
      org.label-schema.vendor="JurisBrain" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Production Stage
# =============================================================================
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash jurisbrain

# Set work directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app.py .
COPY .env.example .

# Create directories for data and logs
RUN mkdir -p /app/legal_db /app/logs && \
    chown -R jurisbrain:jurisbrain /app

# Switch to non-root user
USER jurisbrain

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Development Stage (optional)
# =============================================================================
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-asyncio black isort flake8

# Install additional development tools
RUN apt-get update && apt-get install -y \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Switch back to jurisbrain user
USER jurisbrain

# Override command for development (with reload)
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# Build Instructions:
# =============================================================================
# 
# Build production image:
# docker build --target production -t jurisbrain-api:latest .
#
# Build development image:
# docker build --target development -t jurisbrain-api:dev .
#
# Run container:
# docker run -p 8000:8000 -e GOOGLE_AI_API_KEY=your_key jurisbrain-api:latest
#
# Run with volume mount for database:
# docker run -p 8000:8000 -v ./legal_db:/app/legal_db jurisbrain-api:latest
#
# =============================================================================
