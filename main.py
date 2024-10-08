import discord.types
from bot import GambaBot, GambaModal, DATA_TABLE, GOLD_ICON
from gamble import Gamble
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

@gamba.command(description="Gets your overall statistics.")
async def stats(ctx: discord.ApplicationContext):
    author = ctx.author
    g = bot.get_user_stats(author)
    embed = bot.create_gamble_embed(g, author, is_summary=True)
    user_recent = bot._dbconn.recent_by_user(DATA_TABLE, author.id, 5)
    def func(g: Gamble) -> str:
        value = g.get_value(bot._api)
        state = 'winning' if value[0] > 0 else 'losing'
        plural = '' if g.hands == 1 else 's'
        return f'<t:{int(g.timestamp)}> - gambled {g.hands} time{plural}, {state} a total of {value[0]} {GOLD_ICON}'
    embed = bot._add_list_of_gambles(embed, user_recent, 'Recent activity:', func)
    await ctx.respond(embed=embed)

@gamba.command(description="Gets the leaderboard for top winners.")
async def winners(ctx: discord.ApplicationContext):
    embed = bot.create_leaderboard(n = 5, winners=True)
    await ctx.respond(embed=embed)

@gamba.command(description="Gets the leaderboard for top losers.")
async def losers(ctx: discord.ApplicationContext):
    embed = bot.create_leaderboard(n = 5, winners=False)
    await ctx.respond(embed=embed)

@gamba.command(description="Gets total stats for Gamba-Bot.")
async def total(ctx: discord.ApplicationContext):
    embed = bot.get_total_stats()
    await ctx.respond(embed=embed)

@gamba.command(description="Deletes your most recent gamble.")
async def delete(ctx: discord.ApplicationContext):
    bot.delete_gamble(ctx.author)
    await ctx.respond(f"<@{ctx.author.id}>'s most recent entry has been deleted.")

bot.run(bot_token)
