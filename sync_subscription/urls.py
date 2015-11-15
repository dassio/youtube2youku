from django.conf.urls import url
from . import views

urlpatterns = [
        url(r'^$', views.index, name="index"),
        url(r'^check_youku_existing_youtube_video$',views.check_youku_existing_youtube_video,name='check_youku_existing_youtube_video'),
        url(r'^get_youku_videos/$', views.get_youku_videos,name="get_youku_videos"),
        url(r'^delete_videos/$',views.delete_videos,name="delete_youku_videos"),
        url(r'^search_youtube_channel/$',views.search_youtube_channel,name="search_youtube_channel"),
        url(r'^youtube_videos/number/$',views.get_channel_video_number,name="get_channel_video_number"),
        url(r'sync_channel/$',views.sync_channel,name="sync_channel"),
        ]

