import discord
from discord.ext import commands
import yt_dlp
import asyncio

# Got to the FFMpeg website and download the files, place them on the root folder of this bot


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {'options' : '-vn'}
YDL_OPTIONS = {'format' : 'bestaudio', 'noplaylist' : True}

with open('auth_key.txt', 'r') as file:
    KEY = file.read()

class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []


    @commands.command()
    async def play(self, ctx, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("You're not in a voice channel!")
        if not ctx.voice_client:
            await voice_channel.connect()


        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                if 'entries' in info:
                    info = info["entries"][0]
                url = info["url"]
                title = info["title"]
                self.queue.append((url, title))
                await ctx.send(f"Added to queue: --> {title}")
        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)


    async def play_next(self, ctx):
        if self.queue:
            print("Inside self.queue")
            url, title = self.queue.pop(0)
            print("Inside pop")
            try:
                source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            except Exception as e:
                print(e)
            print("Inside source =")
            ctx.voice_client.play(source, after=lambda _:self.client.loop.create_task(self.play_next(ctx)))
            print("Inside voice_client.play")
            await ctx.send(f"Now playing -->{title}")
        elif not ctx.voice_client.is_playing():
            await ctx.send("Queue is empty!")


    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped")


    @commands.command()
    async def disconnect(self, ctx):
        await ctx.disconnect()

client = commands.Bot(command_prefix="+", intents=intents)

async def main():
    await client.add_cog(MusicBot(client))
    await client.start(KEY)


asyncio.run(main())