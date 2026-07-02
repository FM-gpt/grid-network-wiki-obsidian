# GRID Wiki Dashboard Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dashboard files
COPY dashboard/ /app/dashboard/
COPY wiki-content/ /app/wiki-content/
COPY wiki/ /app/wiki/

# Install minimal dependencies
RUN pip install --no-cache-dir jinja2

# Create non-root user
RUN adduser --disabled-password --gecos '' wikiuser
USER wikiuser

# Expose ports
EXPOSE 8082
EXPOSE 8083

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8082/')" || exit 1

# Default command
CMD ["python3", "-m", "http.server", "8082", "--directory", "/app/dashboard"]
