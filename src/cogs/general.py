from pymongo.database import Database
import config
import misc
from nextcord import utils
from nextcord.client import Client
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.ext.commands.errors import MemberNotFound
from nextcord.member import Member
from nextcord.user import ClientUser
from pymongo import MongoClient

mongo = MongoClient(
    f"mongodb+srv://{config.mongo.get('username')}:{config.mongo.get('password')}@{config.mongo.get('host')}/{config.mongo.get('db')}?retryWrites=true&w=majority")
db = mongo.authenticator
servers_cursor = db.servers
users_cursor = db.users


class GeneralCommands(commands.Cog):
    """Miscellaneous Commands"""

    def __init__(self: ClientUser, client: commands.Bot, db: Database):
        self.client = client
        self.db = db.axi

    @commands.command(name="ping", description="Pong!", brief="Pong!", aliases=["pong"], category="General")
    async def ping(self, ctx: commands.Context):
        embed = Embed(
            title="Pong!", description=f"The client latency is around {round(self.client.latency * 1000)}ms.", color=0x800080)
        await ctx.send(embed=embed)

    @commands.command(name="serverinfo", description="Get information about the server.", brief="Get information about the server.", aliases=["server", "guildinfo", "guild"], category="General")
    async def serverinfo(self, ctx: commands.Context):
        server = ctx.guild
        embed = Embed(
            title=f"{server.name}",
            description=f"{server.description if server.description else 'No description'}",
            color=0x800080,
        )

        embed.add_field(name="Owner", value=f"{server.owner}")
        embed.add_field(name="Members", value=f"{server.member_count}")
        embed.add_field(name="Roles", value=f"{len(server.roles)}")
        embed.add_field(name="Channels", value=f"{len(server.channels)}")
        embed.add_field(name="Created At",
                        value=f"{server.created_at.strftime('%d/%m/%Y')}")

        if server.icon:
            embed.set_thumbnail(url=server.icon.url)
        if server.banner:
            embed.set_image(url=server.banner.url)
        elif server.splash:
            embed.set_image(url=server.splash.url)

        embed.set_footer(text=f"ID: {server.id}")
        await ctx.send(embed=embed)

    @commands.command(name="userinfo", description="Get information about the user.", brief="Get information about the user.", aliases=["user", "memberinfo", "member"], category="General")
    async def userinfo(self, ctx: commands.Context, member: Member = None):
        if member is None:
            member = ctx.author
        embed = Embed(
            title=f"{member.name}",
            description=f"{member.mention}",
            color=0x800080,
        )

        if member.banner is not None:
            embed.set_image(url=member.banner.url)

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        if member.nick:
            embed.add_field(name="Nickname",
                            value=f"{member.nick}", inline=False)

        if member.joined_at:
            embed.add_field(
                name="Joined At", value=f"{member.joined_at.strftime('%d/%m/%Y')}", inline=False)

        if member.roles:
            embed.add_field(
                name="Roles", value=f"{', '.join([role.name for role in member.roles])}", inline=False)

        if member.activity:
            embed.add_field(name="Activity",
                            value=f"{member.activity.name}", inline=False)

        if member.status:
            embed.add_field(
                name="Status", value=f"{member.status.name}", inline=False)

        trustscore = misc.calculate_trust_score(member)
        embed.add_field(name="Trust Score", value=f"{trustscore}", inline=False)

        embed.set_footer(
            text=f"ID: {member.id} | Account Created At: {member.created_at.strftime('%d/%m/%Y @ %H:%M:%S')}")
        await ctx.send(embed=embed)

    @commands.command(name="trustscore", description="Calculate the trustscore of a user.", brief="Calculate the trustscore of a user.", aliases=["ts"], category="General")
    async def calc_trustscore(self, ctx: commands.Context, *, member: Member):
        try:
            score = misc.calculate_trust_score(member)

            # create a purple embed with the trustscore, avatar, name and discriminator
            embed = Embed(title=f"{member.name}#{member.discriminator}'s trustscore",
                          description=f"This score is automagically determined by automatic checks.", color=0x800080)
            embed.add_field(
                name="Score", value=f"**{score if score>=0 else 'Unknown'}**", inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)

            embed.set_footer(text=f"Copyright © checksum")

            await ctx.send(embed=embed)
        except MemberNotFound:
            await ctx.send(f"The specified member could not be found.")

    @commands.command(name="invite", description="Get the invite link for the bot.", brief="Get the invite link for the bot.", aliases=["inv"], category="General")
    async def invite(self, ctx: commands.Context):
        await ctx.send(f"Invite me to your server: https://discord.com/oauth2/authorize?client_id=638432564612300842&scope=bot&permissions=8")


def setup(bot):
    bot.add_cog(GeneralCommands(bot, bot.db))
