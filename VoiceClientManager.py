# Basically need to rewrite this entire method to handle downloading


import discord
import asyncio
from youtube_search import YoutubeSearch
from mutagen.mp3 import MP3


class VoiceClientManager:
    # A list of all valid voice commands
    voiceCommands = (">>play", ">>pause", ">>start", ">>leave", ">>resume", ">>stop", ">>queue", ">>skip")
    isPlaying = False

    # ---- Helper Functions ----

    # Given a user message, will isolate the command name in the message (up to first space)
    # and ignoring the command prefix
    # SHOULD ONLY BE CALLED AFTER CONFIRMING THAT THE COMMAND PREFIX WAS GIVEN
    def isolateCommand(self, msg):
        data = msg.content.split(" ")[0].replace(">>", "")
        print("Command Called:" + data)
        return data

    # Used to check if a given timestamp is within the maximum runtime
    def isValidLength(self, timestamp):
        times = timestamp.split(":")
        if len(times) <= 2:
            return True
        elif len(times) > 3:
            return False
        elif (int(times[0])) + (int(times[1]) / 60) <= self.maxLength:
            return True
        else:
            return False

    # Given a video time-stamp format, will return the length in seconds
    def lengthSeconds(self, timestamp):
        times = timestamp.split(":")  # Isolates each part of the timestamp
        length = 0
        for index in range(0, len(times)):
            length += int(times[index]) * (60 ** index)
        return length

    # Given a message with a song query, will return the url of a youtube search with query, as well as it's title, and
    # length in seconds
    # Also responsible for checking if the video intended to use is too long
    async def returnTitleUrlLength(self, searchterms):
        # First format the terms by removing spaces
        searchterms = searchterms.replace(" ", "_")
        result = YoutubeSearch(searchterms, max_results=1).to_dict()[0]
        if self.isValidLength(result.get('duration')):
            return (result.get('title'),
                    "https://www.youtube.com/watch?v=" + result.get('id'),
                    self.lengthSeconds(result.get('duration')))
        else:
            return None

    # Will establish a connection with a voice channel
    async def connectVClient(self, message):
        if self.voice_client is None:
            # Provided a channel, set the vClient of the object by connecting
            # By this method I no longer have to manage connection of vClient in the main manager
            if message.author.voice.channel is None:
                await message.channel.send("You are not connected to a voice channel")
            else:
                self.voice_client = await message.author.voice.channel.connect()

    # Responsible for getting a file from the fileManager, given a url
    async def getRequestedFile(self, url):
        file = await self.fileManager.retriveFile(url)
        if file is None:
            file = await self.fileManager.downloadFile(url)
        return file

    # Function responsible for starting music playback
    async def startQueue(self, message):
        terms = message.content.replace(">>play ", "")
        if terms == "debug":
            print("Entering Debug Play")
            self.queued.append("test.mp3")
            await self.connectVClient(message)
            await self.playback()
        else:
            print("Entering Standard Play")
            await self.getFileStartPlayback(message, terms)

    async def getFileStartPlayback(self, message, terms):
        queryData = await self.returnTitleUrlLength(terms)

        # If titleUrl is returned as a None, that means that video was too long to handle, send message to alert
        if queryData is None:
            await message.channel.send("Sorry, that video is too long for me to handle. Try to keep it below "
                                       + str(self.maxLength) + " hours")
        else:
            file = await self.getRequestedFile(queryData[1])
            print("recieved:" + file)
            print("queuing")
            self.queued.append((file, queryData[2]))
            await self.connectVClient(message)
            await self.playback()

    # Disconnected the vClient from the voice channel
    async def disconnectVClient(self):
        # The voice client disconnect and connect commands must be awaited as they involve interaction with discord
        # directly, as opposed to the existing manager
        await self.voice_client.disconnect()

    # Function responsible for adding songs to the queue, given the original message
    async def queueSong(self, msg):
        terms = msg.content.replace(">>play ", "")
        await self.getFileStartPlayback(msg, terms)

    # This function is responsible for actually playing the songs in the queue
    # Must be called by the play function
    async def playback(self):
        if self.isPlaying:
            await self.playback()
        else:
            if len(self.queued) == 0:
                await self.disconnectVClient()
            else:
                target = self.queued[0][0]
                print("Now Playing:"+target)
                self.queued = self.queued[1:]
                self.swapPlayState(True)
                await self.voice_client.play(discord.FFmpegPCMAudio(target), after=self.swapPlayState(False))
                await asyncio.sleep(self.queued[0][1]+2)

    # Uses a boolean to set the current playback state (used to determine if something is currently being played)
    def swapPlayState(self, state):
        self.isPlaying = state

    # ---- Primary Functions ----
    async def play(self, msg):
        # In the case that the queue is empty, start it
        if len(self.queued) == 0:
            await self.startQueue(msg)
        elif self.voice_client is None:
            await self.startQueue(msg)
        else:
            await self.queueSong(msg)
            await self.playback()

    async def pause(self, msg):
        print("Pause Call")
        if self.voice_client is not None:
            await self.voice_client.pause()

    async def start(self, msg):
        if self.voice_client is not None:
            self.voice_client.resume()

    async def leave(self, msg):
        if self.voice_client is not None:
            print("Executing Leave")
            self.queued = []  # Empty Queue and disconnect
            await self.disconnectVClient()

    async def resume(self, msg):
        # Does the same thing as start
        if self.voice_client is not None:
            self.voice_client.resume()

    async def stop(self, msg):
        # Does the same thing as pause
        if self.voice_client is not None:
            self.voice_client.pause()

    async def queue(self, msg):
        await msg.channel.send("Kanwarpal hasn't added this feature yet")

    async def skip(self, msg):
        await msg.channel.send("Kanwarpal hasn't added this feature yet")

    # A Dictionary of all primary functions, using the functions as values
    primaryFunc = {
        "play": play,
        "pause": pause,
        "start": start,
        "leave": leave,
        "resume": resume,
        "stop": stop,
        "queue": queue,
        "skip": skip
    }

    # Constructor
    def __init__(self, message, fm):
        # Set up instance variables by the constructor parameters
        self.voice_client = None
        self.guild = message.guild
        self.currentChannel = message.channel
        self.queued = []  # An array which holds all audio sources queued up
        self.fileManager = fm  # This is the file manager that the vClient must correspond with
        self.maxLength = 1.5  # The maximum length video allowed to be handled

    # This is the primary function to allow interaction with this instance of a vClient Manager from other
    # objects
    async def passCommand(self, msg):
        # Note that this method should only ever be passed commands from the guild associated with this vClient instance
        try:
            await self.primaryFunc.get(self.isolateCommand(msg))(self, msg)
        except Exception as e:
            print(e)
