from random import choice
from nextcord import embeds
from nextcord.ext import commands
from nextcord.embeds import Embed
from nextcord.ext.commands.bot import Bot
from nextcord.member import Member
from pymongo.database import Database
from aiohttp import ClientSession


class FunCommands(commands.Cog, name="Fun"):
    """The description for FunCommands goes here."""

    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db.axi

    @commands.command(name="roll", brief="Rolls a die.")
    async def die(self, ctx: commands.Context, *, args: str = None):
        """Rolls a die.

        Usage:
            roll [number of sides]
        """
        if args is None:
            args = 6
        try:
            args = int(args)
        except ValueError:
            await ctx.send(embed=Embed(
                title="Error",
                description="The number of sides must be an integer.",
                color=0xFF0000
            ))
            return
        if args < 2:
            await ctx.send(embed=Embed(
                title="Error",
                description="The number of sides must be at least 2.",
                color=0xFF0000
            ))
            return
        await ctx.send(embed=Embed(
            title="Rolling a die",
            description=f"You rolled a **{choice(range(1, args + 1))}**.",
            color=0x800080
        ))

    @commands.command(name="flip", brief="Flips a coin.")
    async def coin(self, ctx: commands.Context):
        """Flips a coin.
        Usage:
            `flip`
        Example:
            `flip`
        """
        choices = ["heads", "tails"]
        embed = Embed(
            title="Flipped a coin.",
            description=f"{ctx.author.mention} flipped a coin and got **{choice(choices)}**.",
            color=0x800080,
        )
        await ctx.send(embed=embed)
        return

    @commands.command(name="8ball", brief="Answers a question.")
    async def eightball(self, ctx: commands.Context, *, question: str):
        """Answers a question.
        Usage:
            `8ball [question]`
        Example:
            `8ball Will I win the lottery?`
        """
        choices = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.",
                   "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."]
        embed = Embed(
            title="Magical 8-ball",
            color=0x800080,
        )
        embed.add_field(name="Question", value=question)
        embed.add_field(name="Answer", value=choice(choices))
        await ctx.send(f"{ctx.author.mention} asked: {question}\n{choice(choices)}")
        return

    @commands.command(name="dadjoke", brief="Gets a dad joke.")
    async def dadjoke(self, ctx: commands.Context):
        """Gets a dad joke.
        Usage:
            `dadjoke`
        Example:
            `dadjoke`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://icanhazdadjoke.com/") as response:
                    data = await response.json()
                    embed = Embed(title="Dad Joke",
                                  description=data["joke"], color=0x800080)
                    await ctx.send(embed=embed)
        return

    @commands.command(name="cat", brief="Gets a cat.")
    async def cat(self, ctx: commands.Context):
        """Gets a cat.
        Usage:
            `cat`
        Example:
            `cat`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/cat") as response:
                    cat_face = await response.json()
                    async with session.get("https://api.thecatapi.com/v1/images/search") as response:
                        data = await response.json()
                        embed = Embed(title="Cat",
                                      description=f"{cat_face['cat']}", color=0x800080)
                        embed.set_image(url=data[0]["url"])
                        await ctx.send(embed=embed)
            return

    @commands.command(name="dog", brief="Gets a dog.")
    async def dog(self, ctx: commands.Context):
        """Gets a dog.
        Usage:
            `dog`
        Example:
            `dog`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://dog.ceo/api/breeds/image/random") as response:
                    data = await response.json()
                    # get breed from url
                    breed = data["message"].split("/")[4]
                    embed = Embed(title="Dog",
                                  description=f"Take a look at this cute {breed}!", color=0x800080)
                    embed.set_image(url=data["message"])
                    await ctx.send(embed=embed)
        return

    @commands.command(name="catfact", brief="Gets a cat fact.")
    async def catfact(self, ctx: commands.Context):
        """Gets a cat fact.
        Usage:
            `catfact`
        Example:
            `catfact`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://catfact.ninja/fact") as response:
                    data = await response.json()
                    embed = Embed(title="Cat Fact",
                                  description=data["fact"], color=0x800080)
                    await ctx.send(embed=embed)
        return

    @commands.command(name="dogfact", brief="Gets a dog fact.")
    async def dogfact(self, ctx: commands.Context):
        """Gets a dog fact.
        Usage:
            `dogfact`
        Example:
            `dogfact`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://dog-api.kinduff.com/api/facts") as response:
                    data = await response.json()
                    embed = Embed(title="Dog Fact",
                                  description=data["facts"][0], color=0x800080)
                    await ctx.send(embed=embed)
        return

    @commands.command(name="hug", brief="Hugs someone")
    async def hug(self, ctx: commands.Context, *, member: Member = None):
        """Sends an anime hugging gif.
        Usage:
            `hug`
        Example:
            `hug`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/hug") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} hugs {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return

    @commands.command(name="kiss", brief="Sends an anime kissing gif")
    async def kiss(self, ctx: commands.Context, *, member: Member = None):
        """Sends an anime kissing gif.
        Usage:
            `kiss`
        Example:
            `kiss`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/kiss") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} kisses {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return

    @commands.command(name="pat", brief="Pats someone")
    async def pat(self, ctx: commands.Context, *, member: Member = None):
        """Sends an anime pat gif.
        Usage:
            `pat`
        Example:
            `pat`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/pat") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} pats {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return

    @commands.command(name="slap", brief="Slaps someone")
    async def slap(self, ctx: commands.Context, *, member: Member = None):
        """Sends an anime slapping gif.
        Usage:
            `slap`
        Example:
            `slap`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/slap") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} slaps {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return

    @commands.command(name="tickle", brief="Tickles someone")
    async def tickle(self, ctx: commands.Context, *, member: Member = None):
        """Sends an anime tickling gif.
        Usage:
            `tickle`
        Example:
            `tickle`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/tickle") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} tickles {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return

    @commands.command(name="cuddle", brief="Cuddles with someone")
    async def cuddle(self, ctx: commands.Context, *, member: Member = None):
        """Sends an anime cuddling gif.
        Usage:
            `cuddle`
        Example:
            `cuddle`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/cuddle") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} cuddles {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return

    @commands.command(name="poke", brief="Pokes someone")
    async def poke(self, ctx: commands.Context, *, member: Member = None):
        """Sends an anime poking gif.
        Usage:
            `poke`
        Example:
            `poke`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/poke") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} pokes {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return

    @commands.command(name="smug", brief="'smugs' someone??")
    async def smug(self, ctx: commands.Context, *, member: Member = None):
        """Sends an anime smug gif.
        Usage:
            `smug`
        Example:
            `smug`
        """
        async with ctx.typing():
            async with ClientSession() as session:
                async with session.get("https://nekos.life/api/v2/img/smug") as response:
                    data = await response.json()
                    embed = Embed(
                        title=f"{ctx.author.name} is smug at {member.name}", color=0x800080)
                    embed.set_image(url=data['url'])
                    await ctx.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(FunCommands(bot, bot.db))
