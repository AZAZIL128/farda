"""نمونه وظایف پس‌زمینه؛ این محل برای اعلان ایمیلی، پاک‌سازی و پردازش‌هاست."""
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from .models import Notification

@shared_task(name="social.cleanup_old_read_notifications")
def cleanup_old_read_notifications(days=180):
    # پاک‌سازی اعلان‌های خوانده‌شده قدیمی برای کنترل رشد دیتابیس
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = Notification.objects.filter(is_read=True, created_at__lt=cutoff).delete()
    return deleted
