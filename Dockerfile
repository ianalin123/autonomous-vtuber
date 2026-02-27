FROM python:3.12-slim

WORKDIR /app

# Install system deps for Playwright + FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    xvfb \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install -e ".[dev]"
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .
