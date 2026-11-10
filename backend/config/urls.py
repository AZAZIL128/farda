"""مسیرهای اصلی بک‌اند و اتصال APIها به اپلیکیشن‌ها."""
from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse

# پاسخ ساده برای بررسی زنده بودن بک‌اند از سمت Docker و Nginx
def health_check(request):
    return JsonResponse({"status": "ok", "service": "iran-farda-api"})

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.social.urls")),
]
