from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.ext.commands.bot import Bot
from nextcord.member import Member
from pymongo.database import Database


class ModerationCommands(commands.Cog, name="Moderation"):
    """The description for ModerationCommands goes here."""

    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db

    @commands.command(name="mute", aliases=["m"], brief="Mute a user", description="Mute a user", usage="mute <user> <reason>")
    @commands.has_guild_permissions(manage_messages=True)
    async def mute(self, ctx, user: Member, *, reason: str):
        """Mute a user"""
        await ctx.message.delete()
        await ctx.send(f"{user.mention} has been muted for {reason}")

    @commands.command(name="unmute", aliases=["um"], brief="Unmute a user", description="Unmute a user", usage="unmute <user>")
    @commands.has_guild_permissions(manage_messages=True)
    async def unmute(self, ctx, user: Member):
        """Unmute a user"""
        await ctx.message.delete()
        await ctx.send(f"{user.mention} has been unmuted")

    @commands.command(name="ban", aliases=["b"], brief="Ban a user", description="Ban a user", usage="ban <user> <reason>")
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, user: Member, *, reason: str):
        """Ban a user"""
        await user.ban(reason=reason, delete_message_days=0)
        await ctx.message.delete()
        await ctx.send(f"{user.mention} has been banned for {reason}")

    @commands.command(name="unban", aliases=["ub"], brief="Unban a user", description="Unban a user", usage="unban <user>")
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, *, user: Member):
        """Unban a user"""
        await user.unban()
        await ctx.message.delete()
        await ctx.send(f"{user.mention} has been unbanned")

    @commands.command(name="kick", aliases=["k"], brief="Kick a user", description="Kick a user", usage="kick <user> <reason>")
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, user: Member, *, reason: str):
        """Kick a user"""
        await user.kick(reason=reason)
        await ctx.message.delete()
        await ctx.send(f"{user.mention} has been kicked for {reason}")
        
    @commands.command(name="purge", aliases=["cc"], brief="Purge messages", description="Purge messages", usage="purge <amount>")
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        """Purge messages"""
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"{amount} messages have been deleted by {ctx.author.mention}!", delete_after=5)
        
def setup(bot):
    bot.add_cog(ModerationCommands(bot, bot.db))
