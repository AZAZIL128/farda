"""سریالایزرهای ثبت‌نام، اطلاعات عمومی کاربر و ویرایش پروفایل."""
from django.contrib.auth import get_user_model, password_validation, authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AbsoluteImageField(serializers.ImageField):
    """فیلد تصویرِ قابل‌نوشتن که نشانی کامل فایل را در پاسخ API برمی‌گرداند."""
    def to_representation(self, value):
        if not value:
            return None
        url = value.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url


User = get_user_model()

class PublicUserSerializer(serializers.ModelSerializer):
    # نشانی کامل تصویرها تا در سربرگ، پروفایل و نوشته‌ها پس از تازه‌سازی نیز درست بارگذاری شوند.
    avatar = AbsoluteImageField(required=False, allow_null=True)
    cover = AbsoluteImageField(required=False, allow_null=True)

    # تعداد دنبال‌کنندگان و دنبال‌شوندگان بدون افشای اطلاعات خصوصی
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    def get_followers_count(self, obj):
        # شمارش دنبال‌کنندگان در پروفایل عمومی
        return obj.followers.count()

    def get_following_count(self, obj):
        # شمارش افرادی که این کاربر دنبال می‌کند
        return obj.following.count()

    def get_posts_count(self, obj):
        # شمارش پست‌های منتشرشده توسط کاربر
        return obj.posts.count()

    class Meta:
        model = User
        fields = ["id", "username", "display_name", "bio", "avatar", "cover", "is_verified", "date_joined", "followers_count", "following_count", "posts_count"]


class MeSerializer(serializers.ModelSerializer):
    # نشانی کامل تصاویر پروفایل در GET و PATCH برگردانده می‌شود تا مرورگر مسیر را اشتباه تفسیر نکند.
    avatar = AbsoluteImageField(required=False, allow_null=True)
    cover = AbsoluteImageField(required=False, allow_null=True)

    # اطلاعات کامل‌تر فقط برای صاحب حساب نمایش داده می‌شود.
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    def get_followers_count(self, obj):
        # تعداد دنبال‌کنندگان حساب جاری
        return obj.followers.count()

    def get_following_count(self, obj):
        # تعداد دنبال‌شوندگان حساب جاری
        return obj.following.count()

    def get_posts_count(self, obj):
        # تعداد پست‌های حساب جاری
        return obj.posts.count()

    def validate_avatar(self, value):
        # جلوگیری از بارگذاری تصویر پروفایل بزرگ‌تر از ۵ مگابایت
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("حجم تصویر پروفایل نباید بیشتر از ۵ مگابایت باشد.")
        return value

    def validate_cover(self, value):
        # جلوگیری از بارگذاری تصویر پس‌زمینه بزرگ‌تر از ۵ مگابایت
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("حجم تصویر پس‌زمینه نباید بیشتر از ۵ مگابایت باشد.")
        return value

    class Meta:
        model = User
        fields = ["id", "username", "email", "display_name", "bio", "avatar", "cover", "is_verified", "is_suspended", "is_staff", "is_superuser", "followers_count", "following_count", "posts_count"]
        read_only_fields = ["id", "username", "is_verified", "is_suspended", "is_staff", "is_superuser"]

class RegisterSerializer(serializers.ModelSerializer):
    # فیلدهای یکتا با پیام‌های فارسی و روشن برای کاربر
    username = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    # رمز عبور ساده‌تر: حداقل ۸ نویسه و نه صرفاً عدد
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["username", "email", "display_name", "password"]

    def validate_username(self, value):
        # نام کاربری حداکثر ۳۰ نویسه است و فقط حروف، عدد و زیرخط می‌پذیرد.
        if len(value) > 30 or not value.replace("_", "").isalnum():
            raise serializers.ValidationError("نام کاربری باید حداکثر ۳۰ نویسه و شامل حروف، عدد یا زیرخط باشد.")
        normalized = value.lower()
        if User.objects.filter(username__iexact=normalized).exists():
            raise serializers.ValidationError("این نام کاربری قبلاً ثبت شده است؛ نام دیگری انتخاب کنید.")
        return normalized

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value.strip()).exists():
            raise serializers.ValidationError("این ایمیل قبلاً در ایران فردا ثبت شده است.")
        return value.strip().lower()

    def validate_password(self, value):
        # ثبت‌نام ساده‌تر: حداقل ۸ نویسه؛ رمز عددیِ صرف پذیرفته نمی‌شود.
        if value.isdigit():
            raise serializers.ValidationError("رمز عبور نباید فقط از عدد تشکیل شده باشد؛ ترکیبی از حروف و عدد انتخاب کنید.")
        if len(value.strip()) < 8:
            raise serializers.ValidationError("رمز عبور باید حداقل ۸ نویسه داشته باشد.")
        return value

    def create(self, validated_data):
        # ساخت حساب با متد create_user برای hash شدن رمز عبور
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class IranFardaTokenSerializer(TokenObtainPairSerializer):
    # جلوگیری از ورود حساب‌هایی که مدیر سامانه آن‌ها را تعلیق کرده است.
    def validate(self, attrs):
        username = str(attrs.get("username", "")).strip().lower()
        password = attrs.get("password", "")
        candidate = User.objects.filter(username__iexact=username).first()
        if not candidate:
            raise AuthenticationFailed({"username": "چنین نام کاربری‌ای در سایت ثبت نشده است."})
        if not candidate.check_password(password):
            raise AuthenticationFailed({"password": "رمز عبور واردشده اشتباه است."})
        if not candidate.is_active:
            raise AuthenticationFailed("این حساب غیرفعال است.")
        if candidate.is_suspended:
            raise AuthenticationFailed("این حساب کاربری توسط مدیر سامانه تعلیق شده است.")
        attrs["username"] = username
        return super().validate(attrs)
