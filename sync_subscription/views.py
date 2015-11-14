from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
import pdb
import json

from .models import Video
import sync


# Create your views here.
def index(request):
    #get access_token
    if not "access_token" in request.session:
        access_token,refresh_token = sync.get_access_token(sync.youku_user_dict)
        request.session["access_token"] = access_token
        request.session["refresh_token"] = refresh_token 
    #get user playlists
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

#get youku existing videos and check for that are from youtube
#and show videos that are published failed
def check_youku_existing_youtube_video(request):
    if not "access_token" in request.session:
        access_token,refresh_token = sync.get_access_token(sync.youku_user_dict)
    playlists= sync.get_playlist(sync.youku_user_dict,request.session["access_token"],request.session["refresh_token"])
    response = {"playlists": playlists}
    data = json.dumps(response)
    return HttpResponse(data,content_type='application/json')

#get youku video for each playlist
def get_youku_videos(request):
    playlist_id = request.GET["playlist_id"]
    if playlist_id == "uncategorized":
        videos = sync.get_videos(sync.youku_user_dict,request.session["uncategorized_videos"],request.session["access_token"],request.session["refresh_token"])
        response = {"videos":videos}
        return HttpResponse(json.dumps(response),content_type='application/json')
    if not "access_token" in request.session:
        access_token,refresh_token = sync.get_access_token(sync.youku_user_dict)
    videos = sync.get_playlist_videos(sync.youku_user_dict,playlist_id,request.session["access_token"],request.session["refresh_token"])
    response = {"videos":videos}
    return HttpResponse(json.dumps(response),content_type='application/json')
#delete videos
def delete_videos(request):
    video_ids = request.POST.getlist("video_ids[]")
    playlist_ids = request.POST.getlist("playlist_ids[]")
    if not "access_token" in request.session:
        access_token,refresh_token = sync.get_access_token(sync.youku_user_dict)    
    deleted_video_ids = sync.delete_videos(video_ids,playlist_ids,sync.youku_user_dict,request.session["access_token"],request.session["refresh_token"])
    if len(deleted_video_ids) == len(video_ids):
        return HttpResponse(json.dumps({"result":"success"}),content_type='application/json')

def search_youtube_channel(request):
    query = request.GET["query"]
    search_type = request.GET["search_type"]
    if "result_more" in request.GET:
        channels,next_page_token = sync.youtube_search(query,search_type,request.session["next_page_token"],sync.google_user_dict) 
        if next_page_token != "none":
            request.session["next_page_token"] = next_page_token
            return HttpResponse(json.dumps({"channels":channels}),content_type='application/json')
        else:
            return HttpResponse(json.dumps({"result":"no_more_results"}),content_type='application/json')
    else:
        channels,next_page_token = sync.youtube_search(query,search_type,"none",sync.google_user_dict)
        request.session["next_page_token"] = next_page_token
        return HttpResponse(json.dumps({"channels":channels}),content_type='application/json')

