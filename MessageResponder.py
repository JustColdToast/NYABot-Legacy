# Kanwarpal Brar
# This class is for a joke feature where upon issuing a command the bot will respond to any message by someone with the same image
# In any final builds this will be deactivated, as it could be abused for spam
# What's passed to the object is the original message, from which author ids and such are retrieved
import discord
import asyncio


class MessageResponder:
    def __init__(self, message):
        self.guild = message.guild  # Set the guild
        self.targetIds = [message.mentions[0], ]  # Retrieve the user mentioned
        self.imgUrl = [message.attachments[0].url, ]  # get the image url

    async def passCommand(self, message):  # Is accessed by main
        # First check if there is a mention
        if len(message.mentions) > 0:
            # If there is a mention, then add it
            await self.addUser(message)
        else:
            await self.respondTo(message)  # RespondTo checks if the user is a target and responds, otherwise nothing happens

    async def respondTo(self, message):
        url = self.retrieveContent(message)
        if url is not None:
            await message.channel.send(url)

    def retrieveContent(self, message):  # This method checks for the users id and retrieves the associated image
        for i in range(0, len(self.targetIds)):
            if self.targetIds[i] == message.author.id:
                return [self.imgUrl[i]]
        return None

    async def addUser(self, message):
        if message.author.id not in self.targetIds:
            self.targetIds.append(message.author.id)
            try:
                self.imgUrl.append(message.attachments[0].url)
            except:  # Yes this is a broad except. No, I don't want to fix it
                await message.channel.send("There is no image attachment")
