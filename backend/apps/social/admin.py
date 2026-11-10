"""ثبت مدل‌های شبکه اجتماعی در پنل مدیریت Django."""
from django.contrib import admin
from .models import Post, Like, Comment, Follow, Notification, Report, SiteConfiguration, Bookmark

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # فهرست پست‌ها همراه نویسنده، تاریخ و وضعیت نمایش
    list_display = ("id", "author", "created_at", "is_hidden", "views_count")
    list_filter = ("is_hidden", "created_at")
    search_fields = ("content", "author__username")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # امکان جست‌وجو و بررسی نظرات کاربران
    list_display = ("id", "author", "post", "created_at")
    search_fields = ("content", "author__username")

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    # فهرست لایک‌ها برای نظارت مدیریتی
    list_display = ("id", "user", "post", "created_at")

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    # مشاهده روابط دنبال‌کردن کاربران
    list_display = ("id", "follower", "following", "created_at")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # امکان مشاهده و بررسی اعلان‌های سامانه
    list_display = ("id", "recipient", "actor", "kind", "is_read", "created_at")

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    # مدیریت گزارش‌های ارسال‌شده توسط کاربران
    list_display = ("id", "reporter", "post", "is_resolved", "created_at")
    list_filter = ("is_resolved", "created_at")


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    fieldsets = (
        ("عنوان‌ها و معرفی", {"fields": ("site_title", "hero_title", "hero_highlight", "hero_description", "feed_title")} ),
        ("ستون کناری", {"fields": ("about_title", "about_text", "features_title", "features_text")} ),
        ("نمایش بخش‌ها", {"fields": ("show_hero", "show_about", "show_features", "show_join")} ),
        ("پابرگ", {"fields": ("footer_text",)}),
        ("سربرگ و لوگو", {"fields": ("header_logo", "header_logo_width", "header_logo_position", "header_background")} ),
    )

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Bookmark)
