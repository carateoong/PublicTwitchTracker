


import os
import json
import datetime
from dotenv import load_dotenv

load_dotenv()
import requests

from datetime import datetime
import pytz


# Gets a new bearer token
def get_new_bearer_token():
    url = "https://id.twitch.tv/oauth2/token?client_id=" + os.getenv('CLIENT_ID') + "&client_secret=" + os.getenv(
        'CLIENT_SECRET') + "&grant_type=client_credentials"

    payload = {}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = json.loads(response.text)
    bearer_token = response_json["access_token"]
    return (bearer_token)


# Gets a list of all streams in the desired game category (stored in env file).
# Returns a dict with 2 elements. The first has key data, value is a list of streams
# Second element is pagination
def get_streams():
    url = "https://api.twitch.tv/helix/streams?game_id=" + os.getenv('GAME_ID')
    payload = {}
    headers = {
        'Authorization': 'Bearer ' + get_new_bearer_token(),
        'Client-Id': os.getenv('CLIENT_ID')
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return (response.text)


# Prints all games in the current games category
def read_streams():
    curr_timestamp = datetime.datetime.utcnow()
    streams_data = json.loads(get_streams())
    for i in streams_data['data']:
        print(i['user_name'] + ' - ' + str(i['viewer_count']) + ' - ' + str(
            curr_timestamp - datetime.datetime.strptime(str(i['started_at']), '%Y-%m-%dT%H:%M:%SZ')))

    print(streams_data['data'])


# Returns a list of all streams live in the current gaming category
def live_streams():
    return json.loads(get_streams())['data']


# Returns a list of all streams in the current games category that have over specified number of viewers.
# Viewer threshold determines how many viewers streamer must be over to be included in the list
def current_streamers_over_threshold_viewers(viewer_threshold, streams_data):
    streams_over_viewer_threshold = []
    for stream in streams_data:
        if stream["viewer_count"] > viewer_threshold and stream["language"] == "en":
            streams_over_viewer_threshold.append(stream)

    # print(streams_over_viewer_threshold)
    return streams_over_viewer_threshold


# If there are no streamers currently over viewer threshold, return false. Otherwise return true
def determine_if_streamers_over_viewer_threshold(viewer_threshold, streams_data):
    return len(current_streamers_over_threshold_viewers(viewer_threshold, streams_data)) != 0


# Returns a string of streamer names and viewers as a string from a list of stream objects
# Format: Streamer1 (viewers), steamer2 (viewers)
def streamer_list_names(stream_list):
    streamer_names_and_viewers = []
    for streamer in stream_list:
        streamer_names_and_viewers.append(f'{streamer["user_name"]} ({streamer["viewer_count"]} viewers)')

    return ', '.join(streamer_names_and_viewers)


# Convert timestamp to PST. Returns a string in PST
def get_timestamp():


    # Get the current time in UTC
    now_utc = datetime.now(pytz.utc)

    # Convert to PST
    pst_timezone = pytz.timezone('America/Los_Angeles')
    now_pst = now_utc.astimezone(pst_timezone)

    # Format the time
    return now_pst.strftime('%Y-%m-%d %H:%M:%S %Z')
