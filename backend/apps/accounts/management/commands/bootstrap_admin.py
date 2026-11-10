"""ساخت خودکار مدیر اصلی در اولین راه‌اندازی؛ بدون نیاز به دستور دستی."""
import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError

class Command(BaseCommand):
    help = "ساخت یا اطمینان از وجود مدیر اصلی ایران فردا"

    def handle(self, *args, **options):
        # مشخصات اولیه مدیر از فایل env خوانده می‌شود.
        username = os.getenv("ADMIN_USERNAME", "admin").strip().lower()
        email = os.getenv("ADMIN_EMAIL", "admin@iranfarda.local").strip()
        password = os.getenv("ADMIN_PASSWORD", "")
        if not password:
            raise CommandError("متغیر ADMIN_PASSWORD تنظیم نشده است؛ ابتدا فایل .env را تکمیل کنید.")

        User = get_user_model()
        admin_user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "display_name": "مدیر سامانه"},
        )
        # حساب مدیر همیشه دسترسی مدیریتی دارد، اما رمز کاربر موجود هر بار بازنویسی نمی‌شود.
        admin_user.email = email
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        if created:
            # رمز مدیر تازه‌ساخته‌شده باید از سیاست امنیتی Django عبور کند.
            try:
                password_validation.validate_password(password, user=admin_user)
            except DjangoValidationError as error:
                admin_user.delete()
                raise CommandError("رمز مدیر ضعیف است: " + "; ".join(error.messages)) from error
            admin_user.set_password(password)
            self.stdout.write(self.style.SUCCESS(f"مدیر اولیه {username} ساخته شد."))
        else:
            self.stdout.write(self.style.WARNING(f"حساب مدیر {username} از قبل وجود داشت؛ رمز آن تغییر نکرد."))
        admin_user.save()
