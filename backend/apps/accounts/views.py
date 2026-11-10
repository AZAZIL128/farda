"""APIهای حساب کاربری، ثبت‌نام و نمایش پروفایل."""
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, MeSerializer, PublicUserSerializer, IranFardaTokenSerializer
from .models import UserPreference
from rest_framework import serializers
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.exceptions import ValidationError

User = get_user_model()

class LoginTokenView(TokenObtainPairView):
    # ورود JWT با بررسی وضعیت تعلیق حساب
    serializer_class = IranFardaTokenSerializer

class RegisterView(generics.CreateAPIView):
    # ثبت‌نام عمومی؛ نقش مدیریتی از طریق این API قابل تعیین نیست.
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class MeView(generics.RetrieveUpdateAPIView):
    # مشاهده یا ویرایش پروفایل فقط برای کاربر واردشده؛ فرم چندبخشی برای دریافت عکس ضروری است.
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return User.objects.annotate(
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
            posts_count=Count("posts", distinct=True),
        ).get(pk=self.request.user.pk)

class UserSearchView(generics.ListAPIView):
    # جست‌وجوی ساده کاربران فعال بر اساس نام کاربری یا نام نمایشی
    serializer_class = PublicUserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        term = self.request.query_params.get("q", "").strip()
        return User.objects.filter(is_active=True, is_suspended=False).filter(
            Q(username__icontains=term) | Q(display_name__icontains=term)
        ).annotate(
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
            posts_count=Count("posts", distinct=True),
        )[:30]

class PublicProfileView(generics.RetrieveAPIView):
    # نمایش پروفایل عمومی از طریق نام کاربری
    serializer_class = PublicUserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "username"

    def get_queryset(self):
        return User.objects.filter(is_active=True, is_suspended=False).annotate(
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
            posts_count=Count("posts", distinct=True),
        )


class UserPreferencesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        prefs, _ = UserPreference.objects.get_or_create(user=request.user)
        return Response({key: getattr(prefs, key) for key in ("show_hero", "show_sidebar", "show_about", "show_features", "compact_feed")})

    def patch(self, request):
        prefs, _ = UserPreference.objects.get_or_create(user=request.user)
        allowed = ("show_hero", "show_sidebar", "show_about", "show_features", "compact_feed")
        for key in allowed:
            if key in request.data:
                if not isinstance(request.data[key], bool):
                    raise serializers.ValidationError({key: "مقدار این گزینه باید روشن یا خاموش باشد."})
                setattr(prefs, key, request.data[key])
        prefs.save()
        return self.get(request)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        identifier = str(request.data.get("username_or_email", "")).strip()
        user = User.objects.filter(email__iexact=identifier).first() if "@" in identifier else User.objects.filter(username__iexact=identifier).first()
        # پاسخ یکسان مانع افشای وجود یا عدم وجود حساب می‌شود.
        if user and user.is_active:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            base = getattr(settings, "FRONTEND_URL", "http://localhost:8080").rstrip("/")
            link = f"{base}/reset-password?uid={uid}&token={token}"
            send_mail("بازیابی رمز عبور ایران فردا", f"برای تعیین رمز جدید وارد این پیوند شوید:\n{link}\nاگر شما درخواست نداده‌اید این پیام را نادیده بگیرید.", settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
        return Response({"detail": "اگر حسابی با این مشخصات وجود داشته باشد، پیوند بازیابی ارسال می‌شود."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            user_id = force_str(urlsafe_base64_decode(request.data.get("uid", "")))
            user = User.objects.get(pk=user_id, is_active=True)
        except Exception:
            raise ValidationError({"token": "پیوند بازیابی معتبر نیست یا منقضی شده است."})
        token = request.data.get("token", "")
        if not default_token_generator.check_token(user, token):
            raise ValidationError({"token": "پیوند بازیابی معتبر نیست یا منقضی شده است."})
        password = request.data.get("password", "")
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(password, user)
        except Exception as exc:
            raise ValidationError({"password": list(getattr(exc, "messages", ["رمز عبور قابل قبول نیست."]))})
        user.set_password(password)
        user.save(update_fields=["password"])
        return Response({"detail": "رمز عبور با موفقیت تغییر کرد."})
