import discord.types
from bot import GambaBot, GambaModal
import discord
import dotenv

try:
    CONFIG = dotenv.dotenv_values()
    bot_token = CONFIG["BOT_TOKEN"]
except KeyError:
    raise RuntimeError("No bot token is set in the enviroment.")

bot = GambaBot()
gamba = bot.create_group("gamba", "Send and receive gamble statistics from GambaBot")

@gamba.command(description="Submits a new gamble to GambaBot.")
async def record(ctx: discord.ApplicationContext, proof_image: discord.message.Attachment):
    """Submits a new gamble to GambaBot."""
    
    await ctx.send_modal(GambaModal(bot, proof_image.url, title="Gambling Results"))

@gamba.command(description="Gets your overall gamba statistics")
async def stats(ctx: discord.ApplicationContext):
    author = ctx.author
    g = bot.get_user_stats(author)
    embed = bot.create_gamble_embed(g, author, is_summary=True)
    await ctx.respond(embed=embed)

bot.run(bot_token)
