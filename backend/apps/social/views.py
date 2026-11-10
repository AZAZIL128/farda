"""APIهای اصلی شبکه اجتماعی و عملیات پنل مدیریت."""
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Post, Like, Comment, Follow, Notification, Report, SiteConfiguration, Bookmark, CommentReaction
from .serializers import PostSerializer, CommentSerializer, NotificationSerializer, ReportSerializer
from .permissions import IsPlatformAdmin, NotSuspendedForWrite

User = get_user_model()

class PostListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, NotSuspendedForWrite]
    # دریافت فید عمومی و ایجاد پست برای کاربر واردشده
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        # پست‌های مخفی یا متعلق به حساب تعلیق‌شده در فید عمومی نمایش داده نمی‌شوند.
        queryset = Post.objects.filter(is_hidden=False, author__is_suspended=False).select_related("author").annotate(
            likes_count=Count("likes", distinct=True), comments_count=Count("comments", distinct=True)
        )
        # در صفحه پروفایل، فید فقط به نوشته‌های همان نام کاربری محدود می‌شود.
        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(author__username=username)
        feed = self.request.query_params.get("feed")
        if feed == "following":
            if self.request.user.is_authenticated:
                queryset = queryset.filter(author__followers__follower=self.request.user)
            else:
                queryset = queryset.none()
        if feed == "explore":
            from django.utils import timezone
            from datetime import timedelta
            queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=4))
        if self.request.query_params.get("sort") == "popular":
            queryset = queryset.order_by("-likes_count", "-views_count", "-created_at")
        return queryset

    def perform_create(self, serializer):
        # حداقل متن یا تصویر برای ارسال پست لازم است.
        content = self.request.data.get("content", "").strip()
        image = self.request.FILES.get("image")
        video = self.request.FILES.get("video")
        if not content and not image and not video:
            raise ValidationError("برای انتشار پست، متن یا تصویر وارد کنید.")
        if self.request.user.is_suspended:
            raise PermissionDenied("حساب شما امکان انتشار محتوا ندارد.")
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    # مشاهده، ویرایش و حذف پست؛ فقط صاحب پست یا مدیر مجاز است.
    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Post.objects.select_related("author").annotate(
        likes_count=Count("likes", distinct=True), comments_count=Count("comments", distinct=True)
    )

    def get_queryset(self):
        # پست مخفی فقط برای نویسنده خودش یا مدیر سامانه قابل مشاهده است.
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return queryset
        if user.is_authenticated:
            return queryset.filter(
                Q(is_hidden=False, author__is_suspended=False) | Q(author=user)
            )
        return queryset.filter(is_hidden=False, author__is_suspended=False)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_authenticated or instance.author_id != request.user.id:
            Post.objects.filter(pk=instance.pk).update(views_count=models.F("views_count") + 1)
            instance.refresh_from_db(fields=["views_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_permissions(self):
        # مشاهده پست عمومی است اما تغییرات نیازمند ورود هستند.
        if self.request.method == "GET":
            return [permissions.AllowAny(), NotSuspendedForWrite()]
        return [permissions.IsAuthenticated(), NotSuspendedForWrite()]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in ("PUT", "PATCH", "DELETE") and obj.author_id != request.user.id and not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied("فقط نویسنده یا مدیر می‌تواند این پست را تغییر دهد.")

class LikeToggleView(APIView):
    # لایک و لغو لایک به‌صورت یک عملیات toggle
    permission_classes = [permissions.IsAuthenticated, NotSuspendedForWrite]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_hidden=False, author__is_suspended=False)
        # کلیک اول لایک را ثبت و کلیک بعدی همان کاربر لایک را لغو می‌کند.
        like = Like.objects.filter(user=request.user, post=post).first()
        if like:
            like.delete()
            liked = False
        else:
            Like.objects.create(user=request.user, post=post)
            liked = True
            if post.author_id != request.user.id:
                Notification.objects.create(recipient=post.author, actor=request.user, kind="like", text=f"{request.user.username} پست شما را پسندید.")
        return Response({"liked": liked, "likes_count": post.likes.count()})

class CommentListCreateView(generics.ListCreateAPIView):
    # نمایش نظرات و ثبت نظر جدید زیر یک پست
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, NotSuspendedForWrite]

    def get_queryset(self):
        # نظرهای پست مخفی یا متعلق به حساب تعلیق‌شده به‌صورت عمومی نمایش داده نمی‌شوند.
        post = get_object_or_404(
            Post, id=self.kwargs["post_id"], is_hidden=False, author__is_suspended=False
        )
        return Comment.objects.filter(post=post).select_related("author")

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs["post_id"], is_hidden=False, author__is_suspended=False)
        parent_id = self.request.data.get("parent")
        if parent_id and not Comment.objects.filter(id=parent_id, post=post).exists():
            raise ValidationError({"parent": "نظر والد معتبر نیست."})
        comment = serializer.save(author=self.request.user, post=post)
        if post.author_id != self.request.user.id:
            Notification.objects.create(recipient=post.author, actor=self.request.user, kind="comment", text=f"{self.request.user.username} برای پست شما نظر نوشت.")


