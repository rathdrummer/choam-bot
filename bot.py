import os, time
import requests
import discord

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("GUILD")

intents = discord.Intents().all()
client = discord.Client(intents=intents)

debug_channel = "choam-laboratory"
STATS = ["Industry", "Technology", "Economy", "Military", "Espionage", "Black Market", "Propaganda", "Honour", "Devotion", "Mentat", "Truthsayer", "Wpn Master"]



async def process_bot_command(message):
    command = message.content[1:]
    if command == "fear":
        response = "I must not fear. Fear is the mind-killer. Fear is the little-death that brings total obliteration. I will face my fear. I will permit it to pass over me and through me. And when it has gone past I will turn the inner eye to see its path. Where the fear has gone there will be nothing. Only I will remain."
        await message.channel.send(response)

    elif command[0:3] == "say":
        response = command[4:]
        await message.channel.send("**"+response+"** ;)")

    elif command == "version":
        date = os.path.getmtime("/home/adam/choam-bot/bot.py")
        await message.channel.send("**CHOAM Listings bot** by Pizza \n*Last updated: "+time.ctime(date)+"*")

    elif command == "apicheck":
        r=requests.get("https://sheetdb.io/api/v1/433vdzbr7zmrl/cells/A1")
        await message.channel.send(r.json()['A1'])

    elif command[0:5] == "sheet":
        cont=True


        if " " in command: #unique GM request
            house = command.split(" ", 1)[1]
            r=requests.get("https://sheetdb.io/api/v1/433vdzbr7zmrl/search?house="+house+"&sheet=HouseStats")
            if len(r.json())==0:
                await message.channel.send("No entries found under House "+house+".")
                cont=False
            data=r.json()[0]
            if not ("gm-chat" in message.channel.name and data["house"].lower() in message.channel.category.name.lower()) or message.channel.name == debug_channel:
                await message.channel.send("*We request that this communication take place across a more secure channel. Thank you for your understanding.*")
                cont=False


        else: #personal channel request
            r=requests.get("https://sheetdb.io/api/v1/433vdzbr7zmrl/search?user="+message.author.name+"&sheet=HouseStats")

            if len(r.json())==0:
                await message.channel.send("*No entries found for user "+message.author.name+".*")
                cont=False
            data=r.json()[0]
            print(data["house"])
            print(message.channel.category.name)
            if not ("gm-chat" in message.channel.name and data["house"].lower() in message.channel.category.name.lower()):
                await message.channel.send("*We request that this communication take place across a more secure channel. Thank you for your understanding.*")
                cont=False


        if cont:
            output = "**House "+data["house"]+"**\n--------"
            for stat in STATS:
                output = output+"\n*"+stat+":* **"+data[stat]+"**"
                if stat=="Devotion":
                    output = output+"\n--------"
            await message.channel.send(output)

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name = GUILD)
    print('Connected to',guild.name,'as',client.user)
    # Print successful startup message
    #debug_channel = discord.utils.get(guild.channels, name="choam-laboratory")
    await debug_channel.send("**CHOAM listings available for consultation.**")


@client.event
async def on_message(message):
    if message.content[0] == "!":
        print(message.content)
        await process_bot_command(message)

client.run(TOKEN)
