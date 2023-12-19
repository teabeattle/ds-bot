import discord
from discord import app_commands
import wavelink

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    node = [wavelink.Node(uri = 'http://localhost:2333',
                     password = "youshallnotpass",
                     )]
    await wavelink.Pool.connect(nodes = node, client=client)
    print(f'Logged in as {client.user} (ID: {client.user.id})\n------')
    for guild in client.guilds:
        tree.copy_global_to(guild = guild)
        await tree.sync(guild = guild)
        
@client.event
async def on_guild_join(guild):
    tree.copy_global_to(guild = guild)
    await tree.sync(guild = guild)

@tree.command(description = 'ПРОПУСКАЕТ ИГРАЮЩИЙ ТРЕК')
async def skip(interaction: discord.Interaction):
    if not interaction.guild.voice_client:
        return await interaction.response.send_message(content='Я ДАЖЕ НЕ В В ГОЛОСОВОМ КАНАЛЕ')
    return await interaction.response.send_message(content=f'СКИПНУТО {await interaction.guild.voice_client.skip()}')
    
            
@tree.command(description = 'ИГРАЕТ МУЗЫКУ')
async def play(interaction: discord.Interaction, link: str):
    if interaction.user.voice:
        if not interaction.guild.voice_client:
            player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
        else:
            player = interaction.guild.voice_client
            player.autoplay = wavelink.AutoPlayMode.partial
            player.QueueMode = wavelink.QueueMode.normal
    else:
        return await interaction.response.send_message(content = 'ТЫ НЕ В ГОЛОСОВОМ КАНАЛЕ')

    tracks: wavelink.Search = await wavelink.Playable.search(link)
    if not tracks:
        return await interaction.response.send_message(content = 'НИЧЕГО НЕ НАЙДЕНО')
    
    if isinstance(tracks, wavelink.Playlist):
        added : int = await player.queue.put_wait(tracks)
        await interaction.response.send_message(content = f'В ОЧЕРЕДЬ ДОБАВЛЕН ПЛЕЙЛИСТ {tracks.name} СОСТОЯЩИЙ ИЗ {added} ТРЕКОВ')
    else:
        track : wavelink.Playable = tracks[0]
        await player.queue.put_wait(track)
        await interaction.response.send_message(content = f"ДОБАВЛЕНО В ОЧЕРЕДЬ '{track}' ДЛИТЕЛЬНОСТЬЮ '{int(track.length/1000//60)}:{str(int(track.length/1000%60)).zfill(2)}'")

    if not player.playing:
        await player.play(player.queue.get())

@tree.command(description = 'ВЫВОДИТ ОЧЕРЕДЬ')
async def q(interaction: discord.Interaction):
    player = interaction.guild.voice_client
    if not player:
        return await interaction.response.send_message(content='Я ДАЖЕ НЕ В В ГОЛОСОВОМ КАНАЛЕ')
    if not player.playing:
        return await interaction.response.send_message(content='ПУСТО')
    if player.queue:
        return await interaction.response.send_message(f"СЕЙЧАС ИГРАЕТ: '{str(player.current)}' ДО КОНЦА ОСТАЛОСЬ '{int((player.current.length-player.position)/1000//60)}:{str(int((player.current.length-player.position)/1000%60)).zfill(2)}' \n'{str(interaction.guild.voice_client.queue)}'")
    return await interaction.response.send_message(f"СЕЙЧАС ИГРАЕТ: '{str(player.current)}' ДО КОНЦА ОСТАЛОСЬ '{int((player.current.length-player.position)/1000//60)}:{str(int((player.current.length-player.position)/1000%60)).zfill(2)}'")

client.run('TOKEN')
