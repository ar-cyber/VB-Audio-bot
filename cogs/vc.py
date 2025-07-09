import discord
from discord.ext import commands, tasks
from discord.ext.commands import Cog
import json, os
import utils.config
class VCRecording(Cog):
    def __init__(self, bot):
        self.client = bot
        self.connections = {}
        self.purge_messages.start()

    @tasks.loop(minutes=5)
    async def purge_messages(self):
        await self.client.wait_until_ready()
        CHANNEL_ID = int(utils.config.config['vc']['cmdchannelid'])
        channel = self.client.get_channel(CHANNEL_ID)

        if channel is None:
            print(f"Channel with ID {CHANNEL_ID} not found.")
            return

        def not_excluded(msg: discord.Message):
            return not msg.pinned

        try:
            deleted = await channel.purge(limit=100, check=not_excluded)
            print(f"Purged {len(deleted)} messages from {channel.name}")
        except discord.Forbidden:
            print("Bot does not have permission to purge messages.")
        except discord.HTTPException as e:
            print(f"Failed to purge messages: {e}")

    @discord.slash_command(name = "record", description = "Record your voice instead of using Discord's bad stuff")
    async def record(self, ctx: discord.ApplicationContext):  # If you're using commands.Bot, this will also work.
        voice = ctx.author.voice
        if ctx.channel.id != int(utils.config.config['vc']['cmdchannelid']): return await ctx.respond(f"You must send this in <#{utils.config.config['vc']['cmdchannelid']}>!", ephemeral=True)
        if not voice:
            return await ctx.respond("You aren't in a voice channel!")
        if voice.channel.id != int(utils.config.config['vc']['channelid']):
            return await ctx.respond(f"You're not in <#{utils.config.config['vc']['channelid']}>")

        vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
        self.connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.

        vc.start_recording(
            discord.sinks.MP3Sink(),  # The sink type to use.
            self.once_done,  # What to do once done.
            ctx.channel  # The channel to disconnect from.
        )
        await ctx.respond("Started recording!")
    async def once_done(self, sink: discord.sinks, channel: discord.TextChannel, *args):  # Our voice client already passes these in.
        recorded_users = [  # A list of recorded users
            f"<@{user_id}>"
            for user_id, audio in sink.audio_data.items()
        ]
        await sink.vc.disconnect()  # Disconnect from the voice channel.
        files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
        await channel.send(f"Audio recording should be attached.\n **ALL MESSAGES IN THIS CHANNEL PURGE EVERY 5 MINUTES SO BE QUICK**", files=files)  # Send a message with the accumulated files.
    @discord.slash_command(name = "stop", description = "Stop recording.")
    async def stop_recording(self, ctx):
        if ctx.guild.id in self.connections:  # Check if the guild is in the cache.
            vc = self.connections[ctx.guild.id]
            vc.stop_recording()  # Stop recording, and call the callback (once_done).
            del self.connections[ctx.guild.id]  # Remove the guild from the cache.
            await ctx.delete()  # And delete.
        else:
            await ctx.respond("I am currently not recording here.")  # Respond with this if we aren't recording.

    

def setup(bot):
    bot.add_cog(VCRecording(bot))