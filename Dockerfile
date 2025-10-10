FROM python:3.11-slim

# Install system dependencies for Discord bot (ffmpeg for audio, opus for voice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libopus0 \
    libopus-dev \
    libsodium23 \
    libsodium-dev \
    libffi-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY . .

# Install Python dependencies
RUN python3 -m venv venv
RUN . venv/bin/activate && pip install -r requirements.txt

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Run the bot
ENTRYPOINT ["/bin/bash"]
#CMD ["python", "master.py"]