FROM python:3.11-slim

# Install system dependencies required for PyAudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    libasound2-dev \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy application code (everything in backend folder)
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=10000

# Expose port
EXPOSE $PORT

# Start the application (app.py is now in current directory)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
