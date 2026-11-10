from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("social", "0001_initial")]
    operations = [migrations.CreateModel(
        name="SiteConfiguration",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("site_title", models.CharField(default="ایران فردا | رسانه معلمان ایران", max_length=100, verbose_name="عنوان سایت")),
            ("hero_title", models.CharField(default="صدای جامعه معلمان،", max_length=180, verbose_name="تیتر اصلی")),
            ("hero_highlight", models.CharField(default="برای فردای بهتر", max_length=180, verbose_name="ادامه تیتر اصلی")),
            ("hero_description", models.TextField(default="ایران فردا فضایی برای گفتگو، انتشار تجربه‌ها، هم‌اندیشی و ارتباط میان معلمان و فعالان آموزشی است.", max_length=600, verbose_name="توضیح معرفی")),
            ("feed_title", models.CharField(default="تازه‌ترین نوشته‌ها", max_length=100, verbose_name="عنوان فید")),
            ("about_title", models.CharField(default="درباره ایران فردا", max_length=100, verbose_name="عنوان ستون درباره ما")),
            ("about_text", models.TextField(default="این فضا برای شنیده‌شدن دیدگاه‌ها، تبادل تجربه و شکل‌گیری ارتباط‌های حرفه‌ای در جامعه آموزشی ایجاد شده است.", max_length=600, verbose_name="متن درباره ما")),
            ("features_title", models.CharField(default="قابلیت‌های جامعه", max_length=100, verbose_name="عنوان امکانات")),
            ("features_text", models.TextField(default="انتشار تجربه و محتوای آموزشی\nگفتگو و تبادل نظر\nدنبال‌کردن همکاران\nدسترسی به پروفایل و اعلان‌ها", verbose_name="امکانات؛ هر مورد در یک خط")),
            ("footer_text", models.CharField(default="ایران فردا؛ رسانه معلمان ایران", max_length=180, verbose_name="متن پابرگ")),
            ("show_hero", models.BooleanField(default=True, verbose_name="نمایش بخش معرفی")),
            ("show_about", models.BooleanField(default=True, verbose_name="نمایش ستون درباره ما")),
            ("show_features", models.BooleanField(default=True, verbose_name="نمایش فهرست امکانات")),
            ("show_join", models.BooleanField(default=True, verbose_name="نمایش دعوت به عضویت")),
            ("updated_at", models.DateTimeField(auto_now=True)),
        ],
        options={"verbose_name": "تنظیمات ظاهر سایت", "verbose_name_plural": "تنظیمات ظاهر سایت"},
    )]
