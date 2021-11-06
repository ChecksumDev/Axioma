from nextcord.embeds import Embed
from youtube_dl import YoutubeDL
YTDL_OPTS = {
    "default_search": "ytsearch",
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    "extract_flat": "in_playlist"
}


class Downloader:
    def __init__(self, url_or_search, requested_by):
        """Plays audio from (or searches for) a URL."""
        with YoutubeDL(YTDL_OPTS) as ydl:
            self.video = self._get_info(url_or_search)
            video_format = self.video["formats"][0]
            self.stream_url = video_format["url"]
            self.video_url = self.video["webpage_url"]
            self.title = self.video["title"]
            self.uploader = self.video["uploader"] if "uploader" in self.video else ""
            self.thumbnail = self.video[
                "thumbnail"] if "thumbnail" in self.video else None
            self.requested_by = requested_by

    def _get_info(self, video_url):
        with YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            self.video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]["url"])  # get info for first self.video
            else:
                self.video = info
            return self.video

    def get_embed(self):
        embed = Embed(
            title=self.title, description=self.uploader, url=self.video_url, color=0x800080)
        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.display_avatar.url)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed
