"""مجوزهای اختصاصی برای عملیات پنل مدیریت."""
from rest_framework.permissions import BasePermission

class IsPlatformAdmin(BasePermission):
    # فقط مدیر دارای دسترسی staff یا superuser می‌تواند API مدیریتی را فراخوانی کند.
    message = "دسترسی به این بخش فقط برای مدیر سامانه مجاز است."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))


class NotSuspendedForWrite(BasePermission):
    # درخواست‌های خواندنی عمومی‌اند؛ اما حساب تعلیق‌شده اجازه تغییر داده ندارد.
    message = "حساب شما توسط مدیر سامانه تعلیق شده است."

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(request.user and request.user.is_authenticated and not request.user.is_suspended)
