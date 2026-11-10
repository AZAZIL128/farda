"""مدل‌های محتوای شبکه اجتماعی: پست، نظر، پسندیدن، دنبال‌کردن و اعلان."""
from django.conf import settings
from django.db import models

class Post(models.Model):
    # هر پست متعلق به یک کاربر است و می‌تواند متن یا تصویر داشته باشد.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts", verbose_name="نویسنده")
    content = models.TextField("متن پست", max_length=50000, blank=True)
    image = models.ImageField("تصویر پست", upload_to="posts/", blank=True, null=True)
    video = models.FileField("ویدئوی پست", upload_to="posts/videos/", blank=True, null=True)
    repost_of = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="reposts", verbose_name="بازنشرِ پست")
    is_hidden = models.BooleanField("مخفی شده", default=False)
    views_count = models.PositiveIntegerField("تعداد بازدید", default=0)
    created_at = models.DateTimeField("زمان انتشار", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["author", "repost_of"], condition=models.Q(repost_of__isnull=False), name="unique_author_repost_target")]
        verbose_name = "پست"
        verbose_name_plural = "پست‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        # عنوان کوتاه پست برای فهرست پنل مدیریت
        return f"پست {self.pk} - {self.author.username}"

class Like(models.Model):
    # هر کاربر فقط یک بار می‌تواند یک پست را پسند کند.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes", verbose_name="کاربر")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", verbose_name="پست")
    created_at = models.DateTimeField("زمان پسندیدن", auto_now_add=True)

    class Meta:
        verbose_name = "پسندیدن"
        verbose_name_plural = "پسندیدن‌ها"
        constraints = [models.UniqueConstraint(fields=["user", "post"], name="unique_user_post_like")]

class Comment(models.Model):
    # نظر کاربران زیر پست‌ها ثبت می‌شود.
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments", verbose_name="پست")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments", verbose_name="نویسنده")
    content = models.CharField("متن نظر", max_length=1500)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies", verbose_name="پاسخ به نظر")
    created_at = models.DateTimeField("زمان ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ["created_at"]

class Follow(models.Model):
    # رابطه دنبال‌کردن میان دو کاربر؛ دنبال‌کردن خود ممنوع است.
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following", verbose_name="دنبال‌کننده")
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers", verbose_name="دنبال‌شونده")
    created_at = models.DateTimeField("زمان دنبال‌کردن", auto_now_add=True)

    class Meta:
        verbose_name = "دنبال‌کردن"
        verbose_name_plural = "دنبال‌کردن‌ها"
        constraints = [
            models.UniqueConstraint(fields=["follower", "following"], name="unique_follower_following"),
            models.CheckConstraint(condition=~models.Q(follower=models.F("following")), name="cannot_follow_self"),
        ]

class Notification(models.Model):
    # اعلان‌های ساده برای دنبال‌کردن، لایک و نظر جدید
    KIND_CHOICES = [
        ("follow", "دنبال‌کردن"),
        ("like", "پسندیدن"),
        ("comment", "نظر جدید"),
        ("system", "اعلان سامانه"),
    ]
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications", verbose_name="دریافت‌کننده")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_notifications", verbose_name="انجام‌دهنده")
    kind = models.CharField("نوع اعلان", max_length=20, choices=KIND_CHOICES, default="system")
    text = models.CharField("متن اعلان", max_length=255)
    is_read = models.BooleanField("خوانده شده", default=False)
    created_at = models.DateTimeField("زمان اعلان", auto_now_add=True)

    class Meta:
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان‌ها"
        ordering = ["-created_at"]

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "post"], name="unique_user_post_bookmark")]

class Report(models.Model):
    # گزارش محتوای نامناسب برای بررسی توسط مدیران
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="reports_made", verbose_name="گزارش‌دهنده")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports", verbose_name="پست")
    REASONS = [("spam", "هرزنامه یا تبلیغات"), ("abuse", "توهین یا آزار"), ("misinformation", "اطلاعات نادرست"), ("violence", "خشونت یا محتوای نامناسب"), ("copyright", "نقض حق نشر"), ("other", "سایر")]
    reason = models.CharField("دلیل گزارش", max_length=32, choices=REASONS)
    details = models.CharField("توضیحات تکمیلی", max_length=500, blank=True)
    is_resolved = models.BooleanField("رسیدگی شده", default=False)
    created_at = models.DateTimeField("زمان گزارش", auto_now_add=True)

    class Meta:
        verbose_name = "گزارش محتوا"
        verbose_name_plural = "گزارش‌های محتوا"
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["reporter", "post"], condition=models.Q(reporter__isnull=False), name="unique_reporter_post_once")]

