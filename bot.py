import discord
from gamble import Gamble
import logging
from connector import Connector
from gw2_api import API
from heapq import nlargest, nsmallest

DATA_TABLE = 'data'
GOLD_ICON = '<:gold:1284129171022286848>'
ECTO_ICON = '<:ecto:1284129080731635754>'
RUNE_ICON = '<:r_o_h:1284131395492646985>'

class GambaBot(discord.Bot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prepare_logger()
        self._dbconn = Connector()
        self._api = API()
        if not self._dbconn.check_table_exists(DATA_TABLE):
            self._dbconn.create_table(DATA_TABLE)

    def handle_gamble(self, author: discord.user.User, *values: tuple[int]) -> Gamble:
        '''Saves a gamble to the local database, and returns an appropriate message.'''

        g = Gamble(author.id, *values)
        self._dbconn.save_gamble(DATA_TABLE, g)
        return g
    
    def get_user_stats(self, author: discord.user.User) -> Gamble:
        '''Gets overall statistics for a user.'''

        g = self._dbconn.user_totals(DATA_TABLE, author.id)[0]
        return g
    
    def get_total_stats(self) -> discord.Embed:
        '''Gets overall statistics for all users.'''

        g = self._dbconn.bot_totals(DATA_TABLE)[0]
        g.user = 'placeholder'
        embed = self.create_gamble_embed(g, is_summary=True)
        embed.description = f"Gamba-Bot has registered a total of {g.hands} gambles."
        return embed

    def create_gamble_embed(self,
            g: Gamble,
            image_url: str | None = None,
            is_summary: bool = False) -> discord.Embed:

        title = "Gambling Report" if is_summary is False else "User Stats"
        description = f"<@{g.user}> gambled **{g.hands}** times."
        embed = discord.Embed(title=title, description=description)

        # Creating feedback on resources spent
        gold_spent = g.hands * 100
        ecto_spent = g.hands * 250
        embed.add_field(name="Spent:",
            value=f"{gold_spent} {GOLD_ICON}\n{ecto_spent} {ECTO_ICON}",
            inline=True)
        
        # Creating feedback on resources gained
        msg = f"{g.gold} {GOLD_ICON}\n{g.ectos} {ECTO_ICON}"
        if g.runes > 0:
            msg += f'\n{g.runes} {RUNE_ICON}'
        embed.add_field(name="Won:",
            value=msg,
            inline=True)
        
        # Creating feedback on difference
        gold_diff = g.gold - gold_spent
        ecto_diff = g.ectos - ecto_spent
        msg = f"{gold_diff} {GOLD_ICON}\n{ecto_diff} {ECTO_ICON}"
        if g.runes > 0:
            msg += f'\n{g.runes} {RUNE_ICON}'
        embed.add_field(name="Profit:",
            value=msg,
            inline=True)
        
        total, average = g.get_value(self._api)
        state = 'gain' if total >= 0 else 'loss'
        msg = f"\nFor a total **{state}** of **{round(abs(total), 2)}** {GOLD_ICON}, or {round(abs(average), 2)} {GOLD_ICON} on average, at current prices."
        embed.add_field(name='',
            value=msg,
            inline=False)
        
        if not is_summary:
            embed.set_image(url=image_url)

        return embed
    
    def create_leaderboard(self, n = 10, winners: bool = False) -> discord.Embed:
        '''
        Returns an Embed containing leaderboards for gambling stats.
        - `n` - number of positions on the leaderboard.
        - `winners` - if true, shows the top wins. Otherwise shows the top losses.
        '''

        users = self._dbconn.all_user_totals(DATA_TABLE)
        title = f"{'Winners' if winners else 'Losers'} Leaderboard"
        embed = discord.Embed(title=title)

        n = min(n, len(users))
        fun = nlargest if winners else nsmallest
        top_total   = fun(n, users, key=lambda x: x.get_value(self._api)[0])
        top_average = fun(n, users, key=lambda x: x.get_value(self._api)[1])

        totals_lb: list[str] = []
        for i in range(n):
            userdata = top_total[i]
            value = userdata._value[0]
            row = f"{i+1}. <@{userdata.user}> {'won' if value > 0 else 'lost'} **{abs(value)}** {GOLD_ICON} total over {userdata.hands} gambles."
            totals_lb.append(row)

        average_lb: list[str] = []
        for i in range(n):
            userdata = top_average[i]
            value = userdata._value[1]
            row = f"{i+1}. <@{userdata.user}> {'won' if value > 0 else 'lost'} **{abs(value)}** {GOLD_ICON} on average over {userdata.hands} gambles."
            average_lb.append(row)

        embed.add_field(
            name=f"Biggest {'Winners' if winners else 'Losers'}",
            value="\n".join(totals_lb),
            inline=False
        )
        embed.add_field(
            name=f"{'Luckiest' if winners else 'Unluckiest'} Gamblers",
            value="\n".join(average_lb),
            inline=False
        )

        return embed        

    def _prepare_logger(self):
        '''Prepares a logger for the bot.'''

        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)
        self._logger = logger

class GambaModal(discord.ui.Modal):
    '''Modal for the form that users input their results into.'''

    def __init__(self, bot: GambaBot, proof_url: str, *args, **kwargs) -> None:
        '''Generates a new input form.'''

        super().__init__(*args, **kwargs)
        self._create_inputs()
        self.bot = bot
        self.img_url = proof_url

    def _create_inputs(self):

        self.add_item(discord.ui.InputText(
            label="Hands",
            style=discord.InputTextStyle.short,
            placeholder="How many times did you gamble?"))
        self.add_item(discord.ui.InputText(
            label="Gold",
            style=discord.InputTextStyle.short,
            placeholder="How much gold did you win?"))
        self.add_item(discord.ui.InputText(
            label="Ectos",
            style=discord.InputTextStyle.short,
            placeholder="How many Globs of Ectoplasm has you win>"))
        self.add_item(discord.ui.InputText(
            label="Runes",
            style=discord.InputTextStyle.short,
            placeholder="How many Supreme Runes of Holding did you win?",))
    
    @property
    def values(self) -> tuple[int] | None:
        '''
        Returns a tuple containing the hands, gold, ectos and runes submitted via
        the modal. If any of the submitted values is not convertable to an integer,
        then retruns None.'''

        try:
            hands = int(self.children[0].value)
            gold = int(self.children[1].value)
            ectos = int(self.children[2].value)
            runes = int(self.children[3].value)

            return hands, gold, ectos, runes
        except ValueError:
            return None

    async def callback(self, interaction: discord.Interaction):
        '''This function is called when the form is submitted.'''

        values = self.values
        if values is None:
            await interaction.response.send_message("Invalid content. Fields must be integers.")
            return
        g = self.bot.handle_gamble(interaction.user, *self.values)
        embed = self.bot.create_gamble_embed(g, image_url=self.img_url)
        await interaction.response.send_message(embed=embed)
