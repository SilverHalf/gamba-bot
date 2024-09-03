import time
import json
from typing import Self

class Gamble:
    '''
    Represents the result of a gamble session.
    '''
    def __init__(self,
            user: str,
            hands: int, 
            gold: int, 
            ectos: int, 
            runes: int,
            timestamp: float | None = None):
        '''
        Creates a new gamble session object with the specified results.
        '''
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = time.time()
        self.user = user
        self.hands = hands
        self.gold = gold
        self.ectos = ectos
        self.runes = runes

    @classmethod
    def from_transaction(cls, json_str: dict[str, int | str]):
        '''Creates a Gamble object from a json string.'''

        dictionary = json.loads(json_str)

        return cls(
            dictionary['user'],
            dictionary['hands'],
            dictionary['gold'],
            dictionary['ectos'],
            dictionary['runes'],
            dictionary['timestamp']
        )

    def save(self, filepath: str) -> None:
        with open(filepath, 'a') as datafile:
            datafile.write(str(self) + "\n")

    def __iadd__(self, other: Self):
        
        self.hands += other.hands
        self.gold += other.gold
        self.ectos += other.ectos
        self.runes += other.runes

        if other.timestamp > self.timestamp:
            self.timestamp = other.timestamp

        return self

    def __str__(self) -> str:
        '''Converts the Gamble data to a json string.'''
        
        data_dict = {
            'timestamp':self.timestamp,
            'user': self.user,
            'hands':self.hands, 
            'gold':self.gold, 
            'ectos':self.ectos, 
            'runes':self.runes
        }
        return json.dumps(data_dict)