'''
Tiny module for handling requests from the GW2 API.
The size of this module means I could probably include it as a function
in `bot` or something, but I prefer leaving it separate in case I
decide to add more functionality or make my life harder for some
reason.
'''

import requests
from enum import Enum
import time
import logging
import sys

PRICE_URL = f"https://api.guildwars2.com/v2/commerce/prices/"
API_LOGGER = logging.Logger('API', logging.DEBUG)
API_LOGGER.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
API_LOGGER.addHandler(handler)

class ItemType(Enum):
    '''Stores the API IDs of various items as integer values.'''
    ectoplasm = 19721
    rune = 83410

class ItemValue:
    '''Contains the value and last update time of an item.'''

    def __init__(self, item: ItemType, cache_timeout: int = 0):
        '''
        Creates a new ItemData instance.
        - `price` - price in coppers, as given by the api.
        - `timestamp` - float, unix time in seconds. Leave empty to use the current time.
        '''

        self._timestamp: float = 0
        self._cache_timeout = cache_timeout
        self._price: int | None = None
        self._item = item

    @property
    def value(self) -> float:
        '''Gets the value of the item in gold.'''
        
        if time.time() - self._timestamp > self._cache_timeout:
            self._update_value_from_api()
        return self._price/10000

    def _update_value_from_api(self):
        api_url = PRICE_URL + str(self._item.value)
        API_LOGGER.debug(f'Getting data from {api_url}')
        data = requests.get(api_url)
        self._price = data.json()['sells']['unit_price']
        self._timestamp = time.time()

class API:
    '''Manages the bot's requests to the GW2 API.'''

    def __init__(self, logger: logging.Logger = API_LOGGER, cache_minutes: int = 30):
        '''
        Creates a new API link.
        - `cache_minutes` - time that the price of an
        item will be cached before re-querying the API.
        '''

        self._timeout = cache_minutes * 60
        self._cache: dict[ItemType, ItemValue] = {}
        self._logger = logger

    def get_item_value(self, item: ItemType) -> float:
        '''
        Gets the value of an item from the Guild Wars 2 API.
        Returns the minmum sell value on the trading post, in gold.
        '''

        if not item in self._cache:
            self._cache[item] = ItemValue(item, cache_timeout=self._timeout)
        return self._cache[item].value
    
if __name__ == '__main__':
    API_LOGGER.removeHandler(handler)
    API_LOGGER.addHandler(logging.StreamHandler(sys.stdout))
    api = API()
    print(api.get_item_value(ItemType.ectoplasm))
    time.sleep(1)
    print(api.get_item_value(ItemType.ectoplasm))