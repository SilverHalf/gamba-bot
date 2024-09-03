from bot import GambaBot
import dotenv

try:
    CONFIG = dotenv.dotenv_values()
    bot_token = CONFIG["BOT_TOKEN"]
except KeyError:
    raise RuntimeError("No bot token is set in the enviroment.")

bot = GambaBot()

bot.run(bot_token)
