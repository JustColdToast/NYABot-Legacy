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
  has currently been removed
* Join and Leave Voice Channels through text commands in any channel the bot has access to
  * Can recognize a force disconnect, and take care of any necessary cleanup automatically
* Play music from youtube url's (This feature is being worked on, and is not stable)
  * Queue up songs to be played from youtube URL's
  * Automatically leave if queue is empty
<h2>Roadmap</h2>
Currently NYABot is very rudimentry, but the basic functions required to build more complex ones on are, for the most part, complete.
The current objective is to work towards finishing the following:
1. Reimplementing the youtube audio streaming method to download files instead of directly streaming them, providing a more stable experience
2. Implement a file manager that monitors the usage of specific audio files and deletes old and unused files to free space
3. Finish the implementation of a response system that can respond to specific provided keywords with a provided image (this one is just for fun, and due to it's abusability for spam, should not be used
in any publically available bots)

## License
Distributed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)
