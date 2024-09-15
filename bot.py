import discord
from gamble import Gamble
import logging
from connector import Connector
from gw2_api import API

DATA_TABLE = 'data'
GOLD_ICON = '<:gold:1284129171022286848>'
ECTO_ICON = '<:ecto:1284129080731635754>'
RUNE_ICON = '<:r_o_h:1284131395492646985>'

class GambaBot(discord.Bot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prepare_logger()
        self._dbconn = Connector()
        self._api = API(logger=self._logger)
        if not self._dbconn.check_table_exists(DATA_TABLE):
            self._dbconn.create_table(DATA_TABLE)

    def handle_gamble(self, author: discord.user.User, *values: tuple[int]) -> Gamble:
        '''Saves a gamble to the local database, and returns an appropriate message.'''

        g = Gamble(author.name, *values)
        self._dbconn.save_gamble(DATA_TABLE, g)
        return g
    
    def get_user_stats(self, author: discord.user.User) -> Gamble:
        '''Gets overall statistics for a user, and returns a formatted message.'''

        g = self._dbconn.user_totals(DATA_TABLE, author.name)[0]
        return g

    def create_gamble_embed(self,
            g: Gamble,
            author: discord.User,
            image_url: str | None = None,
            is_summary: bool = False) -> discord.Embed:

        title = "Gambling Report" if is_summary is False else "User Stats"
        description = f"<@{author.id}> gambled **{g.hands}** times, with the following results."
        embed = discord.Embed(title=title, description=description)

        # Creating feedback on resources spent
        gold_spent = g.hands * 100
        ecto_spent = g.hands * 250
        embed.add_field(name="Total Spent:",
            value=f"{gold_spent} {GOLD_ICON}\n{ecto_spent} {ECTO_ICON}",
            inline=True)
        
        # Creating feedback on resources gained
        msg = f"{g.gold} {GOLD_ICON}\n{g.ectos} {ECTO_ICON}"
        if g.runes > 0:
            msg += f'\n{g.runes} {RUNE_ICON}'
        embed.add_field(name="Total Won:",
            value=msg,
            inline=True)
        
        # Creating feedback on difference
        gold_diff = g.gold - gold_spent
        ecto_diff = g.ectos - ecto_spent
        msg = f"{gold_diff} {GOLD_ICON}\n{ecto_diff} {ECTO_ICON}"
        if g.runes > 0:
            msg += f'\n{g.runes} {RUNE_ICON}'
        embed.add_field(name="Net winnings:",
            value=msg,
            inline=True)
        
        total, average = g.get_value(self._api)
        state = 'gained' if total >= 0 else 'lost'
        msg = f"\nOverall, they {state} **{round(abs(total), 2)}** {GOLD_ICON}, or {round(abs(average), 2)} {GOLD_ICON} on average."
        embed.add_field(name='',
            value=msg,
            inline=False)
        
        if not is_summary:
            embed.set_image(url=image_url)

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
        embed = self.bot.create_gamble_embed(g, interaction.user, image_url=self.img_url)
        await interaction.response.send_message(embed=embed)