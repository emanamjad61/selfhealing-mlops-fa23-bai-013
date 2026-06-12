FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/opt/huggingface \
    HF_HOME=/opt/huggingface

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.3.0+cpu \
    && pip install --no-cache-dir \
        flask==3.0.3 \
        transformers==4.41.2 \
        prometheus-client==0.20.0 \
        requests==2.32.3 \
        pytest==8.2.2 \
        selenium==4.21.0

RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')"

COPY . .
RUN mkdir -p /app/logs

EXPOSE 5000
CMD ["python", "app.py"]
