from django.apps import AppConfig

class SocialConfig(AppConfig):
    # پیکربندی اپلیکیشن شبکه اجتماعی
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.social"
    label = "social"
    verbose_name = "شبکه اجتماعی"