class CommentReaction(models.Model):
    REACTIONS = [("like", "پسندیدن"), ("support", "حمایت"), ("insightful", "مفید")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_reactions")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="reactions")
    reaction = models.CharField(max_length=20, choices=REACTIONS, default="like")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "comment", "reaction"], name="unique_user_comment_reaction")]

class SiteConfiguration(models.Model):
    """تنظیمات قابل ویرایش ظاهر و متن‌های صفحه اصلی توسط مدیر سامانه."""
    site_title = models.CharField("عنوان سایت", max_length=100, default="ایران فردا | رسانه معلمان ایران")
    hero_title = models.CharField("تیتر اصلی", max_length=180, default="صدای جامعه معلمان،")
    hero_highlight = models.CharField("ادامه تیتر اصلی", max_length=180, default="برای فردای بهتر")
    hero_description = models.TextField("توضیح معرفی", max_length=600, default="ایران فردا فضایی برای گفتگو، انتشار تجربه‌ها، هم‌اندیشی و ارتباط میان معلمان و فعالان آموزشی است.")
    feed_title = models.CharField("عنوان فید", max_length=100, default="تازه‌ترین نوشته‌ها")
    about_title = models.CharField("عنوان ستون درباره ما", max_length=100, default="درباره ایران فردا")
    about_text = models.TextField("متن درباره ما", max_length=600, default="این فضا برای شنیده‌شدن دیدگاه‌ها، تبادل تجربه و شکل‌گیری ارتباط‌های حرفه‌ای در جامعه آموزشی ایجاد شده است.")
    features_title = models.CharField("عنوان امکانات", max_length=100, default="قابلیت‌های جامعه")
    features_text = models.TextField("امکانات؛ هر مورد در یک خط", default="انتشار تجربه و محتوای آموزشی\nگفتگو و تبادل نظر\nدنبال‌کردن همکاران\nدسترسی به پروفایل و اعلان‌ها")
    footer_text = models.CharField("متن پابرگ", max_length=180, default="ایران فردا؛ رسانه معلمان ایران")
    header_custom = models.JSONField("شخصی‌سازی سربرگ", default=dict, blank=True)
    footer_custom = models.JSONField("شخصی‌سازی پابرگ", default=dict, blank=True)
    home_custom = models.JSONField("شخصی‌سازی صفحه اصلی", default=dict, blank=True)
    custom_font = models.FileField("قلم اختصاصی", upload_to="branding/fonts/", blank=True, null=True)
    custom_font_name = models.CharField("نام قلم اختصاصی", max_length=80, blank=True)
    # سقف تعداد واژه‌های هر نوشته؛ مقدار پیش‌فرض برای نصب‌های فعلی ۵۰۰ واژه است.
    post_max_words = models.PositiveSmallIntegerField("حداکثر واژه‌های هر پست", default=500)
    header_logo = models.ImageField("لوگوی سربرگ", upload_to="branding/", blank=True, null=True)
    header_logo_width = models.PositiveSmallIntegerField("عرض لوگو", default=220)
    header_logo_position = models.CharField("جایگاه لوگو", max_length=10, default="right", choices=[("right", "راست"), ("center", "وسط"), ("left", "چپ")])
    header_background = models.CharField("رنگ پس‌زمینه سربرگ", max_length=20, default="#ffffff")
    bottom_nav_background = models.CharField("رنگ پس‌زمینه منوی پایین", max_length=20, default="#ffffff")
    bottom_nav_color = models.CharField("رنگ آیکون‌های منوی پایین", max_length=20, default="#7b8297")
    bottom_nav_active_color = models.CharField("رنگ گزینه فعال منوی پایین", max_length=20, default="#34479D")
    bottom_nav_home_label = models.CharField("عنوان خانه در منوی پایین", max_length=30, default="خانه")
    bottom_nav_explore_label = models.CharField("عنوان اکسپلور در منوی پایین", max_length=30, default="اکسپلور")
    bottom_nav_following_label = models.CharField("عنوان برای شما در منوی پایین", max_length=30, default="برای شما")
    show_hero = models.BooleanField("نمایش بخش معرفی", default=True)
    show_about = models.BooleanField("نمایش ستون درباره ما", default=True)
    show_features = models.BooleanField("نمایش فهرست امکانات", default=True)
    show_join = models.BooleanField("نمایش دعوت به عضویت", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تنظیمات ظاهر سایت"
        verbose_name_plural = "تنظیمات ظاهر سایت"

    def __str__(self):
        return "تنظیمات صفحه اصلی"

    @classmethod
    def current(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
