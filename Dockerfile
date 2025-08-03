# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Expose Streamlit port
EXPOSE 8547

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8547/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8547", "--server.address=0.0.0.0"]
