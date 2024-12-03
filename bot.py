import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="h!", intents=intents)
queue = []  # Fila de músicas

# Caminho para o FFmpeg
ffmpeg_path = r"D:\Arquivos\Projetos\DJ TANJIRO\ffmpeg\bin\ffmpeg.exe"  # Atualize o caminho conforme necessário

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

async def play_next(ctx, voice_client):
    if queue:
        url = queue.pop(0)
        with yt_dlp.YoutubeDL({'format': 'bestaudio'}) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
        voice_client.play(
            FFmpegPCMAudio(audio_url, executable=ffmpeg_path, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"),
            after=lambda e: bot.loop.create_task(play_next(ctx, voice_client))
        )
        await ctx.send(f"Tocando agora: {info['title']}")
    else:
        await ctx.send("Fila vazia otário.")
        await voice_client.disconnect()

@bot.command(name="play")
async def play(ctx, url: str):
    if not ctx.author.voice:
        await ctx.send("Entra em um canal ae.")
        return

    channel = ctx.author.voice.channel
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if not voice_client:
        voice_client = await channel.connect()

    if voice_client.is_playing():
        queue.append(url)
        await ctx.send("Adicionado à fila!")
    else:
        queue.append(url)
        await play_next(ctx, voice_client)

@bot.command(name="stop")
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        queue.clear()
        await ctx.send("Parando a reprodução e limpando a fila.")
        await voice_client.disconnect()
    else:
        await ctx.send("Não há nada tocando no momento.")

@bot.command(name="skip")
async def skip(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Pulando para a próxima música!")
        await play_next(ctx, voice_client)
    else:
        await ctx.send("Não há nada tocando para pular.")

bot.run("MEU_TOKEN")