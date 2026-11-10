"""مدل کاربر اختصاصی شبکه اجتماعی ایران فردا."""
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # اطلاعات نمایشی کاربر در پروفایل عمومی
    email = models.EmailField("ایمیل", unique=True)
    display_name = models.CharField("نام نمایشی", max_length=80, blank=True)
    bio = models.CharField("درباره من", max_length=280, blank=True)
    avatar = models.ImageField("تصویر پروفایل", upload_to="avatars/", blank=True, null=True)
    cover = models.ImageField("تصویر پس‌زمینه", upload_to="covers/", blank=True, null=True)

    # وضعیت‌های مدیریتی برای تأیید هویت و محدودسازی حساب‌ها
    is_verified = models.BooleanField("نشان تأیید", default=False)
    is_suspended = models.BooleanField("حساب تعلیق شده", default=False)
    created_at = models.DateTimeField("تاریخ عضویت", auto_now_add=True)

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ["-date_joined"]

    def __str__(self):
        # نام کاربری برای نمایش در پنل مدیریت
        return self.username

class UserPreference(models.Model):
    """تنظیمات شخصی نمایش برای هر حساب کاربری."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preferences")
    show_hero = models.BooleanField(default=True)
    show_sidebar = models.BooleanField(default=True)
    show_about = models.BooleanField(default=True)
    show_features = models.BooleanField(default=True)
    compact_feed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "تنظیمات نمایش کاربر"
        verbose_name_plural = "تنظیمات نمایش کاربران"
