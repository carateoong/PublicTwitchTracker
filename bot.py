# bot.py

import os

import discord
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import func, desc, cast
from sqlalchemy.sql import select
from sqlalchemy.sql import text, literal_column
from sqlalchemy.orm import aliased
from sqlalchemy import Integer, DateTime
#from sqlalchemy.sql.functions import row_number
from sqlalchemy.sql import over

# Create alias for subquery
from sqlalchemy import select
from sqlalchemy.orm import aliased

from sqlalchemy.sql import label
from datetime import datetime
from zoneinfo import ZoneInfo
import pytz


import twitch
import asyncio

from database import get_engine, streams

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client(intents=discord.Intents.default())

# Handles the event that the Client has made a connection to Discord and prepared response data
"""
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )"""

"""
async def setup_hook(self) -> None:
    # start the task to run in the background
    determine_if_streamers_over_viewer_thresholds.start()
"""

#Connects to database
def database_connect():
    Base = declarative_base()
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

# I
def log_streams_in_database(streams_data):
    """
    For each stream in the stream_data list, logs into the database
    :param streams_data: A list of all streams live in the current gaming category in a json object
    :return: None
    """
    session = database_connect()
    for s in streams_data:

        stream_entry = streams('', s["id"], s["user_id"], s["user_login"], s["user_name"], s["game_id"], s["game_name"],
                               s["type"], s["title"], s["tags"], s["viewer_count"], s["started_at"],s["is_mature"])
        session.add(stream_entry)

    session.commit()

