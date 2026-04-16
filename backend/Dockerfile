FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies without caching pip files
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/

# Transfer ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port 8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Default command
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
