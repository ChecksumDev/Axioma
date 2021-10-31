#!/usr/bin/env python3

from nextcord.activity import Game
from nextcord.embeds import Embed
from nextcord.enums import Status
from nextcord.ext import commands
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


client = Client(intents=Intents.all())

# Connect to MongoDB
db = client.db.axi  # Connect to the database
cursor = db.meta  # Connect to the collection


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    await client.change_presence(status=Status.do_not_disturb, activity=Game("$help / checksum is my creator."))

    for guild in client.guilds:
        isInitilized = cursor.find_one({"server": guild.id})
        if isInitilized is None:
            init_guild(guild, cursor)

@client.event
async def on_member_join(member: Member):
    server = cursor.find_one({"server": member.guild.id})

    if server is None:
        return print(f'{member.guild.name} has no server settings, aborting on_member_join')

    if server["modules"]["verification"] == True:
        print(f'{member.name} has joined {member.guild.name}, waiting for verification')

    if server["modules"]["welcome"] == True:
        await member.send(server.settings.welcome_message)


@client.event
async def on_member_remove(member: Member):
    server = cursor.find_one({"server": member.guild.id})

    if server is None:
        print(f'{member.guild.name} has no server settings, aborting on_member_join')
        return

    if server["modules"]["verification"] == True:
        print(f'{member.name} has left {member.guild.name}, deleting user settings')


@client.event
async def on_guild_join(guild: Guild):
    init_guild(guild)

    print(f'{client.user.name} has been added to {guild.name}, adding to database')
    embed = Embed(title="Hey there!",
                  description=f'Thank you for adding me to {guild.name}!\nAll of my features are disabled by default, to configure me, run the {cursor.find({"server": guild.id}).next()["settings"]["prefix"]}config command.', color=0x800080)
    await guild.owner.send(embed=embed)

client.run(config.token)
