import discord
from discord.ext import commands, tasks
from discord.ext.commands import Cog
from discord import app_commands
import utils.config
class GitHub_SEQTA(Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        for forum in utils.config.config['forums']['forumids'].split(','): 
            if thread.parent.type == discord.ChannelType.forum and thread.parent.id == int(forum): 
                print(f"New forum post detected: {thread.name}")
                body = f"""# Welcome <@{thread.owner_id}> to the VB-Audio bug reports forum. A helper will be with you soon. 
## Just a couple things
1. Please make sure that you've described your issue clearly so we can help you quicker.
2. Please attach a photo of Voicemeeter/Matrix and the System Sound dialog (Windows + R; type in mmsys.cpl; press enter)
3. Please **be patient**. Helpers are volunteers, not paid people.

If you've done all of these, good job! We'll be with you soon!

"""         
                thread.send(body)
            

async def setup(bot):
    await bot.add_cog(GitHub_SEQTA(bot))