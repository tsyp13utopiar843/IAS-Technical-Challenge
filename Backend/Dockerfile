FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install agent-specific requirements
COPY agents/maint/requirements.txt agents/maint/requirements.txt
COPY agents/energy/requirements.txt agents/energy/requirements.txt
COPY agents/cyber/requirements.txt agents/cyber/requirements.txt
COPY agents/safety/requirements.txt agents/safety/requirements.txt
COPY agents/ppe/requirements.txt agents/ppe/requirements.txt
COPY agents/backlog/requirements.txt agents/backlog/requirements.txt
COPY agents/orchestrator/requirements.txt agents/orchestrator/requirements.txt
COPY agents/planner/requirements.txt agents/planner/requirements.txt

# Install all agent requirements
RUN pip install --no-cache-dir -r agents/maint/requirements.txt && \
    pip install --no-cache-dir -r agents/energy/requirements.txt && \
    pip install --no-cache-dir -r agents/cyber/requirements.txt && \
    pip install --no-cache-dir -r agents/safety/requirements.txt && \
    pip install --no-cache-dir -r agents/ppe/requirements.txt && \
    pip install --no-cache-dir -r agents/backlog/requirements.txt && \
    pip install --no-cache-dir -r agents/orchestrator/requirements.txt && \
    pip install --no-cache-dir -r agents/planner/requirements.txt || true

# Copy application code
COPY . .

# Create necessary directories for state and logs
RUN mkdir -p agents/maint/state \
    agents/energy/state \
    agents/cyber/state \
    agents/safety/state \
    agents/ppe/state \
    agents/backlog/state

# Expose the main orchestrator port (Railway will assign a public port)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/status', timeout=5)" || exit 1

# Use railway_main.py to run all services in monolith mode
# This is optimized for Railway's single-container deployment
CMD ["python", "railway_main.py"]
