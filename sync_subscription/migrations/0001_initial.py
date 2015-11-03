# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access_token', models.CharField(max_length=255)),
                ('refresh_token', models.CharField(max_length=255)),
                ('expires_in', models.CharField(max_length=255)),
                ('user_id', models.CharField(max_length=255)),
                ('authorize_datetime', models.DateTimeField(verbose_name=b'authorized date')),
            ],
            options={
                'db_table': 'authorization',
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('video_id', models.CharField(max_length=255)),
                ('channel_id', models.CharField(max_length=255)),
                ('playlist_id', models.CharField(max_length=255)),
                ('video_title', models.CharField(max_length=255)),
                ('youku_video_id', models.CharField(max_length=30, null=True, blank=True)),
                ('sync_date', models.DateTimeField(verbose_name=b'date synced')),
            ],
            options={
                'db_table': 'video',
            },
        ),
    ]
