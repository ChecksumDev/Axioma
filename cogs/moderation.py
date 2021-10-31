from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.ext.commands.bot import Bot
from nextcord.member import Member
from pymongo.database import Database


class ModerationCommands(commands.Cog, name="Moderation"):
    """The description for ModerationCommands goes here."""

    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db.axi
        self.pagination_warns = []
        self.pagination_warns_current_page = 0

    async def on_reaction_add(self, reaction, user):
        """Respods to reactions added to the bot's messages, for pagination."""
        message = reaction.message
        if message.author.id != self.bot.user.id:
            return

        if reaction.emoji == "⏮":
            # go to the first page
            await message.edit(embed=Embed(self.pagination_warns[0]))
            return
        elif reaction.emoji == "⏭":
            # go to the last page
            await message.edit(embed=Embed(self.pagination_warns[-1]))
        elif reaction.emoji == "◀":
            # go to the previous page
            if self.pagination_warns_current_page > 0:
                self.pagination_warns_current_page -= 1
                await message.edit(embed=Embed(self.pagination_warns[self.pagination_warns_current_page]))
        elif reaction.emoji == "▶":
            # go to the next page
            if self.pagination_warns_current_page < len(self.pagination_warns) - 1:
                self.pagination_warns_current_page += 1
                await message.edit(embed=Embed(self.pagination_warns[self.pagination_warns_current_page]))
        

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

    @commands.command(name="warn", aliases=["w"], brief="Warn a user", description="Warn a user", usage="warn <user> <reason>")
    @commands.has_guild_permissions(kick_members=True)
    async def warn(self, ctx, user: Member, *, reason: str):
        """Warn a user"""
        if user.id == ctx.author.id:
            return await ctx.send("You can't warn yourself")

        self.db.warns.insert_one({"user": user.id,
                                  "guild": ctx.guild.id,
                                  "mod": ctx.author.id,
                                  "reason": reason,
                                  "date": ctx.message.created_at})

        await ctx.message.delete()
        await ctx.send(f"{user.mention} has been warned for `{reason}`")

    @commands.command(name="warns", aliases=["ws"], brief="Get a user's warns", description="Get a user's warns", usage="warns <user>")
    @commands.has_guild_permissions(kick_members=True)
    async def warns(self, ctx, user: Member):
        """Get a user's warns"""
        warns = self.db.warns.find({"user": user.id, "guild": ctx.guild.id})
        warns_count = self.db.warns.count({"user": user.id, "guild": ctx.guild.id})
        
        # get the number of warns for the user without using count()
        if warns_count == 0:
            return await ctx.send(f"{user.mention} has no warns")

        for i in range(0, warns_count, 5):
            embed = Embed(title=f"{user.name}'s warns",
                          description="", color=0x800080)
            embed.set_author(name=ctx.author.name)
            embed.set_footer(
                text=f"Page {i // 5 + 1}/{(warns.count() // 5) + 1}")

            for warn in warns[i:i + 5]:
                embed.add_field(
                    name=f"{warn['mod']}", value=f"{warn['reason']}", inline=False)

            self.pagination_warns.append(embed)

        self.pagination_warns_current_page = 0
        await ctx.send(embed=self.pagination_warns[0])
        await ctx.message.add_reaction("⏮")
        await ctx.message.add_reaction("◀")
        await ctx.message.add_reaction("▶")
        await ctx.message.add_reaction("⏭")


def setup(bot):
    bot.add_cog(ModerationCommands(bot, bot.db))
