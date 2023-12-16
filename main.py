import asyncio
import discord
from discord.ext import commands
from collections import deque
import cv2
import youtube_dl

queue = deque()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})\n------')

async def play_next_track(ctx, delay):
    await asyncio.sleep(delay)
    await skip(ctx)

@bot.command()
async def play(ctx, query, next_track=False):
    if not next_track:
        queue.append(query)

    if not ctx.voice_client.is_playing() and queue:
        url = queue[0]
        ydl_opts = {'format': 'best'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_url = info_dict.get("url", None)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get('title', None)

        # start the video
        cap = cv2.VideoCapture(video_url)
        while (True):
            ret,frame = cap.read()
            cv2.imshow('frame',frame)
            if cv2.waitKey(20) & 0xFF == ord('q'):
                break    

        cap.release()
        cv2.destroyAllWindows()

        await play_next_track(ctx, info_dict['duration'])
        await ctx.send(f'ИГРАЕТ {video_title}')

@bot.command()
async def skip(ctx):
    if queue:
        queue.popleft()
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        if queue:
            await play(ctx, queue[0], next_track=True)

@bot.command()
async def q(ctx):
     await ctx.send(f'ОЧЕРЕДЬ {list(queue)}')

@play.before_invoke
async def ensure_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("ТЫ НЕ В ГОЛОСОВОМ КАНАЛЕ")
    else:
        await ctx.voice_client.move_to(ctx.author.voice.channel)

async def main():
    async with bot:
        await bot.start('TOKEN')

asyncio.run(main())
