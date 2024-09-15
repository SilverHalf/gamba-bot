'''
This module defines the general data structure and behaviour for Gambles.
'''

import time
import json
from gw2_api import API, ItemType
import logging
import sys

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
        self._value: tuple[float] | None = None

    def get_value(self, api: API) -> tuple[float]:
        '''Net total and average value of the gamble.'''

        if self._value is not None:
            return self._value

        ecto_value = api.get_item_value(ItemType.ectoplasm)
        rune_value = api.get_item_value(ItemType.rune)

        spent = self.hands*(100 + 250 * ecto_value)
        gained = self.gold + self.ectos * ecto_value + self.runes * rune_value
        value = gained - spent

        self._value = (round(value, 2), round(value/self.hands, 2))
        return self._value

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
    logger = logging.Logger('testLogger', logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    api = API(logger)
    g = Gamble('silver', 1, 25, 300, 0)
    print(g.get_value(api))