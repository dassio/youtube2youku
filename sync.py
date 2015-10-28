#youtube_dl module from https://github.com/rg3/youtube-dl
from youtube_dl import YoutubeDL
#youku python sdk from http://open.youku.com/down
from youku.youku_upload import YoukuUpload
#google python sdk : pip install --upgrade google-api-python-client
from apiclient.discovery import build
#Peewee ORM : pip install peewee
from peewee import *

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

#mariadb username and password
mariadb_username = re.compile("mariadb_username\s*=\s*\"(.*)\"").search(config_data).group(1)
mariadb_passwd = re.compile("mariadb_passwd\s*=\s*\"(.*)\"").search(config_data).group(1)
mariadb_database_name = re.compile("mariadb_database_name\s*=\s*\"(.*)\"").search(config_data).group(1)
mariadb_socket_path = re.compile("mariadb_socket_path\s*=\s*\"(.*)\"").search(config_data).group(1)

db =MySQLDatabase(mariadb_database_name,user=mariadb_username,passwd=mariadb_passwd,unix_socket=mariadb_socket_path)

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
        }
database_user_dict = {
        "mariadb_username":mariadb_username,
        "mariadb_passwd":mariadb_passwd,
        "mariadb_database_name":mariadb_database_name,
        "mariadb_socket_path":mariadb_socket_path
        }
#Class for video info 
#using peewee
class Video(Model):
    video_id = CharField()
    channel_id = CharField()
    playlist_id = CharField()
    video_title = CharField()
    youku_video_id = CharField()
    class Meta:
        database = db

#get access toke for youku using your own username  and password
#todo:Oauth2
#---------------------------------------------------------------
def get_access_token(youku_client_id,youku_account,youku_passwd,youku_redirect_url,youku_client_secret):
    youku_client_id = youku_user_dict["youku_client_id"]
    youku_account = youku_user_dict["youku_account"]
    youku_passwd = youku_user_dict["youku_passwd"]
    youku_redirect_url = youku_user_dict["youku_redirect_url"]
    youku_client_secret = youku_user_dict["youku_client_secret"]

    data = urllib.urlencode({'client_id': youku_client_id, 'response_type': 'code', 'redirect_uri': youku_redirect_url, 'account': youku_account,'password': youku_passwd, 'auth_type': '1'})
    request = urllib2.Request(url="https://openapi.youku.com//v2/oauth2/authorize_submit",data=data)
    try:
        response = urllib2.urlopen(request)
    except URLError as e:
        print e.reason

    query  = urlparse.urlparse(response.geturl()).query
    code = urlparse.parse_qs(query)["code"][0]
    data = urllib.urlencode({'client_id': youku_client_id, 'client_secret':
    youku_client_secret, 'redirect_uri': youku_redirect_url, 'code': code, 'grant_type': 'authorization_code'})
    request = urllib2.Request(url="https://openapi.youku.com/v2/oauth2/token",data=data)
    try:
        response = urllib2.urlopen(request)
    except URLError as e:
        print e.reason
    res = json.load(response)
    return res["access_token"]

#download video from website like youtube
#--------------------------------------------------------
def download_video(url):
    downloader =  YoutubeDL()
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
            os.remove(file_name)
            return video_id


#sync video by downloading and uploading video
#args:
#   url:    video youtube watch url:    "https://www.youtube.com/watch?v=vd2dtkMINIw" 
#--------------------------------------------------------
def sync_video(url,youku_user_dict,google_user_dict,database_user_dict):
    youku_client_id = youku_user_dict["youku_client_id"]
    access_toke  = get_access_token(youku_user_dict)

    video_id = upload_video(download_video(url),access_token,youku_client_id)
    return video_id


#given an array of playlist and sync it to youku
#args:
#   play_list:  an array of playlist id:    "["PLtb1FJdVWjUfZ9fWxPPCrOO7LUquB3WrB"]"
#------------------------------------------------------------------
def sync_playlist(play_lists,google_user_dict):
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
                video_url  = "https://www.youtube.com/watch?v=" + video_id
                video_url = video_url.encode('ascii','ignore')
                youku_video_id = sync_video(video_url)
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
                    video_url  = "https://www.youtube.com/watch?v=" + video_id
                    video_url = video_url.encode('ascii','ignore')
                    youku_video_id = sync_video(video_url)
                    video_item.youku_video_id = youku_video_id
                    video_item.save()
 
if __name__ == '__main__':
    sync_video("https://www.youtube.com/watch?v=Gf0jp6jthFA",youku_user_dict)
    sync_playlist(["PL61E5B398705E7D99"],google_user_dict)

