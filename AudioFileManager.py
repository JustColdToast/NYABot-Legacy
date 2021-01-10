# Kanwarpal Brar (JustColdToast)
# NYABot Re-write

# Dependencies
import discord
from pytube import YouTube
import asyncio
import sqlite3
import os
import time


# File Manager communicates with all vClients to pass requested audio files, as well as to monitor which files have
# not been access in a long time (for cleanup)
class FileManager:
    def __init__(self, vclientscount):
        # Holds the file name for the sqlite database being used
        self.database = "fileBase.db"

        # Holds the count of connected vClients
        self.vCount = vclientscount

        # Setup the sqlite database (needs to be recreated each time bot is run)
        if not os.path.exists(self.database):
            self.setupDB(self.database)

    # ---- Helper Functions: These are used in conjunction with other functions below (called from them) ----

    # setupDB creates the database used to store data about files being used
    def setupDB(self, dbName):
        conn = sqlite3.connect(dbName)
        curs = conn.cursor()
        # Below is the table that holds all files and their last access date
        # fileName and lastAccessTime are self explanatory, usedby counts how many vClients are using this file
        curs.execute('''create table files (fileName text, url text, lastAccessTime real, usedby integer)''')
        # Save Changes and end connection to database
        conn.commit()
        conn.close()

    # Given a url, will check how many vClients are using a file associated with that url in the database
    async def getUsedBy(self, url, dbCurs):
        for row in dbCurs.execute('SELECT * FROM files'):
            if row[1] == url:
                return row[3]
        return 0

    # Given a specific youtube url, will check if it's file exists in the given database, returns it
    def checkDBForFile(self, url, dbCurs):
        # Iterate through each row for the file
        for row in dbCurs.execute('''select * from files'''):
            if row[1] == url:
                return row[0]  # Return the filename

        # If file not find return None
        return None

    # Will Return a connection to the database, and an associated cursor, in a tuple, or None
    def databaseConnect(self):
        try:
            conn = sqlite3.connect(self.database)
            curs = conn.cursor()
            return (conn, curs)
        except sqlite3.Error as error:  # If error occurs, return null
            print(error)
            return None

    # Will add a specific file to the database, along with it's access time
    async def addFileToDB(self, filename, url, accesstime, usedby):
        dbData = self.databaseConnect()
        if dbData is not None:
            dbData[1].execute('''insert into files values (?,?,?,?)''', (filename, url, accesstime, usedby))
            dbData[0].commit()
            dbData[1].close()
            dbData[0].close()

    # Given a filename, url, and accesstime (for a file that exists in the database), will update
    # the access time, and increment the usedby count by usedbyAddition
    async def updateFileInfo(self, url, usedbyAddition):
        dbData = self.databaseConnect()

        if dbData is not None:
            updateQuery = '''Update files set lastAccessTime = ?, usedby = ? where url = ?'''
            count = await self.getUsedBy(url, dbData[1])
            dbData[1].execute(updateQuery, (time.time(),
                                            usedbyAddition + count,
                                            url))
            dbData[0].commit()
            dbData[1].close()
        else:
            print("Connection failed to establish in file info update")

    # ---- Inter-Class Function: responsible for setting up responders and voice clients ----

    # Called from __main__.py, tells the FileManager that it just had another client created attached
    async def clientAdded(self):
        self.vCount += 1

    # Method used to receive file requests from a vClient, from database
    async def retriveFile(self, url):
        # Setup Database Connection
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        # Let's hope that calling this synchronous function doesn't hold up everything too long
        searchResult = self.checkDBForFile(url, curs)

        # In the case that the file was found, the vClient will start using it, so update lastAccessTime and user count
        if searchResult is not None:
            print(searchResult+" was found")
            await self.updateFileInfo(url, 1)

        return searchResult  # May be None, must be checked by vClient

    # Given a youtube url, will download the first youtube result associated, using pytube
    # and add the required data to the database
    # Download File should only ever be called by a vClient if retrieveFile fails to find a matching file
    async def downloadFile(self, url):
        yt = YouTube(url)
        item = yt.streams.filter(only_audio=True).first().download()
        title = yt.title
        mp3Name = title + ".mp3"
        os.rename(title + ".mp4", mp3Name)
        await self.addFileToDB(mp3Name, url, time.time(), 1)
        return mp3Name  # I can do this because currently I just put everything in the root directory
