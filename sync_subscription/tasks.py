#youtube_dl module from https://github.com/rg3/youtube-dl
from youtube_dl import YoutubeDL
#youku python sdk from http://open.youku.com/down
from youku.youku_upload import YoukuUpload
#google python sdk : pip install --upgrade google-api-python-client
from apiclient.discovery import build

from celery import shared_task
from django.utils import timezone
from .models import Video,Token
import urllib2
import urllib
import urlparse
import pdb
import codecs
import re
import io
import os
import random
import shlex
import sys
import json
import pdb
import requests


#download video from website like youtube
#--------------------------------------------------------
def download_video(url,google_user_dict):
    if google_user_dict["google_username"] != None and google_user_dict["google_passwd"]:
        params = {"username":google_user_dict["google_username"],"password":google_user_dict["google_passwd"]}
    else:
        params = {}
    downloader =  YoutubeDL(params)
    res = downloader.download([url])
    filename = downloader.prepare_filename(res[1])
    ret_code = res[0]
    video_info = res[1]
    return video_info

#upload  video to youku
#----------------------------------------------------------
def upload_video(video_info,access_token,youku_client_id):
    downloader = YoutubeDL()
    title = video_info[u"title"]
    file_name  = downloader.prepare_filename(video_info)
    tags = ["dassio",video_info["uploader"]]
    discription  = video_info["description"][0:1950]


    youku = YoukuUpload(youku_client_id,access_token,file_name)
    params = youku.prepare_video_params(title,tags,discription,'reproduced')
    try:
        if os.path.isfile(file_name + ".upload"):
            youku._read_upload_state_from_file()
            video_id = youku.upload(params)
        else:
            video_id = youku.upload(params)
    except:
        video_id = youku.upload(params)
    else:
        if video_id != "":
            try:
                os.remove(file_name)
            except:
                write_string("traceback.print_exc()")
            return video_id 


#sync video by downloading and uploading video
#args:
#   url:    video youtube watch url:    https://www.youtube.com/watch?v=vd2dtkMINIw
#--------------------------------------------------------
def sync_video(url,google_user_dict,youku_user_dict,access_token):
    youku_client_id = youku_user_dict["youku_client_id"]
    video_id = upload_video(download_video(url,google_user_dict),access_token,youku_client_id)
    return video_id

#given an array of playlist and sync it to youku
#args:
#   play_list_id:  playlist_id "["PLtb1FJdVWjUfZ9fWxPPCrOO7LUquB3WrB"]"
#------------------------------------------------------------------
def sync_playlist(play_list_id,google_user_dict,youku_user_dict):
    google_api_key = google_user_dict["google_api_key"]
    service = build("youtube","v3",developerKey=google_api_key)
    response = service.play_list_items().list(part ="snippet",playlistId=playlist_id).execute()
    for item in response["items"]:
        video_id = item["snippet"]["resourceId"]["videoId"]
        channel_id = item["snippet"]["channelId"]
        playlist_id = item["snippet"]["playlistId"]
        video_title = item["snippet"]["title"]
        video_item,created = Video.objects.get_or_create(video_id=video_id,channel_id=channel_id,playlist_id=playlist_id,video_title=video_title)
        if created:
            if video_title != "Private video":
                video_url  = "https://www.youtube.com/watch?v=" + video_id
                video_url = video_url.encode('ascii','ignore')
                youku_video_id = sync_video(video_url,google_user_dict,youku_user_dict)
                video_item.youku_video_id = youku_video_id
            video_item.save() 
    while "nextPageToken" in response:
        response = play_list_items.list(part="snippet",playlistId=playlist,pageToken=response["nextPageToken"]).execute()
        for item in response["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            channel_id = item["snippet"]["channelId"]
            playlist_id = item["snippet"]["playlistId"]
            video_item_title = item["snippet"]["title"]
            video_item,created = Video.objects.get_or_create(video_id=video_id,channel_id=channel_id,playlist_id=playlist_id,video_title=video_title)
            if created:
                if video_title != "Private video":
                    video_url  = "https://www.youtube.com/watch?v=" + video_id
                    video_url = video_url.encode('ascii','ignore')
                    youku_video_id = sync_video(video_url,google_user_dict,youku_user_dict)
                    video_item.youku_video_id = youku_video_id
                video_item.save()  
@shared_task
def sync_channel_videos(videos,youku_user_dict,google_user_dict,access_token,refresh_token):
    for video in videos:
        video_id = video["id"]["videoId"]
        channel_id = video["snippet"]["channelId"]
        video_title = video["snippet"]["title"]
        video_item,created = Video.objects.get_or_create(video_id=video_id,channel_id=channel_id,video_title=video_title,sync_date=timezone.now())
        if created:
            if video_title != "Private video":
                video_url  = "https://www.youtube.com/watch?v=" + video_id
                youku_video_id = sync_video(video_url,google_user_dict,youku_user_dict,access_token)
                video_item.youku_video_id = youku_video_id
            else:
                video_item.video_title = "private video"
            video_item.save()


