# NYABot
A simple and versatile discord bot, written in python, using [Discord.py](https://github.com/Rapptz/discord.py) and [YTDL](https://github.com/ytdl-org/youtube-dl).
NYABot is an long-term project of mine, designed for my personal discord. However, it's design does not prevent the bot from working across
multiple servers.
<br/>

## About NYABot
NYABot has a variety of features, with more being added over time. As of now, the bot can:
* Recognize and respond to commands intended for it, via it's prefix (>>)
  * This can be further expanded on easily to add functionaly for more text-based interactions with the bot
  * Alternativly, the bot can be configured to respond to specific phrases not using it's command prefix (>>), however this functionality
    has currently been removed because I have no real use for it
* Join and Leave Voice Channels through text commands in any channel the bot has access to
  * Can recognize a force disconnect, and take care of any necessary cleanup automatically
* Play music from youtube url's (This feature is being worked on, and is not stable)
  * Queue up songs to be played from youtube URL's
  * Automatically leave if queue is empty

A variety of features have been removed from the public version, and do note that the rewrite branch has some features missing.

## About Rewrite (available in rewrite branch)
The Rewrite of NYABot was focused on restructuring the way that the bot handles text commands, and manages audio playback.
To reliably play audio from youtube in Discord calls I wanted to download them off of youtube, and then play the file directly, as opposed to the original streaming method from YTDL.
It also gave me the opportunity to experiment with SQL databases through SQLite, as I needed a way to reliably store and access information about what files have been downloaded, from which youtube links, and when they were last accessed.
Currently, the File Manager is mostly complete as it reliably downloads files from youtube, and records/accesses information about them.
I plan to further expand on it by using the last access time of a file, as well the number of voice clients accessing the file, to determine which files can safely be deleted to save on space.


## Roadmap
Currently NYABot is very rudimentry, but the basic functions required to build more complex ones on are, for the most part, complete.
The current objective is to work towards finishing the following:
1. Finish implementing a file manager that monitors the usage of specific audio files and deletes old and unused files to free space
2. Finish the implementation of a response system that can respond to specific provided keywords with a provided image (this one is just for fun, and due to it's abusability for spam, should not be used in any publically available bots)

## Usage
Remember to swap out my bot token for your discord bot token and then the bot should go online when running __main__.py

## License
Distributed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)
