FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m consumer_user
USER consumer_user

CMD ["python", "consumer.py"]
