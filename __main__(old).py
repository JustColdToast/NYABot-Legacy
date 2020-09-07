import asyncio

import discord
import time
import threading

# Below is the discord client class. It handles all functions involving direct interaction with discord

class ClientManager(discord.Client):
    vc = None
    censorList = []  # Represents a list of user ids to censor
    # structure of dictionary is: guildId: [arrayofUserId's]
    watchIdSet = {311652909421166592:[]}

    def delayed_response(self, delay, phrase, channel):
        time.sleep(delay)
        channel.sendMessage(phrase)
        # This function takes a phrase and waits a period of time, then sends it in discord chat
        # This must always be performed on a new thread, as to not disrupt other bot functions

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await self.watchForId()

    async def on_message(self, message):
        if message.author == client.user:  # Prevent bot from responding to itself
            return
        # print('Message from {0.author}: {0.content}'.format(message))

        # message type is passed to function, .content returns as a string
        if message.content.startswith(">>"):  # Only execute commands starting with >
            if message.content.startswith(">>summon"):  # Summon command
                await message.channel.send("Yo!")
            elif (message.content.startswith(">>admin") and message.author.id == 287250659328393216):  # Summon command
                while True:
                    print("receiving")
                    msg = input(": ")
                    if msg == "break":
                        break
                    else:
                        await message.channel.send(msg)
            elif (message.content.startswith(">>join")):  # Summons the bot to the senders voice channel
                self.vc = await message.author.voice.channel.connect()
                self.vc.play(discord.FFmpegPCMAudio('musicSrc/music.mp3'), after=lambda e: print('done', e))
            elif (message.content.startswith(">>pause")):
                if (self.vc!=None):
                    self.vc.pause()
                else:
                    message.channel.send("I'm not playing anything")
            elif (message.content.startswith(">>start")):
                voiceManager = VoiceClientManager(message.author.voice.channel)

                '''if (self.vc!=None):
                    self.vc.resume()
                else:
                    message.channel.send("I'm not playing anything")'''
            elif (message.content.startswith(">>stop")):
                if (self.vc!=None):
                    await self.vc.disconnect()
            elif (message.content.startswith(">>watchFor")):
                id = int(message.content.replace(">>watchFor ",""))
                if id in self.watchIdSet[message.guild.id]:
                    await message.channel.send("Already watching that id")
                else:
                    self.watchIdSet[message.guild.id].append(id)
                    await message.channel.send("Watching")
            elif (message.content.startswith(">>censor")):
                id = int(message.content.replace(">>censor ",""))
                if id in self.censorList:
                    await message.channel.send("Already censoring")
                else:
                    self.censorList.append(id)

            elif (message.content.startswith(">>regGuild")):
                self.regisGuild = message.guild
                await message.channel.send("Guild Registered")

            elif (message.content.startswith(">>troll")):
                # Command provided in form: >>troll [count]
                # Count defines the number of times a trolling is performed
                # This is currently only designed for Oz, future implementations may use different music sounds
                content = message.content.split(" ")
                await self.commitAction("troll", message.author.voice.channel, int(content[1]))
                
            elif (message.content.startswith(">>jaydonGay")):
                print("Jaydon gay")
                #  This method is designed to piss of jaydon, not yet implemented

            elif (message.content.startswith(">>play")):
                content = message.content.replace(">>play ","")  # Removes everything except the command
                if content.lower() == "test":
                    self.vc = await message.author.voice.channel.connect()
                    self.vc.play(discord.FFmpegPCMAudio('musicSrc/music.mp3'), after=lambda e: print('done', e))
                elif content.lower() == "chungas":
                    self.vc = await message.author.voice.channel.connect()
                    self.vc.play(discord.FFmpegPCMAudio('musicSrc/chungas.mp3'), after=lambda e: print('done', e))
                elif content.lower() == "chammak":
                    self.vc = await message.author.voice.channel.connect()
                    self.vc.play(discord.FFmpegPCMAudio('musicSrc/Chammak.mp3'), after=lambda e: print('done', e))
        else:
            if (message.author.id == 503720029456695306):
                await message.channel.send("Hi Dadbot, I'm Nyabot!")
            elif(message.author.id in self.censorList):  # This branch deletes the messages of anyone in the censor list
                await message.delete()

    async def watchForId(self): # This class handles watching for a specific set of id's when called, in voice channels
        while True:
            # It runs in cycles of every 10 seconds
            # idSet should be an array of discord id's. They should be longs
            breaker = False
            await asyncio.sleep(10)
            for serverId in self.watchIdSet:
                for channel in client.get_guild(serverId).voice_channels:
                    if channel in [cli.channel for cli in client.voice_clients]:  # If connected to the channel already
                        breaker = True
                        break
                    for user in channel.members:
                        for userId in self.watchIdSet[serverId]:
                            if userId == user.id:
                                print("Found")
                                await self.commitAction("troll", channel)
                                await asyncio.sleep(10)  # After performing an action you can sleep

                    if breaker==True:
                        break

    async def commitAction(self, type, channel, count):  # Responsible for performing specific actionsets for the watchForId def
        if type == "memeSong":
            self.vc = await channel.connect()
            self.vc.play(discord.FFmpegPCMAudio('musicSrc/memeSong.mp3'))
            await asyncio.sleep(28)
            await self.vc.disconnect()
        elif type == "troll":
            self.vc = await channel.connect();  # Connect to the voice channel
            await asyncio.sleep(30)
            for i in range(count):
                self.vc.play(discord.FFmpegPCMAudio("musicSrc/mechLunchSeq.mp3"))
                await asyncio.sleep(60)  # Wait 20 seconds before the next round
            await self.vc.disconnect()  # Close the line

