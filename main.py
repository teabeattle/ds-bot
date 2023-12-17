import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from pytube import YouTube
from collections import deque

queue = deque()

MY_GUILD = discord.Object(id = 1002264111574421614)
class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.all()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})\n------')

@client.tree.command(description = 'ИГРАЕТ МУЗЫКУ')
async def play(interaction: discord.Interaction, link: str):
    if interaction.user.voice:
        voice_client = await interaction.user.voice.channel.connect()
    else:
        return await interaction.response.send_message(content = 'ТЫ НЕ В ГОЛОСОВОМ КАНАЛЕ')

    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True, audio_codec='opus').order_by('abr').desc().first().download(filename='music.webm')
    source = discord.FFmpegOpusAudio(stream)

    voice_client.play(source, after=lambda e: print(f'ERROR: {e}') if e else None)

    await interaction.response.send_message(content = f'ИГРАЕТ {yt.title}')

client.run('TOKEN')
