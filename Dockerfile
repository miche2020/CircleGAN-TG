FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY model.pkl .
COPY bot.py .
COPY .env .
COPY utils/ ./utils/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"] 