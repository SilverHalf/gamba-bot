import time
import json
from typing import Self

class Gamble:
    '''
    Represents the result of a gamble session.
    '''
    def __init__(self,
            user: str,
            hands: int = 0, 
            gold: int = 0, 
            ectos: int = 0,
            runes: int = 0,
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