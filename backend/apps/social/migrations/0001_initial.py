# migration اولیه مدل‌های اجتماعی؛ پس از ایجاد مدل کاربر اجرا می‌شود.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField(blank=True, max_length=5000, verbose_name="متن پست")),
                ("image", models.ImageField(blank=True, null=True, upload_to="posts/", verbose_name="تصویر پست")),
                ("is_hidden", models.BooleanField(default=False, verbose_name="مخفی شده")),
                ("views_count", models.PositiveIntegerField(default=0, verbose_name="تعداد بازدید")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="زمان انتشار")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="posts", to=settings.AUTH_USER_MODEL, verbose_name="نویسنده")),
            ],
            options={"verbose_name": "پست", "verbose_name_plural": "پست‌ها", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.CharField(max_length=1500, verbose_name="متن نظر")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comments", to=settings.AUTH_USER_MODEL, verbose_name="نویسنده")),
                ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comments", to="social.post", verbose_name="پست")),
            ],
            options={"verbose_name": "نظر", "verbose_name_plural": "نظرات", "ordering": ["created_at"]},
        ),
        migrations.CreateModel(
            name="Follow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="زمان دنبال‌کردن")),
                ("follower", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="following", to=settings.AUTH_USER_MODEL, verbose_name="دنبال‌کننده")),
                ("following", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="followers", to=settings.AUTH_USER_MODEL, verbose_name="دنبال‌شونده")),
            ],
            options={"verbose_name": "دنبال‌کردن", "verbose_name_plural": "دنبال‌کردن‌ها"},
        ),
        migrations.CreateModel(
            name="Like",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="زمان پسندیدن")),
                ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="likes", to="social.post", verbose_name="پست")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="likes", to=settings.AUTH_USER_MODEL, verbose_name="کاربر")),
            ],
            options={"verbose_name": "پسندیدن", "verbose_name_plural": "پسندیدن‌ها"},
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("follow", "دنبال‌کردن"), ("like", "پسندیدن"), ("comment", "نظر جدید"), ("system", "اعلان سامانه")], default="system", max_length=20, verbose_name="نوع اعلان")),
                ("text", models.CharField(max_length=255, verbose_name="متن اعلان")),
                ("is_read", models.BooleanField(default=False, verbose_name="خوانده شده")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="زمان اعلان")),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sent_notifications", to=settings.AUTH_USER_MODEL, verbose_name="انجام‌دهنده")),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL, verbose_name="دریافت‌کننده")),
            ],
            options={"verbose_name": "اعلان", "verbose_name_plural": "اعلان‌ها", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reason", models.CharField(max_length=500, verbose_name="دلیل گزارش")),
                ("is_resolved", models.BooleanField(default=False, verbose_name="رسیدگی شده")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="زمان گزارش")),
                ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reports", to="social.post", verbose_name="پست")),
                ("reporter", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reports_made", to=settings.AUTH_USER_MODEL, verbose_name="گزارش‌دهنده")),
            ],
            options={"verbose_name": "گزارش محتوا", "verbose_name_plural": "گزارش‌های محتوا", "ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(model_name="follow", constraint=models.UniqueConstraint(fields=("follower", "following"), name="unique_follower_following")),
        migrations.AddConstraint(model_name="follow", constraint=models.CheckConstraint(condition=~models.Q(follower=models.F("following")), name="cannot_follow_self")),
        migrations.AddConstraint(model_name="like", constraint=models.UniqueConstraint(fields=("user", "post"), name="unique_user_post_like")),
    ]
