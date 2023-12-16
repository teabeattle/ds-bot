import asyncio
import discord
from discord.ext import commands
from pytube import YouTube
from collections import deque
import cv2
import pafy

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
        video = pafy.new(url)
        best = video.getbest(preftype="webm")

        # start the video
        cap = cv2.VideoCapture(best.url)
        while (True):
            ret,frame = cap.read()
            cv2.imshow('frame',frame)
            if cv2.waitKey(20) & 0xFF == ord('q'):
                break    

        cap.release()
        cv2.destroyAllWindows()

        await play_next_track(ctx, video.length)
        await ctx.send(f'ИГРАЕТ {video.title}')

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
