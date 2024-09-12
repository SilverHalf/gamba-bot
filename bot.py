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

    def handle_gamble(self, author: discord.user.User, *values: tuple[int]):
        '''Saves a gamble to the local database, and returns an appropriate message.'''

        g = Gamble(author.name, *values)
        self._dbconn.save_gamble(DATA_TABLE, g)
        gold = round(g.gold, 2)
        ectos = round(g.ectos, 2)
        runes = round(g.runes, 2)

        userid = author.id
        msg = f"<@{userid}> gambled {g.hands} times, winning {gold}💰, {ectos}🔮, and {runes}🀄."
        total, average = g.value
        state = 'won' if total >= 0 else 'lost'
        msg += f"\nIn total, they {state} **{round(abs(total), 2)}**💰, or {round(abs(average), 2)} on average."

        return msg
    
    def get_user_stats(self, author: discord.user.User):
        '''Gets overall statistics for a user, and returns a formatted message.'''

        g = self._dbconn.user_totals(DATA_TABLE, author.name)[0]
        userid = author.id
        gold = round(g.gold, 2)
        ectos = round(g.ectos, 2)
        runes = round(g.runes, 2)
        msg = f"<@{userid}> has gambled a total of {g.hands} times, winning {gold}💰, {ectos}🔮, and {runes}🀄."
        total, average = g.value
        state = 'won' if total >= 0 else 'lost'
        msg += f"\nOverall, they {state} **{round(abs(total), 2)}**💰, or {round(abs(average), 2)} on average."

        return msg

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
            placeholder="How many Globs of Ectoplasm did you win>"))
        self.add_item(discord.ui.InputText(
            label="Runes",
            style=discord.InputTextStyle.short,
            placeholder="How many Runes of Holding did you win?",
            value='0'))
    
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
        msg = self.bot.handle_gamble(interaction.user, *self.values)
        msg += f"\n{self.img_url}"
        await interaction.response.send_message(msg)