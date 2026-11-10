from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("social", "0003_social_upgrade")]
    operations = [
        migrations.AddField("siteconfiguration", "bottom_nav_background", models.CharField(default="#ffffff", max_length=20, verbose_name="رنگ پس‌زمینه منوی پایین")),
        migrations.AddField("siteconfiguration", "bottom_nav_color", models.CharField(default="#7b8297", max_length=20, verbose_name="رنگ آیکون‌های منوی پایین")),
        migrations.AddField("siteconfiguration", "bottom_nav_active_color", models.CharField(default="#34479D", max_length=20, verbose_name="رنگ گزینه فعال منوی پایین")),
        migrations.AddField("siteconfiguration", "bottom_nav_home_label", models.CharField(default="خانه", max_length=30, verbose_name="عنوان خانه در منوی پایین")),
        migrations.AddField("siteconfiguration", "bottom_nav_explore_label", models.CharField(default="اکسپلور", max_length=30, verbose_name="عنوان اکسپلور در منوی پایین")),
        migrations.AddField("siteconfiguration", "bottom_nav_following_label", models.CharField(default="برای شما", max_length=30, verbose_name="عنوان برای شما در منوی پایین")),
    ]
