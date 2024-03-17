import asyncio
from asyncio import Queue

import functools
import typing

import discord
from discord import app_commands

from pytube import YouTube

import logging

def to_thread(func: typing.Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})\n------')
    for guild in client.guilds:
        tree.copy_global_to(guild = guild)
        await tree.sync(guild = guild)

@client.event
async def on_guild_join(guild: discord.Guild):
    tree.copy_global_to(guild = guild)
    await tree.sync(guild = guild)


class DServer():
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        self.queue = Queue()
        self.tracks = []
        self.current_track: asyncio.Task = None

    async def play_queue(self):
        while True:
            self.current_track = asyncio.create_task(self.queue.get_nowait())
            while not self.current_track.done():
                await asyncio.sleep(1)
            if not self.queue.qsize():
                break

    @to_thread
    def download_song(self, song: YouTube):
        return song.streams.filter(only_audio=True, audio_codec='opus').order_by('abr').desc().first().download(filename=f'{self.guild.id}.webm')

    async def play_song(self, song: YouTube):
        try:
            stream = await self.download_song(song)
            source = discord.FFmpegPCMAudio(stream)
            self.guild.voice_client.play(source)
            asyncio.sleep(song.length)
        except asyncio.CancelledError:
            pass
        finally:
            self.tracks.pop(0)

    
    async def queue_append(self, item: YouTube):
        await self.queue.put(self.play_song(item))
    
    def track_append(self, item: str):
        self.tracks.append(item)

    async def skip(self):
        self.current_track.cancel()

        if self.queue.qsize():
            await self.play_queue()

guilds: dict[discord.Guild.id, DServer] = {}

@tree.command(description="ИГРАЕТ МУЗЫКУ")
async def play(interaction: discord.Interaction, link: str):
    if not interaction.user.voice:
        return await interaction.response.send_message(content="Ты даже не в голосовом канале!")
    
    try:
        yt = YouTube(link)
    except:
        return await interaction.response.send_message(content="Принимаю только ссылки на YOUTUBE (не уверен, что все)")
    
    if (not interaction.guild.voice_client) or (interaction.guild.voice_client.channel != interaction.user.voice.channel):
        await interaction.user.voice.channel.connect()

    if interaction.guild_id not in guilds:
        guilds[interaction.guild_id] = DServer(interaction.guild)
    
    dserver = guilds[interaction.guild_id]

    await dserver.queue_append(yt)
    dserver.track_append(yt.title)

    if len(dserver.tracks) == 1:
        await interaction.response.send_message(content=f"Сейчас играет {yt.title}")
        await dserver.play_queue()
    else:
        await interaction.response.send_message(content=f"Добавлено в очередь {yt.title}")

@tree.command(description="ПРОПУСКАЕТ ТРЕК")
async def skip(interaction: discord.Interaction):
    if interaction.guild_id not in guilds or len(guilds[interaction.guild_id].tracks) == 0:
        await interaction.response.send_message(content="Нечего скипать")
    else:
        interaction.guild.voice_client.stop()
        await interaction.response.send_message(content="Скипнуто")
        await guilds[interaction.guild_id].skip()
        

@tree.command(description="Выводит очередь")
async def q(interaction: discord.Interaction):
    if interaction.guild_id not in guilds:
        await interaction.response.send_message(content="Я ни разу в жизни не играл треки")
    elif not guilds[interaction.guild_id].tracks:
        await interaction.response.send_message(content="Пусто")
    else:
        tracks = guilds[interaction.guild_id].tracks
        message = f"Сейчас играет: {tracks[0]}"
        if tracks[1:]:
            for track in tracks[1:]:
                message += f"\nЗатем будет играть -> {track}"
        else:
            message += "\nНу и все вообщемото"
        await interaction.response.send_message(content=message)


client.run(token="TOKEN", log_handler=logging.FileHandler(filename="logs", encoding="utf-8", mode="w"))
