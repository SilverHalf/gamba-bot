'''
This module defines the general data structure and behaviour for Gambles.
'''

import time
import json
from gw2_api import get_item_value, Item

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
        Creates a new gamble session object with the given data.

        - `user` - username of the gambler
        - `hands` - number of gambles done by the user in the session.
        - `gold` - gross total raw gold gained during the session.
        - `ectos` - gross total ectos gained during the session.
        - `runes` - total number of superior runes of holding won.
        - `timestamp` - float, number of seconds in unix time.
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

    @property
    def value(self):
        '''Net total and average value of the gamble.'''

        ecto_value = get_item_value(Item.ectoplasm)
        rune_value = get_item_value(Item.rune)

        spent = self.hands*(100 + 250 * ecto_value)
        gained = self.gold + self.ectos * ecto_value + self.runes * rune_value
        value = gained - spent

        return value, value/self.hands

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

if __name__ == "__main__":
    g = Gamble('silver', 2, 200, 650, 1)
    print(g.value)