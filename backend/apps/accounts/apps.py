from django.apps import AppConfig

class AccountsConfig(AppConfig):
    # تنظیمات اپلیکیشن کاربران و تعیین نوع کلید اصلی
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = "مدیریت کاربران"
