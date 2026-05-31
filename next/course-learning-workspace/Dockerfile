FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    fonts-dejavu \
    fonts-noto-cjk \
    libreoffice-calc \
    libreoffice-impress \
    libreoffice-writer \
    poppler-utils \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir notebooklm-py==0.6.0

COPY app ./app
COPY web ./web

ENV CLW_HOST=0.0.0.0
ENV CLW_PORT=8780
ENV CLW_DATA_DIR=/data
ENV NOTEBOOKLM_HOME=/data/notebooklm

EXPOSE 8780

CMD ["python", "-m", "app.server"]
