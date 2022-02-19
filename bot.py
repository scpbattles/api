import string
import random
import json
import time

import discord
from discord.ext import commands

id_characters = string.ascii_letters + string.ascii_uppercase

bot = commands.Bot(command_prefix = "!")

@bot.event
async def on_ready():
    print("Ready")

@bot.command()
async def server(ctx, suffix, *args):

    if suffix == "create":

        server_id = args[0]

        auth_id = ""

        for i in range(31):
            auth_id += random.choice(id_characters)

        with open("server_auths.json","r") as file:
            server_auths = json.load(file)

        server_auths[server_id] = auth_id

        with open("server_auths.json", "w") as file:
            json.dump(server_auths,file, indent = 4)

        await ctx.author.send(f"Created new server {server_id}.\n\nYour server's private API auth ID: ```{auth_id}```\n**Do not share this!**\n\n You can use **!regenerate** to renew your ID.")

@bot.command()
async def regenerate(ctx, server_id):

    auth_id = ""

    for i in range(31):
        auth_id += random.choice(id_characters)

    with open("server_auths.json","r") as file:
        server_auths = json.load(file)

    server_auths[server_id] = auth_id

    with open("server_auths.json", "w") as file:
        json.dump(server_auths,file, indent = 4)


    await ctx.author.send(f"Created new server {server_id}.\n\nYour server's private API auth ID: ```{auth_id}```\n**Do not share this!**\n\n You can use **!regenerate** to renew your ID.")

bot.run("OTQzMDM0ODM2NTY4OTAzNzMw.YgtLoQ.xqnnlLgfDaoHUP3eLfwbK1Ae4hw")
