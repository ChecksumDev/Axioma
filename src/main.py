#!/usr/bin/env python3

from types import TracebackType
from nextcord.activity import Activity
from nextcord.embeds import Embed
from nextcord.enums import ActivityType, Status
from nextcord.ext import commands
from nextcord.ext.commands.context import Context
from nextcord.ext.commands.errors import (BadArgument, CheckFailure,
                                          CommandError, CommandNotFound,
                                          CommandOnCooldown, DisabledCommand,
                                          MissingRequiredArgument,
                                          NoPrivateMessage, MissingPermissions)
from nextcord.flags import Intents
from nextcord.guild import Guild
from nextcord.member import Member
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from classes.MemberClass import MemberClass

import config
from secrets import token_urlsafe
from misc import init_guild

print("[Axi] Loading...")


class Client(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('$'), **kwargs)
        self.mongo = MongoClient(
            f"mongodb+srv://{config.mongo.get('username')}:{config.mongo.get('password')}@{config.mongo.get('host')}/{config.mongo.get('db')}?retryWrites=true&w=majority")
        self.db: Database = self.mongo.axi  # ! SELF -> CLIENT -> DB -> COLLECTION

        for cog in config.cogs:
            try:
                self.load_extension(cog)
                print(f'[Axi] Loaded {cog}')
            except Exception as exc:
                print(
                    f'[Axi] Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')

    async def on_ready(self):
        print(f'[Axi] Logged on as {self.user} (ID: {self.user.id})')
        print(
            f'[Axi] Ready to serve {len(self.guilds)} guilds and {len(self.users)} users')
        await self.change_presence(activity=Activity(type=ActivityType.listening, name=f"$help | Serving {len(self.guilds)} guilds and {len(self.users)} users!"))

        for guild in self.guilds:
            init_guild(guild, self.db)
                    
            
    async def on_guild_join(self, guild: Guild):
        await init_guild(self, guild)

        async for member in guild.fetch_members(limit=None):
            user = self.db.users.find_one({'id': member.id})
            if user is None:
                self.db.users.insert_one({
                    'id': member.id,
                    'username': member.name,
                    'discriminator': member.discriminator,
                    'avatar': member.display_avatar.url,
                    'bot': member.bot,
                    'guilds': [],
                    'settings': {
                        'timezone': 'UTC',
                        'language': 'en-US',
                    },
                })
            else:
                self.db.users.update_one(
                    {'id': member.id}, {'$push': {'guilds': member.guild.id}})

    async def on_guild_remove(self, guild: Guild):
        self.db.guilds.delete_one({'id': guild.id})

    async def on_member_join(self, member: Member):
        # TODO: Add welcome message
        user = self.db.users.find_one({'id': member.id})
        if user is None:
            self.db.users.insert_one({
                'id': member.id,
                'username': member.name,
                'discriminator': member.discriminator,
                'avatar': member.display_avatar.url,
                'bot': member.bot,
                'guilds': [],
                'settings': {
                    'timezone': 'UTC',
                    'language': 'en-US',
                },
            })
        else:
            self.db.users.update_one(
                {'id': member.id}, {'$push': {'guilds': member.guild.id}})

        pass

    async def on_member_remove(self, member: Member):
        self.db.users.update_one(
            {'id': member.id}, {'$pull': {'guilds': member.guild.id}})
        pass

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_shard_ready(self, shard_id):
        print(f'[Axi] Shard {shard_id} ready')

    async def on_command_error(self, ctx: Context, error):
        embed = Embed(
            title="I'm sorry Dave, I'm afraid I can't do that.", color=0xFF0000)
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_footer(text=f"{ctx.author} | {ctx.guild}")

        embed_log = embed.copy()
        error_id = token_urlsafe(4)

        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, MissingRequiredArgument):
            embed.add_field(
                name="Error", value=f"Missing required argument (`{error.param.name}`)")
            await ctx.send(embed=embed)
            return
        elif isinstance(error, BadArgument):
            embed.add_field(
                name="Error", value=f"Invalid argument (`{error.param.name}`)")
            await ctx.send(embed=embed)
            return
        elif isinstance(error, CommandOnCooldown):
            embed.add_field(
                name="Error", value=f"You are on cooldown for {error.retry_after:.2f} seconds.")
            await ctx.send(embed=embed)
            return
        elif isinstance(error, CheckFailure):
            embed.add_field(
                name="Error", value=f"You do not have the required permissions.")
            await ctx.send(embed=embed)
            return
        elif isinstance(error, MissingPermissions):
            embed.add_field(
                name="Error", value=f'You do not have the required permissions (`{", ".join(error.missing_perms)}`). to run this command.')
            await ctx.send(embed=embed)
            return
        elif isinstance(error, CommandError):
            embed.add_field(
                name="Error", value=f"An error has occurred while running the command.")
            await ctx.send(embed=embed)

            embed_log.set_footer(
                text=f"ID: {error_id} | {ctx.author} | {ctx.guild}")
            embed_log.add_field(
                name="Command", value=f"{ctx.command}", inline=False)
            embed_log.add_field(
                name="Error", value=f"```{error.with_traceback(None)}```", inline=False)
            error_log = self.get_channel(904422022585655298)
            await error_log.send(content="<@&904422021302198335> A fatal error has occured!", embed=embed_log)
            return
        elif isinstance(error, NoPrivateMessage):
            embed.add_field(
                name="Error", value=f"This command cannot be used in private messages.")
            await ctx.send(embed=embed)
            return
        elif isinstance(error, DisabledCommand):
            embed.add_field(
                name="Error", value=f"This command has been disabled.")
            await ctx.send(embed=embed)
            return


client = Client(intents=Intents.all())
db = client.db

client.run(config.token)
