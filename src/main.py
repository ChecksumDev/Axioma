#!/usr/bin/env python3

from nextcord.activity import Activity
from nextcord.embeds import Embed
from nextcord.enums import ActivityType, Status
from nextcord.ext import commands
from nextcord.ext.commands.errors import (BadArgument, CheckFailure,
                                          CommandError, CommandNotFound,
                                          CommandOnCooldown, DisabledCommand,
                                          MissingRequiredArgument,
                                          NoPrivateMessage)
from nextcord.flags import Intents
from nextcord.guild import Guild
from nextcord.member import Member
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

import config
from misc import init_guild

print("[Axi] Loading...")


class Client(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('$'), **kwargs)
        self.db: Database = MongoClient(
            f"mongodb+srv://{config.mongo.get('username')}:{config.mongo.get('password')}@{config.mongo.get('host')}/{config.mongo.get('db')}?retryWrites=true&w=majority")
        for cog in config.cogs:
            try:
                self.load_extension(cog)
                print(f'[Axi] Loaded {cog}')
            except Exception as exc:
                print(
                    f'[Axi] Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')

    async def on_ready(self):
        print(f'[Axi] Logged on as {self.user} (ID: {self.user.id})')
        print(f'[Axi] Ready to serve {len(self.guilds)} guilds and {len(self.users)} users')
        await self.change_presence(activity=Activity(type=ActivityType.listening, name="$help | created by checksum"), status=Status.do_not_disturb)

    async def on_guild_join(self, guild: Guild):
        await init_guild(self, guild)

    async def on_guild_remove(self, guild: Guild):
        self.db.guilds.delete_one({'id': guild.id})

    async def on_member_join(self, member: Member):
        pass

    async def on_member_remove(self, member: Member):
        pass

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_shard_ready(self, shard_id):
        print(f'[Axi] Shard {shard_id} ready')

    async def on_command_error(self, ctx, error):
        embed = Embed(title="Error", color=0xFF0000)
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_footer(text=f"{ctx.author} | {ctx.guild}")
        if isinstance(error, CommandNotFound):
            return
        if isinstance(error, MissingRequiredArgument):
            embed.description = f"Missing required argument {error.param}"
            await ctx.send(embed=embed)
            return
        if isinstance(error, BadArgument):
            embed.description = f'{ctx.author.mention}, you provided an invalid argument.'
            await ctx.send(embed=embed)
            return
        if isinstance(error, CommandOnCooldown):
            embed.description = f'{ctx.author.mention}, you are on cooldown for {error.retry_after:.2f} seconds.'
            await ctx.send(embed=embed)
            return
        if isinstance(error, CheckFailure):
            embed.description = f'{ctx.author.mention}, you do not have the required permissions.'
            await ctx.send(embed=embed)
            return
        if isinstance(error, CommandError):
            embed.description = f'{ctx.author.mention}, {error}'
            await ctx.send(embed=embed)
            return
        if isinstance(error, NoPrivateMessage):
            embed.description = f'{ctx.author.mention}, this command cannot be used in private messages.'
            await ctx.send(embed=embed)
            return
        if isinstance(error, DisabledCommand):
            embed.description = f'{ctx.author.mention}, this command has been disabled.'
            await ctx.send(embed=embed)
            return


client = Client(intents=Intents.all())
db = client.db.axi

client.run(config.token)
