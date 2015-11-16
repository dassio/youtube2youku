from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.conf import settings
from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher
import pdb
import json


from .models import Video
from .tasks import sync_channel_videos
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
    protocol = request.is_secure() and 'wss://' or 'ws://'
    WEBSOCKET_URI =protocol + request.get_host() + settings.WEBSOCKET_URL
    context = {"playlists": playlists,"WEBSOCKET_URI":WEBSOCKET_URI,"WS4REDIS_HEARTBEAT":settings.WS4REDIS_HEARTBEAT}
    return render(request,"sync_subscription/index.html",context)

#get youku existing videos and check for that are from youtube
#and show videos that are published failed
def check_youku_existing_youtube_video(request):
    if not "access_token" in request.session:
        access_token,refresh_token = sync.get_access_token(sync.youku_user_dict)
    playlists= sync.get_playlist(sync.youku_user_dict,request.session["access_token"],request.session["refresh_token"])
    response = {"playlists": playlists}
    request.session["playlists"] = playlists
    data = json.dumps(response)
    return HttpResponse(data,content_type='application/json')

#get youku video for each playlist
def get_youku_videos(request):
    playlist_id = request.GET["playlist_id"]
    if not "access_token" in request.session:
        access_token,refresh_token = sync.get_access_token(sync.youku_user_dict)
    pdb.set_trace()
    videos = sync.get_playlist_videos(sync.youku_user_dict,playlist_id,request.session["access_token"],request.session["refresh_token"],request.session["playlists"])
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

def get_channel_video_number(request):
    channel_id = request.GET["channel_id"]
    if "published_after" in request.GET:
        video_number = sync.get_channel_video_number(channel_id,request.GET["published_after"],sync.google_user_dict)
        return HttpResponse(json.dumps({"video_number":video_number}),content_type='application/json') 


def sync_channel(request):
    pdb.set_trace()
    if not "access_token" in request.session:
        access_token,refresh_token = sync.get_access_token(sync.youku_user_dict)
    channel_id = request.POST["channel_id"]
    published_after = request.POST["published_after"]
    sync_playlist_bool = request.POST["sync_playlist_bool"]
    videos = sync.get_channel_videos(channel_id,published_after,sync.google_user_dict)
    #redis_publisher = RedisPublisher(facility='uploading', broadcast=True)
    #uploading_status = RedisMessage("hello")
    #redis_publisher.publish_message(uploading_status)
    videos_trunked = trunks(videos,10) #split video_ids into 10 length trunk 
    for videos_trunk in videos_trunked:
       sync_channel_videos.delay(videos_trunk,sync.youku_user_dict,sync.google_user_dict,request.session["access_token"],request.session["refresh_token"])
    

    return HttpResponse(json.dumps({"videos":videos}),content_type='application/json')

def trunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

