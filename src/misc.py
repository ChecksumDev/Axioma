from typing import Collection
from nextcord.member import Member
from datetime import datetime as dt
from nextcord.guild import Guild
from pymongo import MongoClient
from pymongo.database import Database
import config

print("[Misc] Initializing MongoDB connection...")

mongo = MongoClient(
    f"mongodb+srv://{config.mongo.get('username')}:{config.mongo.get('password')}@{config.mongo.get('host')}/{config.mongo.get('db')}?retryWrites=true&w=majority")
db = mongo.authenticator  # Connect to the database
servers_cursor = db.servers  # Connect to the collection
users_cursor = db.users  # Connect to the collection


class TrustScore:
    TRUSTED_0 = 0 >= 1000
    TRUSTED_1 = 0 >= 900
    TRUSTED_2 = 0 >= 800
    TRUSTED_3 = 0 >= 700
    TRUSTED_4 = 0 >= 600
    TRUSTED_5 = 0 >= 500
    TRUSTED_6 = 0 >= 400
    TRUSTED_7 = 0 >= 300
    TRUSTED_8 = 0 >= 200
    TRUSTED_9 = 0 >= 100
    TRUSTED_10 = 0 >= 0


def calculate_trust_score(user: Member):
    """ 
    This function will calculate the trust score of a given discord account 
    by checking aspects like if the account has an avatar, how old the
    account is, if the account has nitro, etc
    """
    trust_score = 0

    if user.avatar is not None and user.avatar != "":
        trust_score += 100
        if user.avatar.is_animated():
            trust_score += 500

    if user.banner is not None and user.banner != "":
        trust_score += 300

    trust_score += (dt.now().year - user.created_at.year) * \
        250 if (dt.now().year - user.created_at.year) > 0 else 0

    if user.public_flags.verified_bot_developer is True or user.public_flags.verified_bot_developer is True:
        trust_score += 500

    if user.public_flags.early_supporter is True:
        trust_score += 500

    if user.public_flags.hypesquad is True:
        trust_score += 500

    if user.public_flags.hypesquad_balance is True:
        trust_score += 150

    if user.public_flags.hypesquad_bravery is True:
        trust_score += 150

    if user.public_flags.hypesquad_brilliance is True:
        trust_score += 150

    if user.public_flags.partner is True:
        trust_score += 1000

    if user.public_flags.bug_hunter is True:
        trust_score += 1000

    if user.public_flags.bug_hunter_level_2:
        trust_score += 1000

    if user.public_flags.staff is True:
        trust_score += 10000

    return trust_score


async def get_role_by_name(guild, name):
    for role in guild.roles:
        if role.name == name:
            return role
    return None


async def get_channel_by_name(guild, name):
    for channel in guild.channels:
        if channel.name == name:
            return channel
    return None


def init_guild(guild: Guild, db: Database):
    db.config.insert_one({
        'id': guild.id,
        'prefix': '$',
        'settings': {
            'welcome': {
                'enabled': False,
                'message': None,
                'channel': None,
                'dm': False,
            },
            'verification': {
                'enabled': False,
                'channel': None,
                'role': None
            },
            'leave': {
                'enabled': False,
                'message': None,
                'channel': None,
                'role': None,
            },
            'modlog': {
                'enabled': False,
                'channel': None,
            },
            'modmail': { # TODO: Add more modmail settings
                'enabled': False,
                'channel': None,
            },
            'autorole': {
                'enabled': False,
                'roles': [],
            },
        }
    })
