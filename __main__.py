# Kanwarpal Brar (JustColdToast)
# NYABot Re-write

# Dependencies
import threading
import discord
import time
import asyncio
from VoiceClientManager import VoiceClientManager
from AudioFileManager import FileManager
import os


# ClientManager handles all discord client interaction: responds to client events by communicating with
# other elements of program
class ClientManager(discord.Client):

    # Command Prefix String
    prefix = ">>"

    # Owner discord id
    ownerID = 287250659328393216

    # Holds a list of all valid audio/voice-channel commands
    voiceCommands = (">>play", ">>pause", ">>start", ">>leave", ">>resume", ">>stop", ">>queue", ">>skip")

    # Holds all Voice Client's associated with instance of Client
    voiceClientManagers = []

    # Holds all message auto-responders associated with instance of client
    responders = []

    # Main File Manager
    fileManager = FileManager(0)



    # ---- Helper Functions: These are used in conjunction with other functions below (called from them) ----

    # Given a user message, will isolate the command name in the message (up to first space)
    # and ignoring the command prefix
    # SHOULD ONLY BE CALLED AFTER CONFIRMING THAT THE COMMAND PREFIX WAS GIVEN
    def isolateCommand(self, msg):
        return msg.content.split(" ")[0].replace(self.prefix, "")

    # Handles vClient Disconnects, when passed a client
    async def disconnectVClient(self, vClient):
        # Tell the vClient to terminate
        await vClient.passCommand(">>leave")
        # Remove it from the list of vClients
        await self.voiceClientManagers.remove(vClient)
        print("Client Removed due to planned leave")

    # Creates a specific vClient, by a message
    async def createVClient(self, msg):
        print("vClient Created")
        # Tell the file manager that a client was added
        await self.fileManager.clientAdded()

        # Make Client and pass first command
        newClient = VoiceClientManager(msg, self.fileManager)
        await newClient.passCommand(msg)
        # Add to list of vClients
        self.voiceClientManagers.append(newClient)

    # will return a specific vClient by a given guild-id
    async def vClientByGuild(self, guildID):
        # Currently implemented as a linear search (nothing fancy)
        for vClient in self.voiceClientManagers:
            if vClient.guild.id == guildID:
                return vClient

        return None # No Guild of target ID found


    # ---- Inter-Class Function: responsible for setting up responders and voice clients ----

    async def passToVCManager(self, msg):
        # First check if a vClient exists, and retrieve it
        targetVClient = await self.vClientByGuild(msg.guild.id)

        # In the case that a play command was issued:
        if msg.content.startswith(self.voiceCommands[0]):
            # Check if client exists, create one if does not
            if targetVClient is None:
                print("creation reached")
                await self.createVClient(msg)
            else:
                # Otherwise, just pass the command
                await targetVClient.passCommand(msg)
        else:  # Any other voice command called
            # only pass command if vClient exists (only play can create clients)
            if targetVClient is not None:
                await targetVClient.passCommand(msg)


    # ---- Primary Functions ----
    # These are all the top-level commands that the bot can respond to, all stored in a dictionary of functions

    # Summon is a test function
    async def summon(self, msg):
        await msg.channel.send("Yo!")

    # Admin is an direct-control function, for debugging (and messing with people)
    async def admin(self, msg):
        # Safety check, only owner can call this method
        if msg.author.id == self.ownerID:
            while True:
                print("receiving")
                text = input(": ")
                if text == "break":
                    break
                else:
                    await msg.channel.send(msg)

    # vClients is a debugging function that returns the number of connected voice managers for client instance
    async def vClients(self, msg):
        await msg.channel.send("I am currently connected to "+str(len(self.voiceClientManagers))+" voice channels")

    # Below functions are all voice commands and will pass secondary to the manager function for them
    async def play(self, msg):
        print("played")
        await self.passToVCManager(msg)
    async def pause(self, msg):
        await self.passToVCManager(msg)
    async def leave(self, msg):
        await self.passToVCManager(msg)
    async def resume(self, msg):
        await self.passToVCManager(msg)
    async def stop(self, msg):
        await self.passToVCManager(msg)
    async def queue(self, msg):
        await self.passToVCManager(msg)
    async def skip(self, msg):
        await self.passToVCManager(msg)

    # A Dictionary of all primary functions, using the functions as value
    # This will return the function by it's key, and parameters can be passed on the dict.get
    # I basically only did this so that I didn't have a giant if-else block for every possible command input
    primaryFunc = {
        "summon": summon,
        "admin": admin,
        "vClients": vClients,
        "play": play,
        "pause": pause,
        "leave": leave,
        "resume": resume,
        "stop": stop,
        "queue": queue,
        "skip": skip
    }

    # ---- Event Functions----

    # Called when connection to discord service is established
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    # Handles all discord server message events, for all connected servers on client instance
    async def on_message(self, message):
        # Prevents bot from responding to itself
        if message.author == self.user:
            return

        # Main branches for handling text commands
        # Checks if message starts with command prefix: passes valid command if so
        if message.content.startswith(self.prefix):
            # Try-except because command might not exist, in which case NoneType is returned
            try:
                await self.primaryFunc.get(self.isolateCommand(message))(self, message)
            except TypeError: # Means command does not exist
                return

    # Called whenever there is a state change in a voice channel on any connected guild
    async def on_voice_state_update(self, member, before, after):
        return


# Set up client, client thread, and execute thread
client = ClientManager()
mainLoop = threading.Thread(target=client.run, args=("[TOKEN]",))
mainLoop.start()