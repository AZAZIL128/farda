# تنظیم فرم ساخت کاربر و نمایش فیلدهای اختصاصی ایران فردا در پنل Django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from .models import UserPreference
from .models import User


class IranFardaUserCreationForm(UserCreationForm):
    # فرم ساخت کاربر جدید؛ ایمیل در این پروژه الزامی و یکتا است.
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "display_name")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # استفاده از فرم اختصاصی تا هنگام ساخت کاربر، ایمیل نیز ثبت شود.
    add_form = IranFardaUserCreationForm
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "display_name", "password1", "password2"),
        }),
    )

    # فیلدهای اختصاصی ایران فردا در فهرست کاربران و فرم ویرایش
    list_display = ("username", "email", "display_name", "is_verified", "is_suspended", "is_staff")
    list_filter = ("is_verified", "is_suspended", "is_staff", "is_active")
    search_fields = ("username", "email", "display_name")
    fieldsets = tuple((name, {**options, "fields": tuple(f for f in options.get("fields", ()) if f not in ("groups", "user_permissions"))}) for name, options in BaseUserAdmin.fieldsets) + (
        ("اطلاعات ایران فردا", {
            "fields": ("display_name", "bio", "avatar", "cover", "is_verified", "is_suspended"),
        }),
    )


# سامانه در این مرحله قابلیت ساخت گروه کاربری ندارد؛ بخش Groups از پنل حذف می‌شود.
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "show_hero", "show_sidebar", "compact_feed")
    search_fields = ("user__username", "user__email")
