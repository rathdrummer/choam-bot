#!/usr/bin/env python3

import os, time
import requests
import discord

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("GUILD")

intents = discord.Intents().all()
client = discord.Client(intents=intents)

gm_channels = ["gms-only","choam-laboratory"]
bot_channel = "choam-services"
debug_channel = None

STATS = ["Industry", "Technology", "Economy", "Military", "Espionage", "Black Market", "Propaganda", "Honour", "Devotion", "Mentat", "Truthsayer", "Wpn Master"]
SKILLS = ["Industry", "Technology", "Economy", "Military", "Espionage", "Black Market", "Propaganda", "Honour", "Devotion"]
HOUSES = ["Test_House_A", "Test_House_R", "Agar", "Agnesborne", "Cidae", "Danu", "Destrym", "Feurok", "Glandriff", "Khalkes", "Lambdamus", "Sonnendrang", "Succulent", "Sykes", "Taloi", "Volkov", "Von Torridt", "Hellion"]

def signed_str(string):
    if int(string)<0:
        return str(string)
    else:
        return "+"+str(string)

def fillout(str, length):
    if len(str)>length:
        return str[:length]
    else:
        return str + ((length-len(str))*" ")

def get_user_house(user):
    for r in user.roles:
        if "House" in r.name:
            return r.name.split(" ",1)[1]
    return None

