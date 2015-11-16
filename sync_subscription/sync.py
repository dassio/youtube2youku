#youtube_dl module from https://github.com/rg3/youtube-dl
from youtube_dl import YoutubeDL
#youku python sdk from http://open.youku.com/down
from youku.youku_upload import YoukuUpload
#google python sdk : pip install --upgrade google-api-python-client
from apiclient.discovery import build
from django.contrib.sessions.backends.db import SessionStore

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

try:
    config_file = open("youtube2youku.config")
    config_data = config_file.read()
    config_file.close()
except:
    print "Can't find user account config file: youtube2youku.config"
    sys.exit(0)

#youku account
youku_client_id = re.compile("youku_client_id\s*=\s*\"(.*)\"").search(config_data).group(1)
youku_client_secret = re.compile("youku_client_secret\s*=\s*\"(.*)\"").search(config_data).group(1)
youku_username = re.compile("youku_username\s*=\s*\"(.*)\"").search(config_data).group(1)
youku_passwd =re.compile("youku_passwd\s*=\s*\"(.*)\"").search(config_data).group(1)
youku_redirect_url =re.compile("youku_redirect_url\s*=\s*\"(.*)\"").search(config_data).group(1)

#google api credential 
google_api_key = re.compile("google_api_key\s*=\s*\"(.*)\"").search(config_data).group(1)
google_client_id = re.compile("google_client_id\s*=\s*\"(.*)\"").search(config_data).group(1)
match = re.compile("google_username\s*=\s*\"(.*)\"").search(config_data)
if match != None:
    google_username  = match.group(1)
else:
    google_username = None
match = re.compile("google_passwd\s*=\s*\"(.*)\"").search(config_data)
if match != None:
    google_passwd  = match.group(1)
else:
    google_passwd = None

#mariadb username and password
mariadb_username = re.compile("mariadb_username\s*=\s*\"(.*)\"").search(config_data).group(1)
mariadb_passwd = re.compile("mariadb_passwd\s*=\s*\"(.*)\"").search(config_data).group(1)
mariadb_database_name = re.compile("mariadb_database_name\s*=\s*\"(.*)\"").search(config_data).group(1)
mariadb_socket_path = re.compile("mariadb_socket_path\s*=\s*\"(.*)\"").search(config_data).group(1)


#dic for youku google database
youku_user_dict = {
        "youku_client_id":youku_client_id,
        "youku_client_secret":youku_client_secret,
        "youku_username":youku_username,
        "youku_passwd":youku_passwd,
        "youku_redirect_url":youku_redirect_url
        }
google_user_dict = {
        "google_api_key":google_api_key,
        "google_client_id":google_client_id,
        "google_username":google_username,
        "google_passwd":google_passwd,
        }
database_user_dict = {
        "mariadb_username":mariadb_username,
        "mariadb_passwd":mariadb_passwd,
        "mariadb_database_name":mariadb_database_name,
        "mariadb_socket_path":mariadb_socket_path
        }

#get access toke for youku using your own username  and password
#save the token to Session so don't have to get access_token for every request
#todo:Oauth2
#---------------------------------------------------------------
def get_access_token(youku_user_dict):
    youku_client_id = youku_user_dict["youku_client_id"]
    youku_username = youku_user_dict["youku_username"]
    youku_passwd = youku_user_dict["youku_passwd"]
    youku_redirect_url = youku_user_dict["youku_redirect_url"]
    youku_client_secret = youku_user_dict["youku_client_secret"]
    #get authorization code
    data = {'client_id': youku_client_id, 'response_type': 'code', 'redirect_uri': youku_redirect_url, 'account': youku_username,'password': youku_passwd, 'auth_type': '1'}
    url="https://openapi.youku.com//v2/oauth2/authorize_submit"
    response = requests.post(url,data=data).url
    code = urlparse.parse_qs(urlparse.urlparse(response).query)["code"][0]
    #get access_token
    data = {'client_id': youku_client_id, 'client_secret': youku_client_secret, 'redirect_uri': youku_redirect_url, 'code': code, 'grant_type': 'authorization_code'}
    url="https://openapi.youku.com/v2/oauth2/token"
    response = requests.post(url,data=data).json()
    return response["access_token"],response["refresh_token"]

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
def sync_video(url,google_user_dict,youku_user_dict):
    youku_client_id = youku_user_dict["youku_client_id"]
    access_token  = get_access_token(youku_user_dict)

    video_id = upload_video(download_video(url,google_user_dict),access_token,youku_client_id)
    return video_id


