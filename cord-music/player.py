import os
import asyncio

import async_timeout
import discord
from discord.ext import commands
from wavelink import Player
from discord.ui import Button, View

from .errors import InvalidLoopMode, NotEnoughSong, NothingIsPlaying
        
class DisPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = asyncio.Queue()
        self.loop = "NONE"  # CURRENT, PLAYLIST
        self.bound_channel = None
        self.track_provider = "yt"

    async def destroy(self) -> None:
        self.queue = None
        
        await super().stop()
        await super().disconnect()

    async def do_next(self) -> None:
        if self.is_playing():
            return

        timeout = int(os.getenv("DISMUSIC_TIMEOUT", 300))
        
        try:
            with async_timeout.timeout(timeout):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            if not self.is_playing():
                await self.destroy()
            
            return

        self._source = track
        await self.play(track)
        self.client.dispatch("dismusic_track_start", self, track)
        await self.invoke_player()

    async def set_loop(self, loop_type: str) -> None:
        valid_types = ["NONE", "CURRENT", "PLAYLIST"]

        if not self.is_playing():
            raise NothingIsPlaying("Ничего не играет. Вы не можете поставить повтор.")

        if not loop_type:
            if valid_types.index(self.loop) >= 2:
                loop_type = "NONE"
            else:
                loop_type = valid_types[valid_types.index(self.loop) + 1]

            if loop_type == "PLAYLIST" and len(self.queue._queue) < 1:
                loop_type = "NONE"

        if loop_type.upper() == "PLAYLIST" and len(self.queue._queue) < 1:
            raise NotEnoughSong("Чтобы использовать повтор плейлиста вам нужно минимум 2 песни.")

        if loop_type.upper() not in valid_types:
            raise InvalidLoopMode("Тип повтора должен быть `NONE`(Никакой), `CURRENT`(Одна песня) или `PLAYLIST`(Плейлист).")

        self.loop = loop_type.upper()

        return self.loop

    async def invoke_player(self, ctx: commands.Context = None) -> None:
        track = self.source

        if not track:
            raise NothingIsPlaying("Ничего не играет.")

        embed = discord.Embed(title=track.title, url=track.uri, color=discord.Color.blurple())
        embed.set_author(name=track.author, url=track.uri, icon_url=self.client.user.display_avatar.url)
        try:
            embed.set_thumbnail(url=track.thumb)
        except AttributeError:
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/776345413132877854/940540758442795028/unknown.png"
            )
        embed.add_field(
            name="Длина",
            value=f"{int(track.length // 60)}:{int(track.length % 60)}",
        )
        embed.add_field(name="Повтор", value=self.loop)
        embed.add_field(name="Громкость", value=self.volume)
        b5 = Button(label="Повтор", emoji="🔂")
        b3 = Button(label="Пропустить", emoji="⏭")
        async def b5_callback(interaction):
                await interaction.response.send_message("**Пропущено** ⏭")
        b5.callback = b5_callback
        b4 = Button(label="Остановить", emoji="⏹")
        async def b4_callback(interaction):
                await destroy()
                await interaction.response.send_message("**Остановленно** ⏹")
        b4.callback = b4_callback
        b3 = Button(label="Пропустить", emoji="⏭")
        async def b3_callback(interaction):
                await interaction.response.send_message("**Пропущено** ⏭")
        b3.callback = b3_callback
        view = View()
        view.add_item(b5)
        view.add_item(b4)
        view.add_item(b3)
        next_song = ""

        if self.loop == "CURRENT":
            next_song = self.source.title
        else:
            if len(self.queue._queue) > 0:
                next_song = self.queue._queue[0].title

        if next_song:
            embed.add_field(name="Далее", value=next_song, inline=False)

        if not ctx:
            return await self.bound_channel.send(embed=embed, view=view)

        await ctx.respond(embed=embed, view=view)
