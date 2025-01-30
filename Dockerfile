FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p models

COPY bot/ bot/
COPY utils/ utils/
COPY main.py .
COPY config.py .

CMD ["python", "main.py"] 