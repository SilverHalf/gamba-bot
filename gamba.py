import discord
import json
from datetime import datetime
import time


class UserStats:

    def __init__(self):
        ...

class GambaBot(discord.Bot):

    def __init__(self, datafile: str):
        super().__init__()
        self._cache: dict[str, dict[str, int]] = {}
        self._load_data(datafile)

    def _load_data(self, filepath: str):
        
        with open(filepath, 'r') as file:
            transactions = file.readlines()
            for transaction in transactions:
                transaction = json.loads(transaction)
    
    def apply_transaction(self,
        user: str,
        hands: int,
        gold: int,
        ectos: int,
        runes: int):

        if not user in self._cache:
            ...


class Gamble:
    '''
    Represents the result of a gamble session.
    '''
    def __init__(self,
            user: str,
            hands:int, 
            gold:int, 
            ectos:int, 
            runes:int,
            timestamp: float | None = None):
        '''
        Creates a new gamble session object with the specified results.
        '''
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = time.time()
        self.user = user
        self.hands_played = hands
        self.gold_won = gold
        self.ectos_won = ectos
        self.runes_won = runes

    def save(self, filepath: str) -> None:
        with open(filepath, 'a') as datafile:
            datafile.write(str(self) + "\n")

    def __str__(self) -> str:
        '''Converts the Gamble data to a json string.'''
        
        data_dict = {
            'time':self.timestamp,
            'user': self.user,
            'hands_played':self.hands_played, 
            'gold_won':self.gold_won, 
            'ectos_won':self.ectos_won, 
            'runes_won':self.runes_won
        }
        return json.dumps(data_dict)


if __name__ == "__main__":
    trans1 = Gamble("silverhalf", 1, 1, 1, 1)
    trans2 = Gamble("silverhalf", 2, 2, 2, 2)
    filename = 'data.jsonl'
    trans1.save(filename)
    trans2.save(filename)