from asyncio import run_coroutine_threadsafe
from math import ceil

from nextcord.ext.commands.context import Context

import config
from misc.downloader import Downloader
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
        raise commands.CommandError('Not currently playing any audio.')


async def in_voice_channel(ctx: Context):
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        raise commands.CommandError(
            'You need to be in the channel to do that.')


async def is_audio_requester(ctx: Context):
    music = ctx.bot.get_cog('Music')
    storage = music.get_storage(ctx.guild)
    permissions = ctx.channel.permissions_for(ctx.author)
    if permissions.administrator or storage.is_requester(ctx.author):
        return True
    else:
        raise commands.CommandError(
            'You need to be the song requester to do that.')


class MusicCommands(commands.Cog, name='Music'):
    def __init__(self, bot, db, config):
        self.bot = bot
        self.config = config
        self.db = db.axi
        self.storage = {
        }
        self.bot.add_listener(self.on_reaction_add, 'on_reaction_add')

    def _get_storage(self, guild):
        if guild.id in self.storage:
            return self.storage[guild.id]
        else:
            self.storage[guild.id] = State()
            return self.storage[guild.id]

    def _vote_skip(self, channel, member):
        storage = self._get_storage(channel.guild)
        storage.skip_votes.add(member)
        users_in_channel = len(
            [member for member in channel.members if not member.bot])
        if float(len(storage.skip_votes))/users_in_channel >= self.config.music.get('vote_skip_ratio'):
            channel.guild.voice_client.stop()

    def _play_song(self, client, storage, song):
        storage.now_playing = song
        storage.skip_votes = set()
        source = PCMVolumeTransformer(FFmpegPCMAudio(
            song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume=storage.volume)

        def after_playing(err):
            if len(storage.playlist) > 0:
                next_song = storage.playlist.pop(0)
                self._play_song(client, storage, next_song)
            else:
                run_coroutine_threadsafe(client.disconnect(), self.bot.loop)
        client.play(source, after=after_playing)

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
        storage = self._get_storage(ctx.guild)
        if client and client.channel:
            await client.disconnect()
            storage.playlist = []
            storage.now_playing = None
            await ctx.send('Left the voice channel.')
        else:
            raise commands.CommandError('Not in a voice channel.')

    @commands.command(name='resume', aliases=['pause'], brief='Resumes or pauses the current song.')
    @commands.guild_only()
    async def pause(self, ctx):
        client = ctx.guild.voice_client
        self._pause_audio(client)
        await ctx.send('Paused/resumed the audio.')

    @commands.command(name='volume', aliases=['vol'], usage='<volume>', brief='Sets the volume of the music.')
    @commands.guild_only()
    async def volume(self, ctx, volume):
        storage = self._get_storage(ctx.guild)
        if volume < 0:
            volume = 0
        max_vol = self.config.music.get('max_volume')
        if max_vol > -1:
            if volume > max_vol:
                volume = max_vol
        client = ctx.guild.voice_client
        storage.volume = float(volume)/100.0
        client.source.volume = storage.volume
        await ctx.send(f"Set the volume to {volume}%.")

    @commands.command(name="skip", aliases=['s'], brief='Skip the current song.')
    @commands.guild_only()
    async def skip(self, ctx):
        storage = self._get_storage(ctx.guild)
        client = ctx.guild.voice_client
        if ctx.channel.permissions_for(ctx.author).administrator or storage.is_requester(ctx.author):
            client.stop()
        elif self.config.music.get('vote_skip'):
            channel = client.channel
            self._vote_skip(channel, ctx.author)
            users_in_channel = len(
                [member for member in channel.members if not member.bot])
            required_votes = ceil(self.config.music.get(
                'vote_skip_ratio')*users_in_channel)
            await ctx.send(f"{ctx.author.mention} voted to skip ({len(storage.skip_votes)}/{required_votes} votes)")
        else:
            raise commands.CommandError('Sorry, vote skipping is disabled.')

    @commands.command(name='np', aliases=['nowplaying', 'currentsong', 'current'], brief='Shows the currently playing song.')
    @commands.guild_only()
    async def nowplaying(self, ctx):
        storage = self._get_storage(ctx.guild)
        message = await ctx.send('', embed=storage.now_playing.get_embed())
        await self._add_reaction_controls(message)

    @commands.command(name='queue', aliases=['q'], brief='Shows the current queue.')
    @commands.guild_only()
    async def queue(self, ctx):
        storage = self._get_storage(ctx.guild)
        await ctx.send(embed=self._queue_embed(storage.playlist))

    @commands.command(name='clear', aliases=['clr', 'cq'], brief='Clears the queue.')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def clearqueue(self, ctx):
        storage = self._get_storage(ctx.guild)
        storage.playlist = []
        ctx.send('Cleared the play queue.')

    @commands.command(name='jump', aliases=['jq'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def jumpqueue(self, ctx, song, new_index):
        storage = self._get_storage(ctx.guild)
        if 1 <= song <= len(storage.playlist) and 1 <= new_index:
            song = storage.playlist.pop(song-1)
            storage.playlist.insert(new_index-1, song)
            await ctx.send(self._queue_text(storage.playlist))
        else:
            raise commands.CommandError('You must use a valid index.')

    @commands.command(name='play', aliases=['p', 'search'], usage='<query>')
    @commands.guild_only()
    async def play(self, ctx, *, url):
        client = ctx.guild.voice_client
        storage = self._get_storage(ctx.guild)
        if client and client.channel:
            try:
                video = Downloader(url, ctx.author)
            except DownloadError as e:
                await ctx.send(f"Error downloading video: {e}")
                return
            storage.playlist.append(video)
            message = await ctx.send('Added to queue.', embed=video.get_embed())
            await self._add_reaction_controls(message)
        elif ctx.author.voice is not None and ctx.author.voice.channel is not None:
            channel = ctx.author.voice.channel
            try:
                video = Downloader(url, ctx.author)
            except DownloadError as e:
                embed = Embed(
                    title='Error', description=f"Error downloading video: {e}", color=8388736)
                await ctx.send(embed=embed)
                return
            client = await channel.connect()
            self._play_song(client, storage, video)
            message = await ctx.send('', embed=video.get_embed())
            await self._add_reaction_controls(message)
        else:
            raise commands.CommandError(
                'You need to be in a voice channel to do that.')

    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        if user != self.bot.user and message.author == self.bot.user:
            await message.remove_reaction(reaction, user)
            if message.guild and message.guild.voice_client:
                user_in_channel = user.voice and user.voice.channel and user.voice.channel == message.guild.voice_client.channel
                permissions = message.channel.permissions_for(user)
                guild = message.guild
                storage = self._get_storage(guild)
                if permissions.administrator or user_in_channel and storage.is_requester(user):
                    client = message.guild.voice_client
                    if reaction.emoji == '⏯':
                        self._pause_audio(client)
                    elif reaction.emoji == '⏭':
                        client.stop()
                    elif reaction.emoji == '⏮':
                        storage.playlist.insert(0, storage.now_playing)
                        client.stop()
                elif reaction.emoji == '⏭' and self.config.music.get('vote_skip') and user_in_channel and message.guild.voice_client and message.guild.voice_client.channel:
                    voice_channel = message.guild.voice_client.channel
                    self._vote_skip(voice_channel, user)
                    channel = message.channel
                    users_in_channel = len(
                        [member for member in voice_channel.members if not member.bot])
                    required_votes = ceil(self.config.music.get(
                        'vote_skip_ratio')*users_in_channel)
                    await channel.send(f"{user.mention} voted to skip. {required_votes} votes required.")


class State:
    def __init__(self):
        self.volume = 0.5
        self.playlist = []
        self.skip_votes = set()
        self.now_playing = None

    def is_requester(self, user): return self.now_playing.requested_by == user


def setup(bot):
    bot.add_cog(MusicCommands(bot, bot.db, config))
