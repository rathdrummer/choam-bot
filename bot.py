import os, time
import discord

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("GUILD")

intents = discord.Intents().all()
client = discord.Client(intents=intents)

test_channel = None


async def process_bot_command(message):
    command = message.content[1:]
    if command == "fear":
        response = "I must not fear. Fear is the mind-killer. Fear is the little-death that brings total obliteration. I will face my fear. I will permit it to pass over me and through me. And when it has gone past I will turn the inner eye to see its path. Where the fear has gone there will be nothing. Only I will remain."
        await message.channel.send(response)

    elif command[0:3] == "say":
        response = command[4:]
        await message.channel.send("**"+response+"**")

    elif command == "version":
        date = os.path.getmtime("/home/adam/choam-bot/bot.py")
        await message.channel.send("**CHOAM Listings bot** by Pizza \n*Last updated: "+time.ctime(date)+"*")

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name = GUILD)
    print('Connected to',guild.name,'as',client.user)
    # Print successful startup message
    test_channel = discord.utils.get(guild.channels, name="choam-laboratory")
    await test_channel.send("**CHOAM listings available for consultation.**")


@client.event
async def on_message(message):
    if message.content[0] == "!":
        print(message.content)
        await process_bot_command(message)

client.run(TOKEN)
