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

mongo = MongoClient(f"mongodb+srv://{config.mongo.get('username')}:{config.mongo.get('password')}@{config.mongo.get('host')}/{config.mongo.get('db')}?retryWrites=true&w=majority")
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

    @commands.command(name="config", description="Configure the bot.", brief="Configure the bot's modules", aliases=["configure"], category="General")
    async def config(self, ctx: commands.Context):
        server = servers_cursor.find_one({"server": ctx.guild.id})
        modules = server["modules"]

        embed = Embed(title="Configure the bot",
                      description="Here are the modules you can configure:", color=0x800080)

        for m in modules:
            embed.add_field(
                name=m, value=f"{'**`✅ Enabled`**' if modules[m] == True else '**`❌ Disabled`**'}", inline=True)

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
