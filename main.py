import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from pytube import YouTube
from collections import deque

queue = deque()



MY_GUILD = discord.Object(id = 0)
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

def play_song(voice_client, error = None, new = True):
    print(f'ERROR: {error}') if error else None
    queue.popleft() if not new else None
    if queue:
        url = queue[0]
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True, audio_codec='opus').order_by('abr').desc().first().download(filename='music.webm')
        source = discord.FFmpegOpusAudio(stream)
        voice_client.play(source, after=lambda e: play_song(voice_client, error = e, new = False))

@client.tree.command(description = 'ПРОПУСКАЕТ ИГРАЮЩИЙ ТРЕК')
async def skip(interaction: discord.Interaction):
    try:
        queue.popleft()
    except:
        return await interaction.response.send_message(content = 'НЕЧЕГО СКИПАТЬ')
    interaction.guild.voice_client.stop()
    await interaction.response.send_message(content = 'СКИПНУТО')
    play_song(interaction.guild.voice_client)
    
            
@client.tree.command(description = 'ИГРАЕТ МУЗЫКУ')
async def play(interaction: discord.Interaction, link: str):
    if interaction.user.voice:
        if interaction.guild.voice_client:
            voice_client = interaction.guild.voice_client
        else:
            voice_client = await interaction.user.voice.channel.connect()
    else:
        return await interaction.response.send_message(content = 'ТЫ НЕ В ГОЛОСОВОМ КАНАЛЕ')
    yt = YouTube(link)
    queue.append(link)
    if len(queue) == 1:
        await interaction.response.send_message(content = f'ИГРАЕТ {yt.title}')
        play_song(voice_client)
    else:
        await interaction.response.send_message(content = f'ДОБАВЛЕНО В ОЧЕРЕДЬ {yt.title}')
    
    

@client.tree.command(description = 'ВЫВОДИТ ОЧЕРЕДЬ')
async def q(interaction: discord.Interaction):
    await interaction.response.send_message(content = f'ОЧЕРЕДЬ: {queue}')

client.run('TOKEN')
