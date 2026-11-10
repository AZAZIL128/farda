#!/bin/sh
# این فایل در هر بار اجرای کانتینر، بک‌اند را بدون دستور دستی آماده می‌کند.
set -e

# منتظر می‌مانیم پایگاه داده PostgreSQL آماده اتصال شود.
echo "در انتظار آماده‌شدن PostgreSQL..."
until python -c "import os, psycopg; psycopg.connect(host=os.getenv('POSTGRES_HOST','db'), port=os.getenv('POSTGRES_PORT','5432'), dbname=os.getenv('POSTGRES_DB','iranfarda'), user=os.getenv('POSTGRES_USER','iranfarda'), password=os.getenv('POSTGRES_PASSWORD','change-this-db-password')).close()"; do
  sleep 2
done

# migrationهای نسخه‌بندی‌شده داخل سورس اعمال می‌شوند.
python manage.py migrate --noinput

# ساخت خودکار مدیر اصلی؛ این فرمان داخل entrypoint اجرا می‌شود و دستی نیست.
python manage.py bootstrap_admin

# جمع‌آوری فایل‌های استاتیک پنل مدیریت Django
python manage.py collectstatic --noinput

# اجرای برنامه با Gunicorn به‌عنوان سرور WSGI
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
