"""مسیرهای API محتوا، تعاملات، اعلان‌ها و پنل مدیریت."""
from django.urls import path
from .views import (
    PostListCreateView, PostDetailView, LikeToggleView, CommentListCreateView, CommentDeleteView, BookmarkListView,
    FollowToggleView, FollowStatusView, NotificationListView, NotificationReadView,
    ReportCreateView, ReportToggleView, BookmarkToggleView, RepostCreateView, CommentReactionView, AdminDashboardView, AdminUsersView, AdminUserActionView,
    AdminPostsView, AdminPostActionView, AdminReportsView, AdminReportResolveView,
    AdminNotificationSendView, AdminFollowsView, PublicSiteConfigurationView, AdminSiteConfigurationView,
)

urlpatterns = [
    # مسیرهای عمومی پست‌ها و تعاملات کاربران
    path("site-settings/", PublicSiteConfigurationView.as_view(), name="public-site-settings"),
    path("posts/", PostListCreateView.as_view(), name="post-list-create"),
    path("bookmarks/", BookmarkListView.as_view(), name="bookmarks"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:post_id>/like/", LikeToggleView.as_view(), name="post-like"),
    path("posts/<int:post_id>/bookmark/", BookmarkToggleView.as_view(), name="post-bookmark"),
    path("posts/<int:post_id>/repost/", RepostCreateView.as_view(), name="post-repost"),
    path("posts/<int:post_id>/comments/", CommentListCreateView.as_view(), name="post-comments"),
    path("comments/<int:comment_id>/", CommentDeleteView.as_view(), name="comment-delete"),
    path("posts/<int:post_id>/report/", ReportToggleView.as_view(), name="post-report-toggle"),
    path("comments/<int:comment_id>/react/", CommentReactionView.as_view(), name="comment-reaction"),
    path("users/<str:username>/follow/", FollowToggleView.as_view(), name="user-follow"),
    path("users/<str:username>/follow-status/", FollowStatusView.as_view(), name="user-follow-status"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("notifications/read/", NotificationReadView.as_view(), name="notifications-read-all"),
    path("notifications/<int:notification_id>/read/", NotificationReadView.as_view(), name="notification-read"),
    path("reports/", ReportCreateView.as_view(), name="report-create"),

    # مسیرهای اختصاصی مدیر؛ تمام مسیرها با مجوز IsPlatformAdmin محافظت می‌شوند.
    path("admin/site-settings/", AdminSiteConfigurationView.as_view(), name="admin-site-settings"),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("admin/users/", AdminUsersView.as_view(), name="admin-users"),
    path("admin/users/<int:user_id>/<str:action>/", AdminUserActionView.as_view(), name="admin-user-action"),
    path("admin/posts/", AdminPostsView.as_view(), name="admin-posts"),
    path("admin/posts/<int:post_id>/<str:action>/", AdminPostActionView.as_view(), name="admin-post-action"),
    path("admin/reports/", AdminReportsView.as_view(), name="admin-reports"),
    path("admin/notifications/send/", AdminNotificationSendView.as_view(), name="admin-notification-send"),
    path("admin/follows/", AdminFollowsView.as_view(), name="admin-follows"),
    path("admin/follows/<int:follow_id>/", AdminFollowsView.as_view(), name="admin-follow-delete"),
    path("admin/reports/<int:report_id>/resolve/", AdminReportResolveView.as_view(), name="admin-report-resolve"),
]
