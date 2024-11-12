# bot.py

import os

import discord
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker

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
            # print("current list = " + str(current_streamers_over_threshold_list))
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


            # print("prev str status1: " + str(previous_streamer_viewer_threshold_status))
            # print("prev str status 2:" + str(previous_streamer_viewer_threshold_size))

            previous_streamer_viewer_threshold_status = current_streamer_over_threshold_status
            previous_streamer_viewer_threshold_size = current_streamer_over_threshold_size

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


