FROM python:3.12-slim

WORKDIR /app

# تنظیم میرور ایرانی برای پکیج‌های سیستمی (دبیان)
RUN sed -i 's|deb.debian.org|mirror.iranserver.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|deb.debian.org|mirror.iranserver.com|g' /etc/apt/sources.list

# نصب پکیج‌های سیستمی
RUN apt-get -o Acquire::Check-Valid-Until=false update && apt-get install -y --no-install-recommends \
    gcc libpq-dev libjpeg62-turbo-dev zlib1g-dev netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# کپی و نصب پکیج‌های پایتون از میرور تسینگ‌هوآ (سریع و بدون تحریم)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

COPY . .

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