#given an array of playlist and sync it to youku
#args:
#   play_list:  an array of playlist id:    "["PLtb1FJdVWjUfZ9fWxPPCrOO7LUquB3WrB"]"
#------------------------------------------------------------------
def sync_playlist(play_lists,google_user_dict,youku_user_dict):
    google_api_key = google_user_dict["google_api_key"]
    service = build("youtube","v3",developerKey=google_api_key)
    play_list_items = service.playlistItems()
    for playlist in play_lists:
        request = play_list_items.list(part ="snippet",playlistId=playlist)
        response = request.execute()
        for item in response["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            channel_id = item["snippet"]["channelId"]
            playlist_id = item["snippet"]["playlistId"]
            video_title = item["snippet"]["title"]

            if not Video.table_exists():
                Video.create_table()
            try:
                Video.get(video_id=video_id)
            except Video.DoesNotExist:
                video_item = Video(video_id=video_id,channel_id=channel_id,playlist_id=playlist_id,video_title=video_title)
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
                video_title = item["snippet"]["title"]

                try: 
                    Video.get(video_id=video_id)
                except Video.DoesNotExist:
                    video_item = Video(video_id=video_id,channel_id=channel_id,playlist_id=playlist_id,video_title=video_title)
                    if video_title != "Private video":  # if the title is "Priavte video, we can't download it right now"
                        video_url  = "https://www.youtube.com/watch?v=" + video_id
                        video_url = video_url.encode('ascii','ignore')
                        youku_video_id = sync_video(video_url,google_user_dict,youku_user_dict)
                        video_item.youku_video_id = youku_video_id
                    video_item.save()

#get youku user playlists
#----------------------------------------
def get_playlist(youku_user_dict,access_token,refresh_token):
    url = "https://openapi.youku.com/v2/playlists/by_me.json"
    data = {"client_id" : youku_user_dict["youku_client_id"],
            "access_token" : access_token,}
    playlists ,code = make_request(url,data,"playlists","GET")
    #store videos that are not in any playlist in session
    playlists.append({"id":"uncategorized","name":"uncategorized","video_count":"0"})
    return playlists

def create_playlist(youku_user_dict,title,tags,access_token,refresh_token):
    url = "https://openapi.youku.com/v2/playlists/create.json"
    data = {"client_id":youku_user_dict["youku_client_id"],
            "access_token":access_token,
            "title":title,
            "tags":tags}
    response ,code = make_request(url,data,"none","GET")["id"]
    return response

def add_videos_to_playlists(youku_user_dict,video_ids,playlist_id,access_token,refresh_token):
    url = "https://openapi.youku.com/v2/playlists/video/add.json"
    data = {"client_id":youku_user_dict["youku_client_id"],
            "access_token":access_token,
            "playlist_id":playlist_id,
            "video_ids":",".join(video_ids),}
    response ,code = make_request(url,data,"none","GET")

#get youku user video for each playlist
#check each video if it is from youtube
#--------------------------------------------
def get_playlist_videos(youku_user_dict,playlist_id,access_token,refresh_token,playlists):
    if playlist_id == "uncategorized":
        playlist_video_ids = list()
        for playlist in playlists:
            if playlist["id"] != "uncategorized":
                videos = get_playlist_videos(youku_user_dict,playlist["id"],access_token,refresh_token,playlists)
                playlist_video_ids = playlist_video_ids + videos
        #get user all videos
        #there are seven stated:normal,encoding,fail,in_review,blocked,limited(not on the document),none(not on the document)
        url = "https://openapi.youku.com/v2/videos/by_me.json"
        data ={"client_id":youku_user_dict["youku_client_id"],
                "access_token": access_token}
        pdb.set_trace()
        response ,code = make_request(url,data,"videos","GET")
        all_video_ids_byme = [ video["id"] for video in response if video["state"] != "none"]    
        all_video_ids_not_on_playlist = [video_id for video_id in all_video_ids_byme if video_id not in playlist_video_ids]
        return all_video_ids_not_on_playlist
    else:
        url = "https://openapi.youku.com/v2/playlists/videos.json"
        data = {"client_id":youku_user_dict["youku_client_id"],
                "playlist_id":playlist_id}
        videos  ,code = make_request(url,data,"videos","GET")
        return videos 


#get videos by video_ids
#-----------------------------------------
def get_videos(youku_user_dict,video_ids,access_token,rfresh_token):
    url =  "https://openapi.youku.com/v2/videos/show_basic_batch.json"
    data = {"client_id":youku_user_dict["youku_client_id"],
            "video_ids":video_ids}
    response,code = make_request(url,data,"videos","GET")
    return response

def make_request(url,data,data_name,method):
    if method == "GET":
        response = requests.get(url,params=data).json()
    if method == "POST":
        response = requests.post(url,data=data).json()
    if 'error' in response and str(response['error']["code"]) == "120040101":
        return response,response["code"]
    if 'error' in response:return response,response["code"]
    if "page" in response:
        response_data = list()
        response_data = response[data_name]
        page = 1 
        while int(response['count'])*int(response['page']) < int(response['total']):
            page = page + 1
            data["page"] = page
            if method == "GET":
                response = requests.get(url,params=data).json()
            if method == "POST":
                response = requests.post(url,data=data).json()
            if 'error' in response and str(response['error']["code"]) == "120040101":
                return response_data
            if 'error' in response:return response,response["code"]
            response_data = response_data + response[data_name]
        return response_data,"OK"
    if data_name == "none":
        return response,"OK"
    return response[data_name],"OK"
#delete playlist and videos
#----------------------------------------------
def delete_videos(video_ids,playlist_ids,youku_user_dict,access_token,refresh_token):
    #delete palylists without deleting videos in it
    url = "https://openapi.youku.com/v2/playlists/destroy.json"
    data = {"client_id":youku_user_dict["youku_client_id"],
            "access_token": access_token,}
    for playlist_id in playlist_ids:
        data["playlist_id"] = playlist_id
        response,code = make_request(url,data,"none","GET")
    #delete vidos
    url = "https://openapi.youku.com/v2/videos/destroy.json"
    data = {"client_id":youku_user_dict["youku_client_id"],
            "access_token": access_token,}
    deleted_video_ids = list()
    for video_id in video_ids:
        data["video_id"] = video_id
        response,code = make_request(url,data,"none","POST")
        #if it is system error from youku we have to check if the video still exist to see if we successfully deleted it
        if code == "1002":deleted_video_ids.append(video_id)
        deleted_video_ids.append(response["id"])
    return deleted_video_ids


def youtube_search(query,search_type,next_page_token,google_user_dict):
    google_api_key = google_user_dict["google_api_key"]
    service = build("youtube","v3",developerKey=google_api_key)
    if next_page_token == "none":
        response = service.search().list(q=query,type=search_type,part="snippet",fields="items/snippet,nextPageToken",maxResults="10").execute()
        if "nextPageToken" in response:
            return response["items"],response["nextPageToken"]
        else:
            return response["items"],"none"
    else:
        response = service.search().list(q=query,type=search_type,part="snippet",fields="items/snippet,nextPageToken",pageToken=next_page_token,maxResults="10").execute()
        if "nextPageToken" in response:
            return  response["items"],response["nextPageToken"]
        else:
            return response["items"],"none"


def get_channel_video_number(channel_id,published_after,google_user_dict):
    google_api_key = google_user_dict["google_api_key"]
    service = build("youtube","v3",developerKey=google_api_key)
    video_number = 0 
    response = service.search().list(part="snippet",fields="items/kind,nextPageToken",channelId=channel_id,publishedAfter=published_after,type="video").execute()
    video_number = video_number + len(response["items"])
    while "nextPageToken" in response:
        response = service.search().list(part="snippet",fields="items/kind,nextPageToken",channelId=channel_id,pageToken=response["nextPageToken"],publishedAfter=published_after,type="video").execute()
        video_number = video_number + len(response["items"])
    return video_number;

def get_channel_videos(channel_id,published_after,google_user_dict):
    google_api_key = google_user_dict["google_api_key"]
    service = build("youtube","v3",developerKey=google_api_key)
    response = service.search().list(part="snippet",fields="items(id,snippet),nextPageToken",publishedAfter=published_after,channelId=channel_id,type="video").execute()
    videos =  response["items"]
    while "nextPageToken" in response:
        response = service.search().list(pageToken=response["nextPageToken"],part="snippet",fields="items/id,nextPageToken",channelId=channel_id,publishedAfter=published_after,type="video").execute()
        videos = videos + response["items"]
    return videos


