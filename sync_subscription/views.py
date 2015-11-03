from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
import pdb
import json

from .models import Video
import sync


# Create your views here.
def index(request):
    playlist_ids = list()
    playlists = dict()
    for video in Video.objects.all():
        if not video.playlist_id in playlist_ids:
            playlist_ids.append(video.playlist_id)
            playlists[video.playlist_id] = list()
    for playlist_id in playlist_ids:
        for video in Video.objects.all():
            if video.playlist_id == playlist_id:
                playlists[playlist_id].append(video.video_title)
    context = {"playlists": playlists}
    return render(request,"sync_subscription/index.html",context)
def check_youku_existing_youtube_video(request):
    playlists = sync.get_playlist(sync.youku_user_dict)
    response = {"playlists": playlists}
    data = json.dumps(response)

    return HttpResponse(data,content_type='application/json')
def get_youku_videos(request):
    playlist_id = request.GET["playlist_id"]
    videos = sync.get_playlist_videos(sync.youku_user_dict,playlist_id)
    response = {"videos":videos}
    return HttpResponse(json.dumps(response),content_type='application/json')
     
