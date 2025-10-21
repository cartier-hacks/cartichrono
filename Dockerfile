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
    pkg-config \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Timezone matchup
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy requirements file
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt

# Copy application files
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Run the bot
CMD ["python", "master.py"]