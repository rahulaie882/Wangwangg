FROM python:3.12-slim

WORKDIR /app

# Playwright Chromium ke liye zaroori system libraries
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    fonts-noto-color-emoji \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxtst6 \
    libxshmfence1 \
    libwayland-client0 \
    libx11-xcb1 \
    libxcb1 \
    libxkbcommon0 \
    libpangoft2-1.0-0 \
    libxdmcp6 \
    libxcb-dri3-0 \
    libgles2 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright Chromium binary download
RUN playwright install chromium

COPY . .

CMD ["python", "bot.py"]
