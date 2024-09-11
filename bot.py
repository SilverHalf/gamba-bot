import discord
from gamble import Gamble
import logging
from connector import Connector

DATA_TABLE = 'data'

class GambaBot(discord.Bot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prepare_logger()
        self._dbconn = Connector()
        if not self._dbconn.check_table_exists(DATA_TABLE):
            self._dbconn.create_table(DATA_TABLE)

    def handle_gamble(self, *args):

        gamble = Gamble(*args)
        self._dbconn.save_gamble(DATA_TABLE, gamble)
        

    def _prepare_logger(self):
        '''Prepares a logger for the bot.'''

        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)
        self._logger = logger


if __name__ == "__main__":
    filename = 'data.jsonl'
    gamble = Gamble("SILVER", 1, 1, 1, 1)
    gamble.save(filename)
    gamble = Gamble("SILVER2", 1, 1, 1, 1)
    gamble.save(filename)
    gamble = Gamble("SILVER", 2, 2, 2, 2)
    gamble.save(filename)
    gamble = Gamble("SILVER2", 2, 2, 2, 2)
    gamble.save(filename)
    bot = GambaBot(filename)
    for player in bot._cache:
        print(bot._cache[player])