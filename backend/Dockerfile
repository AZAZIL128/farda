FROM python:3.9-slim

WORKDIR /app

# نصب پکیج‌های سیستمی با تایم‌اوت بالا (چون اینترنت مستقیم است ممکن است کند باشد)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev libjpeg62-turbo-dev zlib1g-dev netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
