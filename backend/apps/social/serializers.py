"""سریالایزرهای پست، نظرات، اعلان‌ها و گزارش‌ها."""
from rest_framework import serializers
from apps.accounts.serializers import PublicUserSerializer
from .models import Post, Comment, Notification, Report

class CommentSerializer(serializers.ModelSerializer):
    # اطلاعات نویسنده و آمار واکنش‌ها برای هر دیدگاه
    author = PublicUserSerializer(read_only=True)
    reaction_counts = serializers.SerializerMethodField()
    my_reactions = serializers.SerializerMethodField()
    def get_reaction_counts(self, obj):
        return {key: obj.reactions.filter(reaction=key).count() for key in ("like", "support", "insightful")}
    def get_my_reactions(self, obj):
        request = self.context.get("request")
        return list(obj.reactions.filter(user=request.user).values_list("reaction", flat=True)) if request and request.user.is_authenticated else []

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "parent", "created_at", "reaction_counts", "my_reactions"]
        read_only_fields = ["id", "author", "created_at"]

class AbsoluteMediaField(serializers.FileField):
    """فیلد رسانهٔ قابل‌بارگذاری که نشانی کامل فایل را در پاسخ می‌دهد."""
    def to_representation(self, value):
        if not value:
            return None
        url = value.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

class AbsoluteImageField(serializers.ImageField):
    """تصویر پست را اعتبارسنجی می‌کند و نشانی کامل آن را برمی‌گرداند."""
    def to_representation(self, value):
        if not value:
            return None
        url = value.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

class PostSerializer(serializers.ModelSerializer):
    # تصویر با اعتبارسنجی نوع فایل و ویدئو به‌صورت فایل عمومی دریافت می‌شوند.
    image = AbsoluteImageField(required=False, allow_null=True)
    video = AbsoluteMediaField(required=False, allow_null=True)

    # اطلاعات نویسنده و آمار تعاملات به‌صورت فقط‌خواندنی نمایش داده می‌شود.
    author = PublicUserSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    is_reported = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "author", "content", "image", "video", "repost_of", "likes_count", "comments_count", "is_liked", "is_bookmarked", "is_reported", "views_count", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "repost_of", "likes_count", "comments_count", "is_liked", "is_bookmarked", "is_reported", "views_count", "created_at", "updated_at"]

    def get_is_liked(self, obj):
        # وضعیت لایک فقط برای کاربر فعلی محاسبه می‌شود.
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.bookmarks.filter(user=request.user).exists())

    def get_is_reported(self, obj):
        # وضعیت گزارش فقط برای کاربر واردشده خودش برگردانده می‌شود.
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and obj.reports.filter(reporter=request.user, is_resolved=False).exists())

    def validate_content(self, value):
        # سقف واژه‌ها از تنظیمات مدیر خوانده می‌شود و در API نیز enforce می‌شود.
        from .models import SiteConfiguration
        maximum = SiteConfiguration.current().post_max_words
        words = len(value.split())
        if words > maximum:
            raise serializers.ValidationError(f"متن پست حداکثر می‌تواند {maximum} واژه داشته باشد؛ تعداد فعلی {words} واژه است.")
        return value

    def validate_video(self, value):
        # کنترل نوع و حجم فایل ویدئویی قبل از ذخیره در فضای رسانه.
        if value and value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError("حجم ویدئو نباید بیشتر از ۱۰۰ مگابایت باشد.")
        if value and not value.name.lower().endswith((".mp4", ".webm", ".mov", ".m4v")):
            raise serializers.ValidationError("فرمت ویدئو باید MP4، WebM یا MOV باشد.")
        return value

    def validate_image(self, value):
        # سقف حجم تصویر پست ۱۰ مگابایت است؛ ImageField فرمت واقعی تصویر را نیز بررسی می‌کند.
        if value and value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("حجم تصویر پست نباید بیشتر از ۱۰ مگابایت باشد.")
        return value

class NotificationSerializer(serializers.ModelSerializer):
    # فرستنده اعلان در صورت وجود به‌صورت خلاصه نمایش داده می‌شود.
    actor = PublicUserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "actor", "kind", "text", "is_read", "created_at"]

class ReportSerializer(serializers.ModelSerializer):
    # ایجادکننده گزارش و وضعیت رسیدگی در API عمومی قابل جعل نیست.
    def validate(self, attrs):
        if attrs.get("reason") == "other" and not attrs.get("details", "").strip():
            raise serializers.ValidationError({"details": "برای گزینه سایر، توضیح کوتاه الزامی است."})
        return attrs
    class Meta:
        model = Report
        fields = ["id", "post", "reason", "details", "is_resolved", "created_at"]
        read_only_fields = ["id", "is_resolved", "created_at"]
