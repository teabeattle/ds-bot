import pytube

from collections import deque

import asyncio
import discord
from discord.ext import commands

queue = []

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

async def play_next_track(ctx, delay):
    await asyncio.sleep(delay)
    await skip(ctx)
   
@bot.command()
async def play(ctx, query, next_track = False):
    queue.append(query) if not next_track else None
    if ctx.voice_client.is_playing():
        print(queue)
        return
        
    yt = pytube.YouTube(queue[0])
    print(yt.title)
    stream = yt.streams.filter(only_audio=True, audio_codec='opus').order_by('abr').desc().first().download(filename='music.webm')
    print(stream)
    
    source = discord.FFmpegOpusAudio(stream)
    ctx.voice_client.play(source, after=lambda e: print(f'ERROR: {e}') if e else None)
    await play_next_track(ctx, yt.length)
        
    await ctx.send(f'ИГРАЕТ {yt.title}')

@bot.command()
async def skip(ctx):
    queue.pop(0)
    print(len(queue))
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    if len(queue):
        await play(ctx, queue[0], next_track = True)

@bot.command()
async def q(ctx):
     await ctx.send(f'ОЧЕРЕДЬ {queue}')

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
