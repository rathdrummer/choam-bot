import os
import discord

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("GUILD")

intents = discord.Intents().all()
client = discord.Client(intents=intents)

print(GUILD)

@client.event
async def on_ready():
    print('Connected to Discord as',client.user)
    print(client.guilds[0].name)
    guild = discord.utils.get(client.guilds, name = GUILD)
    print("Guild:",guild.name)

@client.event
async def on_message(message):
    if message.content == "!fear":
        response = "I must not fear. Fear is the mind-killer. Fear is the little-death that brings total obliteration. I will face my fear. I will permit it to pass over me and through me. And when it has gone past I will turn the inner eye to see its path. Where the fear has gone there will be nothing. Only I will remain."
        await message.channel.send(response)


client.run(TOKEN)
