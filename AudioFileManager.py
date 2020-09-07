# The audio file manager is in charge of the downloading of audio files from YTDL, and providing them to players
# By seperating the file manager from the audio player a single entity can communicate with multiple players
# Ideally, the file manager can be used to monitor usage of specific files and delete files that have not been used
# ^ In a while, thus clearing up space

# Kanwarpal Brar

import discord
import youtube_dl
import asyncio


class FileManager:
    def __init__(self):
        filesInUse = []  # Setup an array of files that are currently being used


# Below I set up YTDL to download audio with
ydl_opts = {}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=dP15zlyra3c'])