import asyncio

import discord
import time
import threading

from MessageResponder import MessageResponder
from VoiceClientManager import VoiceClientManager

'''
THINGS TO DO:
1: Clean up your voice commands in passToVCManager section, split everything into different methods
2: Take care of handling errors when passing commands, such as invalid file playing (nonexistant name, no name)
'''


# Below is the discord client class. It handles all functions involving direct interaction with discord chat messages


class ClientManager(discord.Client):
    voiceCommands = (">>play", ">>pause", ">>start", ">>leave", ">>resume", ">>stop", ">>queue", ">>stream", ">>skip")
    voiceClientManagers = []
    censorList = []  # Represents a list of user ids to censor
    # structure of dictionary is: guildId: [arrayofUserId's]
    watchIdSet = {311652909421166592: []}
    responder = None

    async def deleteVClient(self, vClient):
        self.voiceClientManagers.remove(vClient)

    # The below method manages organization of VoiceClientManagers, and passing of commands
    async def createVClient(self, message):
        # Given a message, create a voiceClient manager
        # This is changed from a previous method where the connection was handled in this file, now it's in VoiceClientManager
        self.voiceClientManagers.append(VoiceClientManager(message))
        await self.voiceClientManagers[len(self.voiceClientManagers) - 1].passCommand(message)

    async def disconnectVClient(self, vClient):
        await vClient.passCommand(">>leave")
        await self.voiceClientManagers.remove(vClient)
        print("Client Removed due to planned leave")

    async def findVClientByGuild(self, findGuild):
        for vClient in self.voiceClientManagers:
            if vClient.guild == findGuild:
                return vClient
        return None

    async def findVClientById(self, findId):
        for vClient in self.voiceClientManagers:
            if vClient.guild.id == findId:
                return vClient

    async def passToVCManager(self, message):
        # Given a play command, check if a voice client exists
        if message.content.startswith(self.voiceCommands[0]):
            # Now check if the voice client exists
            vClient = await self.findVClientByGuild(message.guild)
            if vClient is None:  # If nonetype is returned, create client
                await self.createVClient(message)
            else:
                # Otherwise if it does exist, pass the command
                await vClient.passCommand(message)
        # elif message.content.startswith(self.voiceCommands[5] or self.voiceCommands[3]):
        #     # Given a disconnect or leave command, perform the instructions for a disconnect
        #     await self.disconnectVClient(await self.findVClientByGuild(message.guild))
        else:
            # Given any other command check if the client exists, and pass command
            # Only the play command has the ability to create a new VoiceClientManager
            vClient = await self.findVClientByGuild(message.guild)
            if vClient is not None:
                await vClient.passCommand(message)

    def isVoiceCommand(self, message):
        for command in self.voiceCommands:
            if message.content.startswith(command):
                return True
        return False

    async def passToResponder(self, message):
        print("responding")
        if self.responder is None:
            self.responder = MessageResponder(message)
        else:
            await self.responder.passCommand(message)

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.author == client.user:  # Prevent bot from responding to itself
            return
        # print('Message from {0.author}: {0.content}'.format(message))

        # message type is passed to function, .content returns as a string
        if message.content.startswith(">>"):  # Only execute commands starting with >
            if message.content.startswith(">>summon"):  # Summon command
                await message.channel.send("Yo!")
            elif message.content.startswith(">>admin") and message.author.id == 287250659328393216:  # Summon command
                while True:
                    print("receiving")
                    msg = input(": ")
                    if msg == "break":
                        break
                    else:
                        await message.channel.send(msg)
            elif message.content.startswith(">>vClients"):
                await message.channel.send("I am currently connected to "+str(len(self.voiceClientManagers))+" voice channels")
            elif message.content.startswith(">>respondto"):
                await self.passToResponder(message)
            elif self.isVoiceCommand(message):
                # This branch exists if the message provided is a voice command
                # It passes the command to the voiceClientManager method on an await
                await self.passToVCManager(message)

    async def on_voice_state_update(self, member, before, after):
        # State changes are monitored so the bot can delete unused voice clients when it is disconnected
        # Otherwise, disconnections would leave the client open, whereas the leave command will not
        # By letting the manager handle the deletion of the client by an update I no longer have to manually do it
        # ... Now I can just pass the command to the bot and deletion is done on any general leave
        if (member == client.user) and (after.channel is None):
            for vClient in self.voiceClientManagers:
                if vClient.guild == before.channel.guild:
                    await self.deleteVClient(vClient)
                    print("Client deleted due to disconnect")


client = ClientManager()
mainLoop = threading.Thread(target=client.run, args=("[YourTokenHere]",))
mainLoop.start()
