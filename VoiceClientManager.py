# This class is an overall part of the discord bot, specifically designed for handling voice clients.
# seperating voice clients from general functions cleans up the main execution file.
# Pass a guild and channel to the class to allow it to operate based on them
import discord
import asyncio
import os
from mutagen.mp3 import MP3
import youtube_dl
from youtube_search import YoutubeSearch

# Effectively, I provide this class access to the main client with reference to the specific guild and channel it manages
# This cleans up code, and prevents commands from overlapping with different voice clients
# The only other way to manage this would be to create an array/list of voice clients and manage each individually
'''
Current Issues:
1: There is no real way to get commands directly in the manager without creating a list of voiceclientManagers
At the point where that happens, I might as well just have a list of voice clients.
2: There will likely be some issues with asynchronous functions when working with two different classes
3: Disconnection must be handled by the main file as it involves removing the class from the manager.
At the same time, it must be passed to the client as well, so it's a two-stage process. First: send disconnect command
to the voiceclient, second: remove from VClient array in main
4: For some reason I'm putting my todo list in the code, why don't I just make a trello???
'''


# TODO Currently voice commands given from outside any voice channel raises an error
# TODO Currently there is a major issue with YTDL where the stream link for the target video will expire while streaming
# TODO ^ It seems the only way to fix this is to download songs in advance, but that will be system heavy and slow
class VoiceClientManager:
    voiceCommands = (">>play", ">>pause", ">>start", ">>leave", ">>resume", ">>stop", ">>queue", ">>stream", ">>skip")

    def __init__(self, message):
        # Set up instance variables by the constructor parameters
        self.voice_client = None
        self.guild = message.guild
        self.currentChannel = message.channel
        self.queue = []  # An array which holds all audio sources queued up
        print("VoiceClientManager created")

    # Below are methods handling functions of the voice client

    # This method is called by the ClientManager to
    async def passCommand(self, message):
        # This method should only ever receive commands from it's corresponding guild
        # Otherwise, commands between guilds would work on any given voiceClient
        if self.voice_client is None:
            # If the voice client is not established, the only valid command is a play command
            if message.content.startswith(self.voiceCommands[0]):
                terms = message.content.replace(">>play ", "")
                await self.startQueue(message, terms)
        else:
            # First check is message is from same channel as bot\
            if message.author.voice.channel == self.voice_client.channel:
                if message.content.startswith(self.voiceCommands[1]):
                    await self.pausePlayback()
                elif message.content.startswith(self.voiceCommands[4] or self.voiceCommands[2]):
                    await self.resumePlayback()
                elif message.content.startswith(self.voiceCommands[0]):  # PLAY COMMAND
                    # First check if a vClient has been established
                    url = message.content.replace(">>play ", "")
                    # Given a play command, add the url to queue
                    print("Queuing in branches: " + url)
                    await self.queueSong(message, url)
                elif message.content.startswith(self.voiceCommands[3]):
                    await self.disconnectVClient()
                elif message.content.startswith(self.voiceCommands[6]):
                    # TODO Change this branch to run a special queue method which prints the song queue
                    await self.printQueue(message)
                elif message.content.startswith(self.voiceCommands[7]):
                    url = message.content.replace(">>stream ", "")
                    await self.stream(url)
                elif message.content.startswith(self.voiceCommands[8]):
                    await self.skipSong()
            else:
                # If the message is sent from outside the current channel
                await message.channel.send("I am currently in use in a different channel")

    # Below methods are kind of self-explanatory
    async def pausePlayback(self):
        self.voice_client.pause()

    async def resumePlayback(self):
        self.voice_client.resume()

    async def playQueued(self):
        self.queue.pop(0)
        if len(self.queue) == 0:
            print("Leaving by queue")
            await self.disconnectVClient()
        else:
            await self.stream(self.queue[0])

    async def queueSong(self, message, terms):
        try:
            url = await self.returnUrl(terms)
            player = await YTDLSource.from_url(url, stream=True)
            self.queue.append(player)
            await message.channel.send("**" + player.title + " by " + player.data.get("id") + "** added to queue")
        except:
            await message.channel.send("I could not find that video on youtube")


    async def play(self, command):  # NOTE PLAY METHOD REPLACED BY STREAM (for youtube videos)
        # Provide a command extracted from the given message from discord, this is used to identify source requested
        print("Asked to play " + command)
        # If something is playing, add to queue, otherwise leave
        # No not await commands for the voice client, it has already been established and the method itself is awaited
        length = int(MP3("./musicSrc/" + command + ".mp3").info.length) + 2
        self.voice_client.play(discord.FFmpegPCMAudio('musicSrc/' + command + '.mp3'))
        # Sleep for the length of the file (only works for mp3's currently)
        print(length)
        await asyncio.sleep(length)
        await self.playQueued()

    async def disconnectVClient(self):
        # The voice client disconnect and connect commands must be awaited as they involve interaction with discord
        # directly, as opposed to the existing manager
        await self.voice_client.disconnect()

    async def checkIfPlaying(self):
        while True:
            if not self.voice_client.is_playing():
                print("leaving")
                await self.disconnectVClient()
            else:
                await asyncio.sleep(5)

    async def stream(self, player):
        # Given a url and channel announce current playback and then get a YTDL stream source
        self.voice_client.play(player, after=lambda e: self.advanceQueue())
        await self.currentChannel.send("**Now playing:** " + player.title + " by " + player.data.get("uploader"))

    async def connectVClient(self, message):
        # Provided a channel, set the vClient of the object by connecting
        # By this method I no longer have to manage connection of vClient in the main manager
        if message.author.voice.channel is None:
            await message.channel.send("You are not connected to a voice channel")
        else:
            self.voice_client = await message.author.voice.channel.connect()

    async def skipSong(self):
        # This method progresses the queue
        if self.voice_client.is_playing():
            self.voice_client.stop()
            await self.playQueued()

    async def startQueue(self, message, terms):
        await self.connectVClient(message)
        url = await self.returnUrl(terms)
        self.queue.append(await YTDLSource.from_url(url, stream=True))
        print(self.queue[0].data)
        await self.stream(self.queue[0])

    def advanceQueue(self):
        # This method is called after a song is finished playing and removes a song from the queue list
        # It runs a threadsafe async to a different function, which allows it to be passed it to the VClient after
        try:
            asyncio.run_coroutine_threadsafe(self.playQueued(), self.voice_client.loop)
        except:  # Yes this is a broad error catch, I blame the discord py module
            pass

    async def printQueue(self, message):
        msg = "Current Queue:\n`"
        for player in self.queue:
            msg += player.title + "\n"
        await message.channel.send(msg + "`")

    async def returnUrl(self, searchterms):
        # First format the terms by removing spaces
        searchterms = searchterms.replace(" ", "_")
        return "https://www.youtube.com/watch?v=" + YoutubeSearch(searchterms, max_results=1).to_dict()[0].get("id")


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
