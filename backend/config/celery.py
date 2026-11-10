"""تنظیم Celery برای اجرای کارهای زمان‌بر خارج از درخواست کاربر."""
import os
from celery import Celery

# معرفی فایل تنظیمات جنگو به Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("iran_farda")
# دریافت تنظیمات صف پردازش از فایل settings.py با پیشوند CELERY
app.config_from_object("django.conf:settings", namespace="CELERY")
# بارگذاری خودکار taskها از اپلیکیشن‌های ثبت‌شده جنگو
app.autodiscover_tasks()
