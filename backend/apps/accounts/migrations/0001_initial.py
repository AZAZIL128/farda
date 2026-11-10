# migration اولیه مدل کاربر اختصاصی ایران فردا؛ باید پیش از اپلیکیشن اجتماعی اجرا شود.
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]
    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("username", models.CharField(error_messages={"unique": "A user with that username already exists."}, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.", max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name="username")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="ایمیل")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("display_name", models.CharField(blank=True, max_length=80, verbose_name="نام نمایشی")),
                ("bio", models.CharField(blank=True, max_length=280, verbose_name="درباره من")),
                ("avatar", models.ImageField(blank=True, null=True, upload_to="avatars/", verbose_name="تصویر پروفایل")),
                ("cover", models.ImageField(blank=True, null=True, upload_to="covers/", verbose_name="تصویر پس‌زمینه")),
                ("is_verified", models.BooleanField(default=False, verbose_name="نشان تأیید")),
                ("is_suspended", models.BooleanField(default=False, verbose_name="حساب تعلیق شده")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ عضویت")),
                ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
                ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
            ],
            options={"verbose_name": "کاربر", "verbose_name_plural": "کاربران", "ordering": ["-date_joined"]},
            managers=[("objects", django.contrib.auth.models.UserManager())],
        ),
    ]
