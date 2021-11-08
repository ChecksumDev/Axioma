from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.ext.commands.bot import Bot
from nextcord.ext.commands.context import Context
from nextcord.member import Member
from pymongo.database import Database
from datetime import datetime as dt
import random
import string


class ModerationCommands(commands.Cog, name="Moderation"):
    """The description for ModerationCommands goes here."""

    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
<<<<<<< Updated upstream
        self.db = db
=======
        self.db = db.axi

    def _random_string():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
        
    @commands.command(name="purge", aliases=["cc"], brief="Purge messages", description="Purge messages", usage="purge <amount>")
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        """Purge messages"""
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"{amount} messages have been deleted by {ctx.author.mention}!", delete_after=5)
        
=======

    @commands.command(name="purge", aliases=["p"], brief="Purge messages", description="Purge messages", usage="purge <amount>")
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx: Context, amount: int):
        """Purge messages"""
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        await ctx.reply(f"Successfully purged {amount} messages!")

    @commands.command(name="warn", aliases=["w"], brief="Warn a user", description="Warn a user", usage="warn <user> <reason>")
    @commands.has_guild_permissions(kick_members=True)
    async def warn(self, ctx, user: Member, *, reason: str):
        """Warn a user"""
        await ctx.message.delete()
        await self.db.guilds.update_one(
            {"id": ctx.guild.id},
            {"$push": {"storage.warns": {
                "user": user.id,
                "mod": ctx.author.id,
                "reason": reason,
                "date": dt.now()
            }}}
        )
        await ctx.send(f"{user.mention} has been warned for {reason}", delete_after=5)

    @commands.command(name="unwarn", aliases=["uw"], brief="Unwarn a user", description="Unwarn a user", usage="unwarn <user>")
    @commands.has_guild_permissions(kick_members=True)
    async def unwarn(self, ctx, user: Member):
        """Unwarn a user"""
        await ctx.message.delete()
        await self.db.guilds.update_one(
            {"id": ctx.guild.id},
            {"$pull": {"storage.warns": {"user": user.id}}}
        )
        await ctx.send(f"{user.mention} has been unwarned", delete_after=5)

    @commands.command(name="warns", aliases=["w"], brief="Get a user's warns", description="Get a user's warns", usage="warns <user>")
    @commands.has_guild_permissions(kick_members=True)
    async def warns(self, ctx, user: Member):
        """Get a user's warns"""
        await ctx.message.delete()
        warns = self.db.guilds.find_one({"_id": ctx.guild.id})[
            "storage"]["warns"]
        embed = Embed(title=f"{user.name}'s warns", color=0xFF0000)
        for warn in warns:
            if warn["user"] == user.id:
                embed.add_field(
                    name=f"{warn['date']}", value=f"{warn['reason']}")
        await ctx.send(embed=embed)

    @commands.command(name="clearwarns", aliases=["cw"], brief="Clear a user's warns", description="Clear a user's warns", usage="clearwarns <user>")
    @commands.has_guild_permissions(kick_members=True)
    async def clearwarns(self, ctx, user: Member):
        """Clear a user's warns"""
        await ctx.message.delete()
        await self.db.guilds.update_one(
            {"id": ctx.guild.id},
            {"$pull": {"storage.warns": {"user": user.id}}}
        )
        await ctx.send(f"{user.mention}'s warns have been cleared", delete_after=5)


>>>>>>> Stashed changes
def setup(bot):
    bot.add_cog(ModerationCommands(bot, bot.db))
