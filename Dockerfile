# language: Dockerfile, target: Railway (US West), base: python:3.11-slim
# *Railway builds this in a container with no GPU and no /dev/shm by
#  default — Chrome dies on launch without --disable-dev-shm-usage, which
#  the code already passes. The bigger trap is UC auto-downloading a
#  chromedriver whose version doesn't match this container's chromium —
#  pin both, and turn UC's build check off so it doesn't try to "fix" it.*

FROM python:3.11-slim

# ── system deps: chromium + driver + the fonts/libs Chrome actually needs ──
RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        chromium-driver \
        ca-certificates \
        fonts-liberation \
        fonts-noto-color-emoji \
        libnss3 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libasound2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── python deps first (layer cache) ──
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# ── UC environment: point it at the system chromium, kill the build check ──
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    webdriver.chrome.disableBuildCheck=true \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY . .

CMD ["python", "ig_creator.py"]
