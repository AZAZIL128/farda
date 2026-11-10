from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [migrations.CreateModel(
        name="UserPreference",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("show_hero", models.BooleanField(default=True)),
            ("show_sidebar", models.BooleanField(default=True)),
            ("show_about", models.BooleanField(default=True)),
            ("show_features", models.BooleanField(default=True)),
            ("compact_feed", models.BooleanField(default=False)),
            ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="preferences", to=settings.AUTH_USER_MODEL)),
        ],
        options={"verbose_name": "تنظیمات نمایش کاربر", "verbose_name_plural": "تنظیمات نمایش کاربران"},
    )]
