FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim

# Install system dependencies (Tesseract OCR, Poppler for PDFs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

# Environment variables
ENV PYTHONPATH=/app
ENV TESSERACT_CMD=/usr/bin/tesseract

EXPOSE 8000 8501

# Command is typically overridden by docker-compose for individual services
CMD ["python", "scripts/run_dev.py"]
