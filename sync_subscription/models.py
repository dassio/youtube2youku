from django.db import models

# Create your models here.
class Video(models.Model):
    video_id = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    playlist_id = models.CharField(max_length=255)
    video_title = models.CharField(max_length=255)
    youku_video_id = models.CharField(max_length=30, blank=True, null=True)
    sync_date =  models.DateTimeField('date synced')

    class Meta:
        db_table = 'video'

class Token(models.Model):
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_in = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    authorize_datetime = models.DateTimeField('authorized date')

    class Meta:
        db_table = 'authorization'
