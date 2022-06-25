from discord.ext.commands.errors import CheckFailure


class NotConnectedToVoice(CheckFailure):
    """Пользователь не подключен к голосовому каналу"""

    pass


class PlayerNotConnected(CheckFailure):
    """Бот не подключен"""

    pass


class MustBeSameChannel(CheckFailure):
    """Пользователь и бот не в одном канале"""

    pass


class NothingIsPlaying(CheckFailure):
    """Ничего не играет"""

    pass


class NotEnoughSong(CheckFailure):
    """Недостатачно треков в очереди"""

    pass


class InvalidLoopMode(CheckFailure):
    """Неизвестный режим повтора"""

    pass
