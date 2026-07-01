FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY nerve-center/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY nerve-center/ .

# Create data directory
RUN mkdir -p /app/data /app/logs

# Expose ports
EXPOSE 8765 8766

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8765/health')" || exit 1

# Run
CMD ["python", "run.py"]