class CommentDeleteView(APIView):
    # نویسنده دیدگاه، صاحب پست یا مدیر می‌تواند دیدگاه را حذف کند.
    permission_classes = [permissions.IsAuthenticated, NotSuspendedForWrite]
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment.objects.select_related("post", "author"), id=comment_id)
        allowed = (comment.author_id == request.user.id or comment.post.author_id == request.user.id or request.user.is_staff or request.user.is_superuser)
        if not allowed:
            raise PermissionDenied("فقط نویسنده دیدگاه، صاحب نوشته یا مدیر می‌تواند آن را حذف کند.")
        comment.delete()  # پاسخ‌ها و واکنش‌های وابسته نیز با حذف آبشاری پاک می‌شوند.
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentReactionView(APIView):
    permission_classes = [permissions.IsAuthenticated, NotSuspendedForWrite]
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, post__is_hidden=False)
        reaction = str(request.data.get("reaction", "like"))
        if reaction not in {"like", "support", "insightful"}:
            raise ValidationError("نوع واکنش معتبر نیست.")
        # واکنش به دیدگاه نیز toggle است؛ کلیک مجدد واکنش خود کاربر را برمی‌دارد.
        obj = CommentReaction.objects.filter(user=request.user, comment=comment, reaction=reaction).first()
        if obj:
            obj.delete()
            active = False
        else:
            CommentReaction.objects.create(user=request.user, comment=comment, reaction=reaction)
            active = True
        counts = {key: comment.reactions.filter(reaction=key).count() for key, _ in CommentReaction.REACTIONS}
        return Response({"active": active, "counts": counts, "mine": list(comment.reactions.filter(user=request.user).values_list("reaction", flat=True))})

class BookmarkToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated, NotSuspendedForWrite]
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_hidden=False)
        # ذخیره‌کردن با کلیک دوباره لغو می‌شود.
        obj = Bookmark.objects.filter(user=request.user, post=post).first()
        if obj:
            obj.delete()
            bookmarked = False
        else:
            Bookmark.objects.create(user=request.user, post=post)
            bookmarked = True
        return Response({"bookmarked": bookmarked})


class BookmarkListView(generics.ListAPIView):
    """فهرست پست‌های ذخیره‌شده فقط برای صاحب حساب."""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(bookmarks__user=self.request.user, is_hidden=False).select_related("author").annotate(
            likes_count=Count("likes", distinct=True), comments_count=Count("comments", distinct=True)
        ).order_by("-bookmarks__created_at")

class RepostCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, NotSuspendedForWrite]
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_hidden=False)
        repost, created = Post.objects.get_or_create(author=request.user, repost_of=post, defaults={"content": post.content, "image": post.image, "video": post.video})
        if created and post.author_id != request.user.id:
            Notification.objects.create(recipient=post.author, actor=request.user, kind="system", text=f"{request.user.username} پست شما را بازنشر کرد.")
        return Response({"id": repost.id, "already_done": not created}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class FollowToggleView(APIView):
    # دنبال‌کردن یا لغو دنبال‌کردن یک کاربر دیگر
    permission_classes = [permissions.IsAuthenticated, NotSuspendedForWrite]

    def post(self, request, username):
        target = get_object_or_404(User, username=username, is_active=True, is_suspended=False)
        if target.id == request.user.id:
            raise ValidationError("نمی‌توانید خودتان را دنبال کنید.")
        relation, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if not created:
            relation.delete()
            following = False
        else:
            following = True
            Notification.objects.create(recipient=target, actor=request.user, kind="follow", text=f"{request.user.username} شما را دنبال کرد.")
        return Response({"following": following, "followers_count": target.followers.count()})

class FollowStatusView(APIView):
    # بررسی اینکه کاربر فعلی، پروفایل موردنظر را دنبال می‌کند یا نه
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        target = get_object_or_404(User, username=username)
        return Response({"following": Follow.objects.filter(follower=request.user, following=target).exists()})

class NotificationListView(generics.ListAPIView):
    # هر کاربر فقط اعلان‌های دریافت‌شده خودش را مشاهده می‌کند.
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related("actor")

class NotificationReadView(APIView):
    # علامت‌گذاری یک اعلان یا تمام اعلان‌ها به‌عنوان خوانده‌شده
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id=None):
        notifications = Notification.objects.filter(recipient=request.user)
        if notification_id is not None:
            notification = get_object_or_404(notifications, id=notification_id)
            notification.is_read = True
            notification.save(update_fields=["is_read"])
            return Response({"updated": 1})
        count = notifications.filter(is_read=False).update(is_read=True)
        return Response({"updated": count})

class ReportToggleView(APIView):
    # گزارش تکراری ساخته نمی‌شود و کاربر می‌تواند گزارش بازِ خودش را لغو کند.
    permission_classes = [permissions.IsAuthenticated, NotSuspendedForWrite]
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_hidden=False)
        report = Report.objects.filter(reporter=request.user, post=post, is_resolved=False).first()
        if report:
            report.delete()
            return Response({"reported": False})
        reason = str(request.data.get("reason", "other"))
        allowed = {key for key, _ in Report.REASONS}
        if reason not in allowed:
            raise ValidationError({"reason": "دلیل گزارش معتبر نیست."})
        details = str(request.data.get("details", ""))[:500]
        if reason == "other" and not details.strip():
            raise ValidationError({"details": "برای گزینه سایر، توضیح الزامی است."})
        Report.objects.create(reporter=request.user, post=post, reason=reason, details=details)
        return Response({"reported": True}, status=status.HTTP_201_CREATED)

class ReportCreateView(generics.CreateAPIView):
    # ثبت گزارش محتوا توسط کاربران واردشده
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, NotSuspendedForWrite]

    def perform_create(self, serializer):
        post = serializer.validated_data["post"]
        if Report.objects.filter(reporter=self.request.user, post=post).exists():
            raise ValidationError("شما قبلاً این نوشته را گزارش کرده‌اید.")
        serializer.save(reporter=self.request.user)

# ------------------------- APIهای پنل مدیریت -------------------------
class AdminDashboardView(APIView):
    # آمار خلاصه برای صفحه اول پنل مدیریت
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        return Response({
            "users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True, is_suspended=False).count(),
            "posts": Post.objects.count(),
            "visible_posts": Post.objects.filter(is_hidden=False).count(),
            "open_reports": Report.objects.filter(is_resolved=False).count(),
            "suspended_users": User.objects.filter(is_suspended=True).count(),
        })

class AdminUsersView(APIView):
    # فهرست کاربران برای مدیریت و نظارت مدیر سامانه
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        term = self.request.query_params.get("q", "").strip()
        qs = User.objects.order_by("-date_joined")
        if term:
            qs = qs.filter(Q(username__icontains=term) | Q(email__icontains=term) | Q(display_name__icontains=term))
        rows = qs.values("id", "username", "email", "display_name", "is_staff", "is_verified", "is_suspended", "date_joined")[:50]
        return Response(list(rows))

