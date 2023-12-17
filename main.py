import asyncio
import discord
from discord.ext import commands
from pytube import YouTube
from collections import deque

queue = deque()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})\n------')
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def play_next_track(self, ctx, delay, query):
        await asyncio.sleep(delay)
        await skip(self, ctx) if (query == queue[0]) else None

    @commands.command()
    async def play(self, ctx, query, next_track=False):
        if not next_track:
            await ctx.send(f'ДОБАВЛЕНО В ОЧЕРЕДЬ {YouTube(query).title}') if queue else None
            queue.append(query)

        if not ctx.voice_client.is_playing() and queue:
            yt = YouTube(queue[0])
            stream = yt.streams.filter(only_audio=True, audio_codec='opus').order_by('abr').desc().first().download(filename='music.webm')
            source = discord.FFmpegOpusAudio(stream)
            ctx.voice_client.play(source, after=lambda e: print(f'ERROR: {e}') if e else None)
            await ctx.send(f'ИГРАЕТ {yt.title}')
            await play_next_track(self, ctx, yt.length, query)
            

    @commands.command()
    async def skip(self, ctx):
        if queue:
            queue.popleft()
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
            if queue:
                await play(self, ctx, queue[0], next_track=True)

    @commands.command()
    async def q(self, ctx):
         await ctx.send(f'ОЧЕРЕДЬ {list(queue)}')

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("ТЫ НЕ В ГОЛОСОВОМ КАНАЛЕ")
        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.start('TOKEN')
        

asyncio.run(main())
