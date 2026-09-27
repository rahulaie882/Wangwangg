FROM python:3.10-slim

# Playwright/Chromium ke liye zaroori system dependencies install karna
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatk1.0-0 \
    libdbus-1-3 \
    libdrm2 \
    libexpat1 \
    libglib2.0-0 \
    libnspr4 \
    libx11-6 \
    libxcb1 \
    libxcursor1 \
    libxi6 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies install karna
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright browser aur uski dependencies download karna
RUN playwright install chromium
RUN playwright install-deps chromium

# Baaki saara code copy karna
COPY . .

# Bot run karne ki command
CMD ["python", "bot.py"]
