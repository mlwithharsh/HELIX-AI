FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-rl.txt /app/requirements-rl.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements-rl.txt

COPY model /app/model
COPY rl /app/rl
COPY memory /app/memory
COPY tests /app/tests
COPY train_rl.py /app/train_rl.py
COPY evaluate_rl.py /app/evaluate_rl.py

CMD ["python", "train_rl.py", "--model-name", "distilgpt2", "--epochs", "1"]
