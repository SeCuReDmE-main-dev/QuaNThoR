FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MIZFILES=/usr/local/share/mizar

RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gzip \
        tar \
        libc6:i386 \
        libgcc-s1:i386 \
        libgmp10:i386 \
        libncurses6:i386 \
        libstdc++6:i386 \
        libtinfo6:i386 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ARG MIZAR_ARCHIVE_URL=https://mizar.uwb.edu.pl/~softadm/pub/system/i386-linux/mizar-8.1.15_5.94.1493-i386-linux.tar

RUN mkdir -p /tmp/mizar \
    && curl -fsSL "$MIZAR_ARCHIVE_URL" -o /tmp/mizar/mizar.tar \
    && tar -xf /tmp/mizar/mizar.tar -C /tmp/mizar \
    && cd /tmp/mizar \
    && sh ./install.sh --default \
    && rm -rf /tmp/mizar

COPY src ./src
COPY scl_guardian ./scl_guardian

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 CMD ["python", "-c", "import sys, urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=4).read(); sys.exit(0)"]

CMD ["python", "src/app.py"]
