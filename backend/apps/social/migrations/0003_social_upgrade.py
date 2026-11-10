from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("social", "0002_siteconfiguration")]
    operations = [
        migrations.AddField(model_name="post", name="video", field=models.FileField(blank=True, null=True, upload_to="posts/videos/", verbose_name="ویدئوی پست")),
        migrations.AddField(model_name="post", name="repost_of", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reposts", to="social.post", verbose_name="بازنشرِ پست")),
        migrations.AddField(model_name="comment", name="parent", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="replies", to="social.comment", verbose_name="پاسخ به نظر")),
        migrations.CreateModel(name="Bookmark", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("created_at", models.DateTimeField(auto_now_add=True)), ("post", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookmarks", to="social.post")), ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookmarks", to=settings.AUTH_USER_MODEL))], options={"constraints": [models.UniqueConstraint(fields=("user", "post"), name="unique_user_post_bookmark")]}),
        migrations.AlterField(model_name="report", name="reason", field=models.CharField(choices=[("spam", "هرزنامه یا تبلیغات"), ("abuse", "توهین یا آزار"), ("misinformation", "اطلاعات نادرست"), ("violence", "خشونت یا محتوای نامناسب"), ("copyright", "نقض حق نشر"), ("other", "سایر")], max_length=32, verbose_name="دلیل گزارش")),
        migrations.AddField(model_name="report", name="details", field=models.CharField(blank=True, max_length=500, verbose_name="توضیحات تکمیلی")),
        migrations.AddField(model_name="siteconfiguration", name="header_logo", field=models.ImageField(blank=True, null=True, upload_to="branding/", verbose_name="لوگوی سربرگ")),
        migrations.AddField(model_name="siteconfiguration", name="header_logo_width", field=models.PositiveSmallIntegerField(default=220, verbose_name="عرض لوگو")),
        migrations.AddField(model_name="siteconfiguration", name="header_logo_position", field=models.CharField(choices=[("right", "راست"), ("center", "وسط"), ("left", "چپ")], default="right", max_length=10, verbose_name="جایگاه لوگو")),
        migrations.AddField(model_name="siteconfiguration", name="header_background", field=models.CharField(default="#ffffff", max_length=20, verbose_name="رنگ پس‌زمینه سربرگ")),
    ]
