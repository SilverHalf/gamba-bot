import discord
from gamble import Gamble
import logging

class GambaBot(discord.Bot):

    def __init__(self, datafile: str):
        super().__init__()
        self._prepare_logger()
        self._cache: dict[str, Gamble] = {}
        self._load_data(datafile)

    def _prepare_logger(self):
        '''Prepares a logger for the bot.'''

        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)
        self._logger = logger

    def _load_data(self, filepath: str):
        '''Build's the bot's cache from the transaction log.'''
        
        self._logger.log(logging.INFO, f"Loading data from {filepath}")
        with open(filepath, 'r') as file:
            transactions = file.readlines()
            for transaction in transactions:
                gamble = Gamble.from_transaction(transaction)
                self._apply_gamble(gamble)
    
    def _apply_gamble(self, gamble: Gamble):
        '''Applies a gamble's values to the internal cache.'''

        if not gamble.user in self._cache.keys():
            self._cache[gamble.user] = gamble
        else:
            self._cache[gamble.user] += gamble


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