async def process_bot_command(message):
    command = message.content[1:]
    if command == "fear":
        response = "I must not fear. Fear is the mind-killer. Fear is the little-death that brings total obliteration. I will face my fear. I will permit it to pass over me and through me. And when it has gone past I will turn the inner eye to see its path. Where the fear has gone there will be nothing. Only I will remain."
        await message.channel.send(response)

    elif command[0:3] == "say":
        response = command[4:]
        await message.channel.send("**"+response+"** ;)")

    elif command == "version":
        date = os.path.getmtime(os.path.realpath(__file__))
        await message.channel.send("**CHOAM Listings bot** by Pizza \n*Last updated: "+time.ctime(date)+"*")

    ### CHARACTER SHEET DISPLAY ###
    elif command[0:5] == "sheet":
        cont=True
        house=""
        # Check channel
        if message.channel.name in gm_channels:
            # ok for any request, interpret argument
            if " " in command:
                house=command.split(" ",1)[1]
            else:
                await message.channel.send("*Please specify the House for enquiry. Example:* `!sheet Atreides`")
                cont=False
        elif "gm-chat" in message.channel.name:
            # only ok for request of appropriate person, no point interpreting argument, just get house name
            for role in message.channel.changed_roles:
                if "House" in role.name:
                    house=role.name.split(" ",1)[1]
            if house=="":
                cont=False
                roles = "`"
                for r in message.channel.changed_roles:
                    roles = roles + r.name + "` `"
                roles = roles[:-1]
                await message.channel.send("*Error: insecure channel? Roles:* "+roles)
        else:
            cont=False
            await message.channel.send("*We request that this communication take place across a more secure channel. Thank you for your understanding.*")

        if cont:
            r=requests.get("https://sheetdb.io/api/v1/sllgumbz286o7/search?house="+house+"&sheet=stats")

            if len(r.json())==0:
                await message.channel.send("*No entries found under House "+house+".*")

            else:
                data=r.json()[0]
                output = "```House "+data["house"]+"\n------------"#+fillout("Skill",13)+fillout("B",5)+fillout("Level",5)
                for stat in STATS:
                    spec = data[stat+"Spec"]
                    if spec!="":
                        spec = "["+spec+"]"
                    line = fillout(stat,13)+fillout(data[stat],3)+spec
                    output = output+"\n"+line
                    if stat=="Devotion":
                        output = output+"\n------"
                output = output+"```"
                await message.channel.send(output)

    ### SHOW TRADES ###
    elif command[0:6] == "trades":
        #house=get_user_house(message.author)
        #if False: #house==None:
        #    await message.channel.send("*This is only permitted for representatives of a noble House.*")
        #else:
        r=requests.get("https://sheetdb.io/api/v1/sllgumbz286o7?sheet=trades")
        tradesFound=False
        for data in r.json():
            if data["active"]!="FALSE" and data["house1"]!="":# and house in [data["house1"], data["house2"]]:
                tradesFound=True
                reply = "```"
                reply += fillout("House "+data["house1"],19)+"🤝  "+"House "+data["house2"]+"\n"+("-"*38)

                for stat in SKILLS:
                    stat_str_1 = stat_str_2 = ""
                    if data[stat+"1"]!="":
                        stat_str_1 = fillout(stat+": "+signed_str(data[stat+"1"]),19)+"|   "
                    if data[stat+"2"]!="":
                        stat_str_2 = stat+": "+signed_str(data[stat+"2"])
                    if stat_str_1 != "" or stat_str_2 != "":
                        reply = reply+"\n"+stat_str_1+stat_str_2
                reply += "\n\n" + data["notes"] + " (ID:"+data["id"]+")```"
                await message.channel.send(reply)

        if not tradesFound:
            await message.channel.send("*No trade records currently available.*")

    elif command[:8] == "newtrade":
            error=""

            if " " not in command:
                error = "*Please consult the attached guide for submitting trade proposals.*\n"
                error += "*Usage:* `!newtrade house1 skill1 modifier1 [...] house2 skill2 [...] notes`\n"
                error += "*Example: `!newtrade Atreides Industry +1 economy -1 Ginaz economy +1 industry -1 Atreides buying Ginaz farmers`*"
                await message.channel.send(error)
                return

            cmd = command.replace("Black Market","BlackMarket").replace("Von Torridt","VonTorridt")
            cmd_list = cmd.split(" ")[1:]
            new_cmd_list = [item.replace("BlackMarket","Black Market").replace("VonTorridt","Von Torridt") for item in cmd_list]

            first_house_selected = True
            stat_name = True
            data = {"house1":"", "house2":""}
            for s in SKILLS:
                data[s+"1"]=""
                data[s+"2"]=""
            current_stat = ""
            house2_logged_a_stat = False
            getting_notes = False
            data["notes"] = ""

            for item in new_cmd_list:
                if not getting_notes:
                    item = item.title()
                    if first_house_selected:
                        if data["house1"] == "":
                            if item not in HOUSES:
                                error = "`"+item+"` is not a House we recognise."
                                break
                            data["house1"] = item
                            continue
                        elif stat_name:
                            if item in SKILLS:
                                current_stat = item
                                stat_name=False
                                continue
                            else:
                                first_house_selected = False
                                if item not in HOUSES:
                                    error = "`"+item+"` is not a House or trade quality we recognise."
                                    break
                                data["house2"] = item
                                continue
                        elif not stat_name:
                            try:
                                int(item)
                            except ValueError:
                                error = "You want to increase `"+current_stat+"` by `"+item+"`?"
                                break
                            data[current_stat+"1"] = int(item)
                            current_stat = ""
                            stat_name=True
                            continue
                    else: #second house data now
                        if stat_name:
                            if item in SKILLS:
                                current_stat = item
                                stat_name=False
                                continue
                            elif house2_logged_a_stat:
                                getting_notes=True
                                data["notes"] += item
                                continue
                            else:
                                error = "`"+item+"` is not a trade quality we know of."
                                break
                        else:
                            try:
                                int(item)
                            except ValueError:
                                error = "You want to change "+current_stat+" by `"+item+"`?"
                                break
                            data[current_stat+"2"] = int(item)
                            house2_logged_a_stat=True
                            stat_name=True
                            current_stat = ""
                else: #getting_notes
                    data["notes"] += " "+item

            if error == "":
                if data["house2"] == "":
                    error="Who is it you are arranging this trade deal with? "
                elif data["notes"] == "":
                    error = "We are struggling to understand the details of this trade proposal, please provide some notes."
                else:
                    authorhouse=""
                    for r in message.author.roles:
                        if "House" in r.name:
                            authorhouse = r.name.split(" ",1)[1]
                        elif "GM" in r.name:
                            authorhouse = "GM"

                    if authorhouse not in [data["house1"],data["house2"],"GM"]:
                        error="You do not have permission to arrange a trade on behalf of another."


            if error != "":
                reply = "*Apologies, there was an issue with your trade proposal. "+error.replace("*","")+"*\n"
                #reply += "*Use:* `!newtrade house1 skill1 modifier1 [...] house2 skill2 [...] notes`"
                reply += "*Example use: `!newtrade Atreides Industry +1 economy -1 Ginaz economy +1 industry -1 Atreides buying Ginaz farmers`*"
            else:
                reply = "*Your trade proposal has been logged:* \n```"
                reply += fillout("House "+data["house1"],19)+"🤝  "+"House "+data["house2"]+"\n"+("-"*38)
                for stat in SKILLS:
                    stat_str_1 = stat_str_2 = ""
                    if data[stat+"1"]!="":
                        stat_str_1 = fillout(stat+": "+signed_str(data[stat+"1"]),19)
                    if data[stat+"2"]!="":
                        stat_str_2 = stat+": "+signed_str(data[stat+"2"])
                    if stat_str_1 != "" or stat_str_2 != "":
                        reply = reply+"\n"+fillout(stat_str_1,19)+"|   "+stat_str_2
                reply += "\n\nNotes: "+data["notes"]+"```"
                reply += "*Please await CHOAM approval for this trade to be enacted. Thank you for your patronage.* \n<@&908129170029154406>"

                url = "https://sheetdb.io/api/v1/sllgumbz286o7?sheet=trades"
                data["id"]="INCREMENT"
                data["approved"] = "FALSE"
                data["active"] = "FALSE"
                data["expiry"] = ""
                d = data
                x=requests.post(url, data=d)

            await message.channel.send(reply)


    elif command == "stilgar":
        await message.channel.send("https://youtu.be/l_kvakUCIYc")

    elif command == "danu":
        await message.channel.send("https://youtu.be/NCBQSkWk8KY")

    elif command == "help":
        reply = "***At your service, my lord. Here are some of the services the Combine Honnete Ober Advancer Mercantiles can provide:***\n"
        reply += "`!sheet` - *View the abilities of your House (over a secure channel, of course).*\n"
        reply += "`!trades` - *Request all ongoing trade listings available for viewing.*\n"
        reply += "`!fear` - *Lest you require reassurance.*\n"
        await message.channel.send(reply)

    else:
        await message.channel.send("*Request* `"+command+"` *not understood. Our sincerest apologies.*")


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name = GUILD)
    print('Connected to',guild.name,'as',client.user)
    #for m in guild.members:
    #    print("- "+m.name)

    # Print successful startup message
    debug_channel = discord.utils.get(guild.channels, name="choam-laboratory")
    #await debug_channel.send("**CHOAM listings available for consultation.**")


@client.event
async def on_message(message):
    if message.content[0] == "!":
        print(message.content)
        await process_bot_command(message)

client.run(TOKEN)
