from django.conf.urls import url
from . import views

urlpatterns = [
        url(r'^$', views.index, name="index"),
        url(r'^check_youku_existing_youtube_video$',views.check_youku_existing_youtube_video,name='check_youku_existing_youtube_video'),
        url(r'^get_youku_videos/$', views.get_youku_videos,name="get_youku_videos"),
        ]

