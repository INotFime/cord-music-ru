from discord.ext import commands

from .errors import MustBeSameChannel, NotConnectedToVoice, PlayerNotConnected


def voice_connected():
    def predicate(ctx: commands.Context):
        if not ctx.author.voice:
            raise NotConnectedToVoice("Вы не находитесь в голосовом канале.")

        return True

    return commands.check(predicate)


def player_connected():
    def predicate(ctx: commands.Context):
        if not ctx.voice_client:
            raise PlayerNotConnected("Бот не находится в голосовом канале.")

        return True

    return commands.check(predicate)


def in_same_channel():
    def predicate(ctx: commands.Context):
        if not ctx.voice_client:
            raise PlayerNotConnected("Бот не находится в голосовом канале.")

        if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            raise MustBeSameChannel("Вы должны быть в одном голосовом канале с ботом.")

        return True

    return commands.check(predicate)


def voice_channel_player():
    def predicate(ctx: commands.Context):
        if not ctx.author.voice:
            raise NotConnectedToVoice("Вы не находитесь в голосовом канале.")

        if not ctx.voice_client:
            raise PlayerNotConnected("Бот не находится в голосовом канале.")

        if ctx.voice_client.channel.id != ctx.author.voice.channel.id:
            raise MustBeSameChannel("Вы должны находится в одном канале с ботом.")

        return True

    return commands.check(predicate)
