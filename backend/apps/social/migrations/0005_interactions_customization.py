from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def remove_duplicate_actions(apps, schema_editor):
    Report = apps.get_model('social', 'Report')
    Post = apps.get_model('social', 'Post')
    seen = set()
    for row in Report.objects.exclude(reporter_id=None).order_by('id').iterator():
        key = (row.reporter_id, row.post_id)
        if key in seen:
            row.delete()
        else:
            seen.add(key)
    seen = set()
    for row in Post.objects.exclude(repost_of_id=None).order_by('id').iterator():
        key = (row.author_id, row.repost_of_id)
        if key in seen:
            row.delete()
        else:
            seen.add(key)

class Migration(migrations.Migration):
    dependencies = [('social', '0004_bottom_navigation_settings'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.RunPython(remove_duplicate_actions, migrations.RunPython.noop),
        migrations.AddConstraint(model_name='post', constraint=models.UniqueConstraint(condition=models.Q(('repost_of__isnull', False)), fields=('author','repost_of'), name='unique_author_repost_target')),
        migrations.AddConstraint(model_name='report', constraint=models.UniqueConstraint(condition=models.Q(('reporter__isnull', False)), fields=('reporter','post'), name='unique_reporter_post_once')),
        migrations.CreateModel(name='CommentReaction', fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('reaction',models.CharField(choices=[('like','پسندیدن'),('support','حمایت'),('insightful','مفید')],default='like',max_length=20)),('created_at',models.DateTimeField(auto_now_add=True)),('comment',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='reactions',to='social.comment')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='comment_reactions',to=settings.AUTH_USER_MODEL))], options={'constraints':[models.UniqueConstraint(fields=('user','comment','reaction'),name='unique_user_comment_reaction')]}),
        migrations.AddField(model_name='siteconfiguration',name='header_custom',field=models.JSONField(blank=True,default=dict,verbose_name='شخصی‌سازی سربرگ')),
        migrations.AddField(model_name='siteconfiguration',name='footer_custom',field=models.JSONField(blank=True,default=dict,verbose_name='شخصی‌سازی پابرگ')),
        migrations.AddField(model_name='siteconfiguration',name='home_custom',field=models.JSONField(blank=True,default=dict,verbose_name='شخصی‌سازی صفحه اصلی')),
        migrations.AddField(model_name='siteconfiguration',name='custom_font',field=models.FileField(blank=True,null=True,upload_to='branding/fonts/',verbose_name='قلم اختصاصی')),
        migrations.AddField(model_name='siteconfiguration',name='custom_font_name',field=models.CharField(blank=True,max_length=80,verbose_name='نام قلم اختصاصی')),
    ]
