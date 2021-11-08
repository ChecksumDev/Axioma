from asyncio import run_coroutine_threadsafe
from math import ceil
from nextcord.ext.commands.bot import Bot

from nextcord.ext.commands.context import Context
from nextcord.ext.commands.errors import CommandError
from pymongo.database import Database

import config
from utils.downloader import Downloader
from nextcord.embeds import Embed
from nextcord.ext import commands
from nextcord.player import FFmpegPCMAudio, PCMVolumeTransformer
from youtube_dl import DownloadError

FFMPEG_BEFORE_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'


async def audio_playing(ctx: Context):
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        raise CommandError('Not currently playing any audio.')


async def in_voice_channel(ctx: Context):
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        raise CommandError(
            'You need to be in the channel to do that.')


class MusicCommands(commands.Cog, name='Music'):
    def __init__(self, bot: Bot, db: Database, config):
        self.bot = bot
        self.config = config
<<<<<<< Updated upstream
        self.db = db
=======
        self.db = db.axi
        self.storage = {}
>>>>>>> Stashed changes
        self.bot.add_listener(self.on_reaction_add, 'on_reaction_add')

    def _vote_skip(self, channel, member):
        self.db.guilds.update_one({'id': channel.guild.id}, {
            '$push': {'storage.music.skip_votes': member.id}})
        votes = self.db.guilds.find_one({'id': channel.guild.id})[
            'storage']['music']['skip_votes']

        users_in_channel = len(
            [member for member in channel.members if not member.bot])
        if float(len(votes))/users_in_channel >= int(self.db.guilds.find_one({'id': channel.guild.id})['settings']['music']['vote_skip_percentage']):
            channel.guild.voice_client.stop()

    def _play_song(self, client, song):
        self.queue = self.db.guilds.find_one({'id': client.guild.id})[
            'storage']['music']['queue']
    
        self.db.guilds.update_one({'id': client.guild.id}, {
            '$push': {'storage.music.current_song': song}})

        self.source = PCMVolumeTransformer(FFmpegPCMAudio(
            song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume=self.db.guilds.find_one({'id': client.guild.id})['settings']['music']['volume'])

        def after_playing(err):
            if len(self.queue) > 0:
                self.db.guilds.update_one({'id': client.guild.id}, {
                    '$pop': {'storage.music.queue': 1}})
                next_song = self.db.guilds.find_one({'id': client.guild.id})[
                    'storage']['music']['queue'][0]

                self._play_song(client, next_song)
            else:
                self.db.guilds.update_one({'id': client.guild.id}, {
                    '$set': {'storage.music.current_song': None, 'storage.music.queue': [], 'storage.music.skip_votes': []}})
                run_coroutine_threadsafe(client.disconnect(), self.bot.loop)
        client.play(self.source, after=after_playing)

    async def _add_reaction_controls(self, message):
        CONTROLS = ['⏮', '⏯', '⏭']
        for control in CONTROLS:
            await message.add_reaction(control)

    def _pause_audio(self, client):
        if client.is_paused():
            client.resume()
        else:
            client.pause()

    def _queue_embed(self, queue):
        if len(queue) > 0:
            embed = Embed(title='Queue', description='\n'.join(
                [f'{index+1}. {song.title}' for index, song in enumerate(queue)]), color=0x800080)
            return embed
        else:
            embed = Embed(
                title='Queue', description='No songs in queue.', color=0x800080)
            return embed

    @commands.command(name='stop', aliases=['leave', 'disconnect'], brief='Stops the bot from playing music.')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def leave(self, ctx):
        client = ctx.guild.voice_client
        if client and client.channel:
            await client.disconnect()
            self.db.guilds.update_one({'id': ctx.guild.id}, {
                '$set': {'storage.music.current_song': None, 'storage.music.queue': [], 'storage.music.skip_votes': []}})

            await ctx.send('Disconnected from the voice channel.')
        else:
            raise CommandError('Not in a voice channel.')

    @commands.command(name='resume', aliases=['pause'], brief='Resumes or pauses the current song.')
    @commands.guild_only()
    async def pause(self, ctx):
        client = ctx.guild.voice_client
        self._pause_audio(client)
        await ctx.send('Paused/resumed the audio.')

    @commands.command(name='volume', aliases=['vol'], usage='<volume>', brief='Sets the volume of the music.')
    @commands.guild_only()
    async def volume(self, ctx, volume: int):
        if volume < 0:
            volume = 0
        max_vol = self.db.guilds.find_one({'id': ctx.guild.id})[
            'storage']['music']['volume']
        if max_vol > -1:
            if volume > max_vol:
                volume = max_vol

        client = ctx.guild.voice_client

        if client and client.channel:
            self.db.guilds.update_one({'id': ctx.guild.id}, {
                '$set': {'storage.music.volume': volume}})
            client.source.volume = float(volume)/100.0
            await ctx.send(f'Set the volume to {volume}%.')
        else:
            raise CommandError('Not in a voice channel.')

        embed = Embed(title='Volume',
                      description=f'Volume set to {volume}%.', color=0x800080)
        await ctx.send(embed=embed)

    @commands.command(name="skip", aliases=['s'], brief='Skip the current song.')
    @commands.guild_only()
    async def skip(self, ctx):
        client = ctx.guild.voice_client
        if ctx.channel.permissions_for(ctx.author).administrator:
            client.stop()
            await ctx.send('Skipped the current song.')
        elif self.db.guilds.find_one({'id': ctx.guild.id})['storage']['music']['current_song']:
            channel = client.channel
            self._vote_skip(channel, ctx.author)
            users_in_channel = len(
                [member for member in channel.members if not member.bot])

            required_votes = ceil(int(self.db.guilds.find_one({'id': channel.guild.id})[
                                  'settings']['music']['vote_skip_percentage']) * users_in_channel)
            await ctx.send(f"{ctx.author.mention} voted to skip ({len(self.db.guilds.find_one({'id': ctx.guild.id})['storage']['music']['skip_votes'])}/{required_votes})")
            if len(self.db.guilds.find_one({'id': ctx.guild.id})['storage']['music']['skip_votes']) >= required_votes:
                self._vote_skip()
                await ctx.send('Skipped the current song.')
        else:
            raise CommandError('You need to be the song requester to do that.')

    @commands.command(name='np', aliases=['nowplaying', 'currentsong', 'current'], brief='Shows the currently playing song.')
    @commands.guild_only()
    async def now_playing(self, ctx):
        current_song = self.db.guilds.find_one({'id': ctx.guild.id})[
            'storage']['music']['current_song']
        if current_song:
            embed = Embed(title='Now Playing',
                          description=current_song['title'], color=0x800080)
            await ctx.send(embed=embed)
        else:
            raise CommandError('No song is currently playing.')

    @commands.command(name='queue', aliases=['q'], brief='Shows the current queue.')
    @commands.guild_only()
    async def queue(self, ctx):
        queue = self.db.guilds.find_one({'id': ctx.guild.id})[
            'storage']['music']['queue']
        embed = self._queue_embed(queue)
        await ctx.send(embed=embed)

    @commands.command(name='clear', aliases=['clr', 'cq'], brief='Clears the queue.')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def clear_queue(self, ctx):
        self.db.guilds.update_one({'id': ctx.guild.id}, {
            '$set': {'storage.music.queue': []}})
        await ctx.send('Cleared the queue.')

    @commands.command(name='jump', aliases=['jq'], usage='<song number>', brief='Jumps to a song in the queue.')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def jump_queue(self, ctx, song_number: int):
        queue = self.db.guilds.find_one({'id': ctx.guild.id})[
            'storage']['music']['queue']
        if song_number > len(queue):
            raise CommandError('Song number is too high.')
        elif song_number < 1:
            raise CommandError('Song number is too low.')
        else:
            self.db.guilds.update_one({'id': ctx.guild.id}, {
                '$set': {'storage.music.current_song': queue[song_number - 1]}})
            self._play_song(ctx.guild.voice_client, queue[song_number - 1])
            await ctx.send(f'Jumped to song {song_number}.')

    @commands.command(name='play', aliases=['p', 'search'], usage='<query>')
    @commands.guild_only()
    async def play(self, ctx, *, url):
        client = ctx.guild.voice_client
        if client and client.channel:
            try:
                video = Downloader(url, ctx.author)
                print(video._get_info())
            except DownloadError as e:
                await ctx.send(f"Error downloading video: {e}")
                return
            self.db.guilds.update_one({'id': ctx.guild.id}, {
                '$set': {'storage.music.current_song': video}})
            message = await ctx.send('Added to queue.', embed=video.get_embed())
            await self._add_reaction_controls(message)
        elif ctx.author.voice is not None and ctx.author.voice.channel is not None:
            channel = ctx.author.voice.channel
            try:
                video = Downloader(url, ctx.author)
            except DownloadError as e:
                raise CommandError(f"Error downloading video: {e}")
            client = await channel.connect()
            print(video.video)
            self._play_song(client, video)
            message = await ctx.send('', embed=video.get_embed())
            await self._add_reaction_controls(message)
        else:
            raise CommandError(
                'You need to be in a voice channel to do that.')

    async def on_reaction_add(self, reaction, user):
        if reaction.message.id in self.reaction_controls:
            if reaction.emoji == '⏯':
                if user.id == reaction.message.author.id:
                    if self.db.guilds.find_one({'id': reaction.message.guild.id})['storage']['music']['current_song']:
                        if reaction.message.guild.voice_client.is_playing():
                            reaction.message.guild.voice_client.pause()
                            await reaction.message.edit(embed=Embed(title='Paused', color=0x800080))
                        else:
                            reaction.message.guild.voice_client.resume()
                            await reaction.message.edit(embed=Embed(title='Resumed', color=0x800080))
                    else:
                        raise CommandError('No song is currently playing.')
                else:
                    raise CommandError(
                        'You need to be the song requester to do that.')
            elif reaction.emoji == '⏭':
                if user.id == reaction.message.author.id:
                    if self.db.guilds.find_one({'id': reaction.message.guild.id})['storage']['music']['current_song']:
                        if reaction.message.guild.voice_client.is_playing():
                            reaction.message.guild.voice_client.stop()
                            await reaction.message.edit(embed=Embed(title='Stopped', color=0x800080))
                        else:
                            raise CommandError('No song is currently playing.')
                    else:
                        raise CommandError('No song is currently playing.')
                else:
                    raise CommandError(
                        'You need to be the song requester to do that.')
            elif reaction.emoji == '⏯':
                if user.id == reaction.message.author.id:
                    if self.db.guilds.find_one({'id': reaction.message.guild.id})['storage']['music']['current_song']:
                        if reaction.message.guild.voice_client.is_playing():
                            reaction.message.guild.voice_client.pause()
                            await reaction.message.edit(embed=Embed(title='Paused', color=0x800080))
                        else:
                            reaction.message.guild.voice_client.resume()
                            await reaction.message.edit(embed=Embed(title='Resumed', color=0x800080))
                    else:
                        raise CommandError('No song is currently playing.')
                else:
                    raise CommandError(
                        'You need to be the song requester to do that.')


def setup(bot):
    bot.add_cog(MusicCommands(bot, bot.db, config))