def get_avg_runtime_lastfivestreams_table():
    """
    use sqlalchemy to get a table that has all streamers and the avg runtime of the last 5 streams in game category
    :return: results list??
    """
    engine = get_engine()

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                user_name,
                AVG(avg_viewer_count) AS avg_viewer_count_lastfivestreams,
                AVG(runtime) AS avg_runtime_lastfivestreams
            FROM (
                SELECT
                    user_name,
                    id AS stream_id,
                    AVG(viewer_count) AS avg_viewer_count,
                    started_at::timestamptz AS started_at,
                    MAX(time_created - started_at::timestamptz) AS runtime,
                    ROW_NUMBER() OVER (PARTITION BY user_name ORDER BY started_at DESC) AS rid
                FROM streams
                GROUP BY user_name, stream_id, started_at
            ) a
            WHERE rid > 1 and rid <= 6
            GROUP BY user_name
            ORDER BY avg_viewer_count_lastfivestreams DESC
        """))

        rows = result.fetchall()
        #print(rows)
        return rows
        #for row in rows:
        #    print(dict(row))  # convert Row to dict

def convert_str_to_PST(str_time):
    # Original UTC time string
    #utc_str = '2025-04-06T00:30:01Z'

    # Parse to datetime with UTC timezone
    utc_dt = datetime.strptime(str_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("UTC"))

    # Convert to US/Pacific (PST or PDT depending on date)
    pst_dt = utc_dt.astimezone(ZoneInfo("America/Los_Angeles"))
    return pst_dt

def get_avg_runtime(stream, lastfivestreams_table):
    """
    get avg runtime of stream
    :param stream:
    :param lastfivestreams_table:
    :return: avg runtime in hours
    """
    avg_runtime = 0
    for entry in lastfivestreams_table:
        if stream["user_name"] == entry[0]:
            avg_runtime = entry[2]
    return avg_runtime

def check_if_streamer_close_to_ending(stream, avg_runtime):
    """
    find streamer in lastfivestreams_Table, and compare current stream's ending time to current avg runtime.
    :param stream: current stream
    :param lastfivestreams_table:
    :return: difference between streamer and usual average runtime (negative means current stream is below avg, positive
    means current stream is longer than average) in hours
    """


    # Get the current time in UTC
    now_utc = datetime.now(pytz.utc)

    # Convert to PST
    pst_timezone = pytz.timezone('America/Los_Angeles')
    now_pst = now_utc.astimezone(pst_timezone)
    print(now_pst)
    print(convert_str_to_PST(stream["started_at"]))
    print(avg_runtime)
    print(now_pst - convert_str_to_PST(stream["started_at"]))
    #return difference
    #will be positive if current stream length > avg runtime, negative if opposite in hours
    return (now_pst - convert_str_to_PST(stream["started_at"]) - avg_runtime).total_seconds()/3600


#@tasks.loop(minutes=10.0, count=None)
async def determine_if_streamers_over_viewer_threshold(viewer_threshold):
    await client.wait_until_ready()  # ensures cache is loaded
    channel = client.get_channel(int(os.getenv('CHANNEL')))
    previous_streamer_viewer_threshold_status = False
    previous_streamer_viewer_threshold_size = 0
    await channel.send(f"Good time to stream! There is no one over {viewer_threshold} viewers streaming your game")

    # Connect to database
    session = database_connect()

    while not client.is_closed():
        try:

            # Get a list of stream data and log it to database
            stream_data = twitch.live_streams()
            log_streams_in_database(stream_data)


            # check if status has changed from last period
            current_streamer_over_threshold_status = twitch.determine_if_streamers_over_viewer_threshold(viewer_threshold,
                                                                                                         stream_data)
            current_streamers_over_threshold_list = twitch.current_streamers_over_threshold_viewers(viewer_threshold,
                                                                                                    stream_data)
            current_streamer_over_threshold_size = len(current_streamers_over_threshold_list)

            # print("current status = " + str(current_streamer_over_threshold_status))
            print("current list = " + str(current_streamers_over_threshold_list))
            # print("current size = " + str(current_streamer_over_threshold_size.env))

            # Check if streamers over threshold status has changed from previous loop
            if (previous_streamer_viewer_threshold_status != twitch.determine_if_streamers_over_viewer_threshold(
                    viewer_threshold, stream_data) or
                    (previous_streamer_viewer_threshold_size != current_streamer_over_threshold_size)):
                # status has changed, send message
                if current_streamer_over_threshold_status:
                    await channel.send(
                        f'Time: {twitch.get_timestamp()} Your window has closed. There are '
                        f'{len(current_streamers_over_threshold_list)} popular people'
                        f' over {viewer_threshold} viewers in the English category streaming your game.  '
                        f'\n Streamers: '
                        f'{twitch.streamer_list_names(current_streamers_over_threshold_list)}.')

                else:
                    await channel.send(f"Good time to stream! There is no one over {viewer_threshold} "
                                       f"viewers streaming your game")

            avg_runtime_lastfivestreams_table = get_avg_runtime_lastfivestreams_table()

            previous_streamer_viewer_threshold_status = current_streamer_over_threshold_status
            previous_streamer_viewer_threshold_size = current_streamer_over_threshold_size

            for stream in current_streamers_over_threshold_list:
                avg_runtime = get_avg_runtime(stream, avg_runtime_lastfivestreams_table)
                runtime_diff = check_if_streamer_close_to_ending(stream, avg_runtime)
                print(runtime_diff)

                if runtime_diff > 0 and runtime_diff % 0.5 < 0.15:
                    await channel.send(f'Streamer {stream["user_name"]} with {stream["viewer_count"]} viewers may be'
                                       f' ending soon. They usually stream for {avg_runtime} hours but have streamed'
                                       f' {runtime_diff} hours over their usual streaming time')

            # print("prev str status1: " + str(previous_streamer_viewer_threshold_status))
            # print("prev str status 2:" + str(previous_streamer_viewer_threshold_size))



            # print("prev str status2: " + str(previous_streamer_viewer_threshold_status))
            # print("prev str status 2:" + str(previous_streamer_viewer_threshold_size))

            # wait time (in seconds)
            print("hello")
            await asyncio.sleep(300)


        except Exception as e:
            print("an error has occurred")
            print(e)


# on_ready is always called when bot has finished logging in and setting up
# This function notifies that the bot has connected to Discord
# Also starts background task, which is determining if streamer have over 100 viewers
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'{client.user} has connected to Database!')

    #determine_if_streamers_over_viewer_threshold.start()
    client.loop.create_task(determine_if_streamers_over_viewer_threshold(100))

client.run(TOKEN)