class AdminUserActionView(APIView):
    # تعلیق/رفع تعلیق یا تأیید نشان کاربر
    permission_classes = [IsPlatformAdmin]

    def post(self, request, user_id, action):
        user = get_object_or_404(User, id=user_id)
        if user.is_superuser:
            raise PermissionDenied("تغییر وضعیت مدیر اصلی از پنل عمومی مجاز نیست.")
        if action == "suspend":
            user.is_suspended = not user.is_suspended
            user.save(update_fields=["is_suspended"])
            return Response({"is_suspended": user.is_suspended})
        if action == "verify":
            user.is_verified = not user.is_verified
            user.save(update_fields=["is_verified"])
            return Response({"is_verified": user.is_verified})
        raise ValidationError("عملیات مدیریتی شناخته‌شده نیست.")

class AdminPostsView(APIView):
    # فهرست پست‌ها برای بررسی مدیر
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        rows = Post.objects.select_related("author").order_by("-created_at").values("id", "author__username", "content", "is_hidden", "created_at")[:40]
        # متن کامل در صفحه مستقل نوشته نمایش داده می‌شود؛ پنل فقط چکیده کوتاه می‌گیرد.
        result = []
        for row in rows:
            content = row["content"] or ""
            row["content"] = content[:140] + ("…" if len(content) > 140 else "")
            result.append(row)
        return Response(result)

class AdminPostActionView(APIView):
    # مخفی‌سازی/نمایش مجدد یا حذف پست توسط مدیر
    permission_classes = [IsPlatformAdmin]

    def post(self, request, post_id, action):
        post = get_object_or_404(Post, id=post_id)
        if action == "hide":
            post.is_hidden = not post.is_hidden
            post.save(update_fields=["is_hidden"])
            return Response({"is_hidden": post.is_hidden})
        if action == "delete":
            post.delete()
            return Response({"deleted": True})
        raise ValidationError("عملیات مدیریتی شناخته‌شده نیست.")

class AdminReportsView(APIView):
    # گزارش‌های کاربران برای بررسی و رسیدگی
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        rows = Report.objects.select_related("reporter", "post").order_by("-created_at").values("id", "reporter__username", "post_id", "reason", "details", "is_resolved", "created_at")[:300]
        return Response(list(rows))


class AdminNotificationSendView(APIView):
    # ارسال اعلان سیستمی به یک گروه انتخاب‌شده یا تمام کاربران فعال
    permission_classes = [IsPlatformAdmin]

    def post(self, request):
        text = str(request.data.get("text", "")).strip()
        recipient_ids = request.data.get("recipient_ids", [])
        send_to_all = bool(request.data.get("send_to_all", False))
        if not text:
            raise ValidationError("متن اعلان را وارد کنید.")
        if len(text) > 255:
            raise ValidationError("متن اعلان نباید بیشتر از ۲۵۵ کاراکتر باشد.")
        recipients = User.objects.filter(is_active=True, is_suspended=False)
        if not send_to_all:
            if not isinstance(recipient_ids, list) or not recipient_ids:
                raise ValidationError("حداقل یک کاربر یا گزینه ارسال برای همه را انتخاب کنید.")
            recipients = recipients.filter(id__in=recipient_ids)
        notifications = [Notification(recipient=item, actor=request.user, kind="system", text=text) for item in recipients]
        Notification.objects.bulk_create(notifications)
        return Response({"sent": len(notifications)})

class AdminFollowsView(APIView):
    # مشاهده و مدیریت روابط دنبال‌کردن برای پشتیبانی و رسیدگی مدیریتی
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        rows = Follow.objects.select_related("follower", "following").order_by("-created_at").values(
            "id", "follower__username", "following__username", "created_at"
        )[:300]
        return Response(list(rows))

    def delete(self, request, follow_id=None):
        relation = get_object_or_404(Follow, id=follow_id)
        relation.delete()
        return Response({"deleted": True})

