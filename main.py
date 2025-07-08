import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import utils.config
import aiohttp
import asyncio
client = commands.Bot(command_prefix=utils.config.config['setup']['command_prefix'], intents=discord.Intents.all())



@client.event
async def on_ready():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('_'):
            cog_name = f'cogs.{filename[:-3]}'
            try:
                await client.load_extension(cog_name)
                print(f'[SUCCESS] Loaded extension {cog_name}')
            except Exception as e:
                print(f'[ERROR] Failed to load {cog_name}: {e}')
    await client.tree.sync()
    print(f"Online as {client.user.name}")


async def is_bot_public(bot_token: str) -> bool:
    url = "https://discord.com/api/v10/oauth2/applications/@me"
    headers = {
        "Authorization": f"Bot {bot_token}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"Failed to retrieve app info: {response.status} {text}")
            
            data = await response.json()
            return data.get("bot_public", True)  # Default to True if missing

check = asyncio.run(is_bot_public(utils.config.config['setup']['token']))
if check:
    raise RuntimeError("This bot cannot be run with 'Public bot' enabled. Please disable it in your devloper portal.")
else:
    print("[INFO]: PB check passed")


client.run(utils.config.config['setup']['token'])