class VoiceClientManager(ClientManager):
    def __init__(self, channel, **options):
        super().__init__(**options) # Call the initilization of the super
        self.vc = self.connectChannel(channel)  # Setup the target vc

    async def connectChannel(self, channel):
        return channel.connect()

client = ClientManager()
mainLoop = threading.Thread(target=client.run, args=("NDE2NzU2NzM4NTA3ODAwNTc2.XdnSmw.MwGh3FhjCOiQdc0QG9fKH8nE_Bw",))
idWatchThread = threading.Thread(target=client.watchForId)
mainLoop.start()

'''
This is an old method of managing vClients
    async def passToVCManager(self, message):
        if message.content.startswith(self.voiceCommands[0]):  # If a play is requested
            if len(self.voiceClientManagers) == 0:
                # Create a new manager, append to list, then pass command
                voiceClient = await message.author.voice.channel.connect()
                self.voiceClientManagers.append(VoiceClientManager(voiceClient, message.guild))
                await self.voiceClientManagers[len(self.voiceClientManagers) - 1].passCommand(message.content)
            else:
                # This branch exists if there are voice clients in use
                # It must first check if a client exists for the current guild
                if message.guild.id == [vClient.guild.id for vClient in self.voiceClientManagers]:
                    # If the voice client manager already exists, respond with a message
                    await message.channel.send("I am already connected to a channel on this server")
                else:
                    # If there is no existing client for this channel, create one
                    # Create a new manager
                    voiceClient = await message.author.voice.channel.connect()
                    self.voiceClientManagers.append(VoiceClientManager(voiceClient, message.guild))
                    await self.voiceClientManagers[len(self.voiceClientManagers) - 1].passCommand(message.content)
        elif message.content.startswith(self.voiceCommands[5] or self.voiceCommands[3]):
            for vClient in self.voiceClientManagers:
                if vClient.guild == message.guild:
                    print(self.voiceClientManagers)
                    await vClient.passCommand(message.content)
                    await self.voiceClientManagers.remove(vClient)
                    print(self.voiceClientManagers)
        else:
            for vClient in self.voiceClientManagers:
                if vClient.guild == message.guild:
                    await vClient.passCommand(message.content)
'''