class AdminReportResolveView(APIView):
    # بستن گزارش پس از بررسی مدیر
    permission_classes = [IsPlatformAdmin]

    def post(self, request, report_id):
        report = get_object_or_404(Report, id=report_id)
        report.is_resolved = True
        report.save(update_fields=["is_resolved"])
        return Response({"resolved": True})


class PublicSiteConfigurationView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        obj = SiteConfiguration.current()
        fields = ("site_title", "hero_title", "hero_highlight", "hero_description", "feed_title",
            "about_title", "about_text", "features_title", "features_text", "footer_text",
            "show_hero", "show_about", "show_features", "show_join", "header_logo_width",
            "header_logo_position", "header_background", "bottom_nav_background", "bottom_nav_color", "bottom_nav_active_color", "bottom_nav_home_label", "bottom_nav_explore_label", "bottom_nav_following_label", "header_custom", "footer_custom", "home_custom", "custom_font_name", "post_max_words")
        data = {field: getattr(obj, field) for field in fields}
        data["header_logo"] = request.build_absolute_uri(obj.header_logo.url) if obj.header_logo else ""
        data["custom_font"] = request.build_absolute_uri(obj.custom_font.url) if obj.custom_font else ""
        return Response(data)

class AdminSiteConfigurationView(APIView):
    permission_classes = [IsPlatformAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        return PublicSiteConfigurationView().get(request)

    def patch(self, request):
        obj = SiteConfiguration.current()
        text_fields = ("site_title", "hero_title", "hero_highlight", "hero_description", "feed_title", "about_title", "about_text", "features_title", "features_text", "footer_text", "header_logo_position", "header_background", "bottom_nav_background", "bottom_nav_color", "bottom_nav_active_color", "bottom_nav_home_label", "bottom_nav_explore_label", "bottom_nav_following_label", "custom_font_name")
        json_fields = ("header_custom", "footer_custom", "home_custom")
        bool_fields = ("show_hero", "show_about", "show_features", "show_join")
        if "post_max_words" in request.data:
            try:
                maximum_words = int(request.data["post_max_words"])
            except (TypeError, ValueError):
                raise ValidationError({"post_max_words": "سقف واژه باید عدد صحیح باشد."})
            if not 10 <= maximum_words <= 5000:
                raise ValidationError({"post_max_words": "سقف واژه باید بین ۱۰ تا ۵۰۰۰ باشد."})
            obj.post_max_words = maximum_words
        if "header_logo_width" in request.data:
            width = int(request.data["header_logo_width"])
            if not 60 <= width <= 500:
                raise ValidationError({"header_logo_width": "عرض لوگو باید بین ۶۰ تا ۵۰۰ پیکسل باشد."})
            obj.header_logo_width = width
        if request.FILES.get("header_logo"):
            obj.header_logo = request.FILES["header_logo"]
        if request.FILES.get("custom_font"):
            font = request.FILES["custom_font"]
            if font.size > 8 * 1024 * 1024 or not font.name.lower().endswith((".woff2", ".woff", ".ttf", ".otf")):
                raise ValidationError("قلم باید با فرمت WOFF2، WOFF، TTF یا OTF و حداکثر ۸ مگابایت باشد.")
            obj.custom_font = font
        for field in text_fields:
            if field in request.data:
                value = str(request.data[field]).strip()
                if not value:
                    raise ValidationError({field: "این فیلد نمی‌تواند خالی باشد."})
                setattr(obj, field, value)
        for field in json_fields:
            if field in request.data:
                value = request.data[field]
                if isinstance(value, str):
                    import json
                    try: value = json.loads(value)
                    except ValueError: raise ValidationError({field: "ساختار تنظیمات معتبر نیست."})
                if not isinstance(value, dict): raise ValidationError({field: "مقدار باید مجموعه‌ای از تنظیمات باشد."})
                setattr(obj, field, value)
        for field in bool_fields:
            if field in request.data:
                if not isinstance(request.data[field], bool):
                    raise ValidationError({field: "مقدار باید روشن یا خاموش باشد."})
                setattr(obj, field, request.data[field])
        obj.save()
        return PublicSiteConfigurationView().get(request)
