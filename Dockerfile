FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium chromium-driver ca-certificates \
        fonts-liberation fonts-noto-color-emoji \
        libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
        libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
        libgbm1 libasound2 libpango-1.0-0 libpangocairo-1.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

ENV CHROME_BIN=/usr/bin/chromium \
    webdriver.chrome.disableBuildCheck=true \
    PYTHONUNBUFFERED=1

COPY . .

CMD ["python", "bot.py"]
