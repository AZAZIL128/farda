# این فایل باعث می‌شود بسته تنظیمات پروژه به‌عنوان یک ماژول پایتون شناخته شود.
from .celery import app as celery_app

__all__ = ("celery_app",)
