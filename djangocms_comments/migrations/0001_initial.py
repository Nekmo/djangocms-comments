# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('cms', '0013_urlconfrevision'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonymousAuthor',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32)),
                ('email', models.EmailField(max_length=254)),
                ('website', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('page_id', models.PositiveIntegerField()),
                ('author_id', models.PositiveIntegerField()),
                ('body', models.TextField()),
                ('requires_attention', models.CharField(choices=[('spam', 'Spam'), ('edited', 'Edited')], max_length=16, blank='')),
                ('moderated', models.CharField(choices=[('spam', 'Spam'), ('edited', 'Edited'), ('deleted', 'Deleted')], max_length=16, blank='')),
                ('moderated_reason', models.CharField(max_length=120, blank=True)),
                ('user_ip', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('referrer', models.URLField(blank=True)),
                ('published', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author_type', models.ForeignKey(to='contenttypes.ContentType', related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(to='cms.CMSPlugin', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('published_by_default', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='CommentsConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('open_comments', models.BooleanField(default=True)),
                ('published_by_default', models.BooleanField(default=True)),
                ('akismet', models.CharField(max_length=12, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='comments',
            name='config',
            field=models.ForeignKey(to='djangocms_comments.CommentsConfig'),
        ),
        migrations.AddField(
            model_name='comment',
            name='config',
            field=models.ForeignKey(to='djangocms_comments.CommentsConfig'),
        ),
        migrations.AddField(
            model_name='comment',
            name='moderated_by',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='comment',
            name='page_type',
            field=models.ForeignKey(to='contenttypes.ContentType', related_name='+'),
        ),
    ]
