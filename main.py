import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from pytube import YouTube
from collections import deque

queue = {}

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})\n------')
    for guild in client.guilds:
        queue[guild.id] = deque()
        tree.copy_global_to(guild = guild)
        await tree.sync(guild = guild)
        
@client.event
async def on_guild_join(guild):
    queue[guild.id] = deque()
    tree.copy_global_to(guild = guild)
    await tree.sync(guild = guild)



def play_song(guild, error = None, new = True):
    print(f'ERROR: {error}') if error else None
    try:
        queue[guild.id].popleft() if not new else None
    except IndexError:
        pass
    if queue[guild.id]:
        url = queue[guild.id][0]
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True, audio_codec='opus').order_by('abr').desc().first().download(filename=f'{guild.id}.webm')
        source = discord.FFmpegOpusAudio(stream)
        guild.voice_client.play(source, after=lambda e: play_song(guild, error = e, new = False))

@tree.command(description = 'ПРОПУСКАЕТ ИГРАЮЩИЙ ТРЕК')
async def skip(interaction: discord.Interaction):
    if not queue[interaction.guild.id]:
        return await interaction.response.send_message(content = 'НЕЧЕГО СКИПАТЬ')
    interaction.guild.voice_client.stop()
    await interaction.response.send_message(content = 'СКИПНУТО')
    play_song(interaction.guild, new = False)
    
            
@tree.command(description = 'ИГРАЕТ МУЗЫКУ')
async def play(interaction: discord.Interaction, link: str):
    if interaction.user.voice:
        if not interaction.guild.voice_client:
            await interaction.user.voice.channel.connect()
    else:
        return await interaction.response.send_message(content = 'ТЫ НЕ В ГОЛОСОВОМ КАНАЛЕ')    
    yt = YouTube(link)
    queue[interaction.guild.id].append(link)
    if len(queue[interaction.guild.id]) == 1:
        await interaction.response.send_message(content = f'ИГРАЕТ {yt.title}')
        play_song(interaction.guild)
    else:
        await interaction.response.send_message(content = f'ДОБАВЛЕНО В ОЧЕРЕДЬ {yt.title}')
    
    

@tree.command(description = 'ВЫВОДИТ ОЧЕРЕДЬ')
async def q(interaction: discord.Interaction):
    await interaction.response.send_message(content = f'ОЧЕРЕДЬ: {queue[interaction.guild.id]}')

client.run('TOKEN')
