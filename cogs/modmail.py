import discord
from discord.ext import commands
from discord.ext.commands import Cog

from utils.config import config
import json
import random
class Modmail(Cog):
    def __init__(self, bot):
        self.client = bot


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user or message.author.bot:
            return
        if str(message.channel.type) == "private":
            data = json.load(open('cogs/modmemory.json', 'r'))
            for item in data['sessions']:
                if message.author.id == item['user']:
                    channel = discord.utils.get(self.client.get_all_channels(), name=item['text_channel'])
                    await channel.send(f"**{str(message.author)} | {str(message.author.id)}:** " + message.content)
                    return
                else:
                    pass
            # Deny everyone from seeing the channel
            guild = self.client.get_guild(int(config['setup']['guild']))
            print(guild.roles)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                message.author: discord.PermissionOverwrite(view_channel=True),
                
            }
            print(config['modmail']['allowed_roles'].split(':'))
            for ROLE_ID in config['modmail']['allowed_roles'].split(':'):
                overwrites[guild.get_role(int(ROLE_ID))] = discord.PermissionOverwrite(view_channel=True)
            print(overwrites)
            id = random.randint(0,10000)
            modmail_channel = await guild.create_text_channel(f"mod-{message.author.id}-{id}", overwrites=overwrites)
            await modmail_channel.send(f"@here\n {message.author} needs assistance. Please respond to them.")
            jsondata = {
                "user": message.author.id,
                "text_channel": f"mod-{message.author.id}-{id}",
                "claimedby": ""
            }
            data['sessions'].append(jsondata)
            with open('cogs/modmemory.json', 'w') as fp:
                print(data)
                json.dump(data, fp)

        # Optiona
            await message.author.send("Welcome to the modmail! A representative will be with you shortly")
        else:
            channel = message.channel
            print(channel.name)
            data = json.load(open('cogs/modmemory.json', 'r'))
            for item in data['sessions']:
                print(item['text_channel'])
                if channel.name == item['text_channel']:
                    print("Found match!")
                    user = await self.client.fetch_user(item['user'])
                    await user.send(f"**{str(message.author)} | {str(message.author.id)}:** " + message.content)
                else:
                    pass



    @commands.slash_command(name = "ping", description="Pong! Check the latency of the bot.")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(f'PONG!\nLatency: {round(self.client.latency * 1000)}ms', ephemeral=True)
    
    
    @commands.slash_command(name = "claim", description = "Claim this modmail message")
    @commands.has_permissions(moderate_members=True)
    @commands.guild_only()
    async def _reply(self, ctx: discord.ApplicationContext):
        data = json.load(open('cogs/modmemory.json', 'r'))
        for item in data['sessions']:
            if ctx.channel.name == item['text_channel']:
                if item['claimedby'] == ctx.user.id:
                    return await ctx.respond("You've already claimed this ticket!", ephemeral=True)
                if item['claimedby'] != "":
                    return await ctx.respond("Someone's already claimed this ticket!", ephemeral=True)
                user = await self.client.fetch_user(item['user'])
                await user.send(f"# **{str(ctx.user)} | {str(ctx.user.id)}** has claimed this ticket")
                await ctx.channel.send(f"# **{str(ctx.user)} | {str(ctx.user.id)}** has claimed this ticket")
                data['sessions'][data['sessions'].index(item)]['claimedby'] == ctx.user.id
                with open('cogs/modmemory.json', 'w') as fp:
                    json.dump(data, fp)
                return await ctx.respond("Sucessfully claimed the ticket!", ephemeral=True)
            else:
                pass
        await ctx.respond("You're not in a modmail channel!", ephemeral=True)

    @commands.slash_command(name = "close", description="Close this ticket.")
    @commands.has_permissions(moderate_members=True)
    @commands.guild_only()
    async def _close(self, ctx: discord.ApplicationContext):
        data = json.load(open('cogs/modmemory.json', 'r'))
        for item in data['sessions']:
            if ctx.channel.name == item['text_channel']:

                user = await self.client.fetch_user(item['user'])
                await user.send(f"# **{str(ctx.user)} | {str(ctx.user.id)}** has closed this ticket.")
                await ctx.channel.send(f"# **{str(ctx.user)} | {str(ctx.user.id)}** has closed this ticket.")
                print(data['sessions'].index(item))
                data['sessions'].remove(item)
                with open('cogs/modmemory.json', 'w') as fp:
                    json.dump(data, fp)
                return await ctx.respond("Sucessfully closed the modmail!", ephemeral=True)
            else:
                pass
        await ctx.respond("You're not in a modmail channel!", ephemeral=True)
    @commands.slash_command(name = "delete", description = "Delete a modmail ticket. IRREVESIBLE!")
    @commands.has_permissions(moderate_members = True)
    @commands.guild_only()
    @app_commands.describe(sure = "Write `I'm sure` if you really want to.")
    async def _del(self, ctx: discord.ApplicationContext, sure: str):
        if sure != "I'm sure":
            return await ctx.respond("`I'm sure` was not written in the sure argument.")
        data = json.load(open('cogs/modmemory.json', 'r'))
        for item in data['sessions']:
            if ctx.channel.name == item['text_channel']:
                return await ctx.respond("This modmail hasn't been closed (hint run `/close` before this)!", ephemeral=True)
            else:
                pass
        if "mod-" in ctx.channel.name:
            await ctx.channel.delete()
            return await ctx.respond("Success!", ephemeral=True)
        else:
            return await ctx.respond("You're not in a ticket channel!", ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(Modmail(bot))
