# افزودن تنظیم سقف واژه‌های پست بدون تغییر یا حذف اطلاعات قبلی
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("social", "0005_interactions_customization")]
    operations = [
        migrations.AlterField(
            model_name="post",
            name="content",
            field=models.TextField(blank=True, max_length=50000, verbose_name="متن پست"),
        ),
        migrations.AddField(
            model_name="siteconfiguration",
            name="post_max_words",
            field=models.PositiveSmallIntegerField(default=500, verbose_name="حداکثر واژه‌های هر پست"),
        ),
    ]
