from gamba import GambaBot
import dotenv
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

try:
    CONFIG = dotenv.dotenv_values()
    bot_token = CONFIG["BOT_TOKEN"]
except KeyError:
    raise RuntimeError("No bot token is set in the enviroment.")

bot = GambaBot()

bot.run(bot_token)
