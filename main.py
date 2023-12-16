import pytube

import os

import asyncio
import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def play(ctx, query):
        
    yt = pytube.YouTube(query)
    print(yt.title)
    stream = yt.streams.filter(only_audio=True, audio_codec='opus').order_by('abr').desc().first().url
    print(stream)
    
    source = await discord.FFmpegOpusAudio(stream)
    ctx.voice_client.play(source, after=lambda e: print(f'ERROR: {e}') if e else None)
        
    await ctx.send(f'ИГРАЕТ {yt.title}')

@play.before_invoke
async def ensure_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("ТЫ НЕ В ГОЛОСОВОМ КАНАЛЕ")
    else:
        await ctx.voice_client.move_to(ctx.author.voice.channel)
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

async def main():
    async with bot:
        await bot.start(os.environ.get('TOKEN'))

asyncio.run(main())
