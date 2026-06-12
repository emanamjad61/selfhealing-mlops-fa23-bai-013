FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir flask==3.0.3 requests==2.32.3 prometheus-client==0.20.0

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
