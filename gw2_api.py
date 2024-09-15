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

class ItemType(Enum):
    '''Stores the API IDs of various items as integer values.'''
    ectoplasm = 19721
    rune = 83410

class ItemValue:
    '''Contains the value and last update time of an item.'''

    def __init__(self, price: int = 0, timestamp: float | None = None):
        '''
        Creates a new ItemData instance.
        - `price` - price in coppers, as given by the api.
        - `timestamp` - float, unix time in seconds. Leave empty to use the current time.
        '''

        if timestamp is None:
            timestamp = time.time()
        self._timestamp = timestamp
        self._price = price

    def update_price(self, price: int):
        '''Updates the price of the item.'''
        
        self._price = price
        self._timestamp = time.time()

    @property
    def value(self):
        '''Returns the value in copper.'''
        return self._price
    
    @property
    def timestamp(self):
        '''Gets the timestamp of the current value.'''
        return self._timestamp

class API:
    '''Manages the bot's requests to the GW2 API.'''

    def __init__(self, logger: logging.Logger = None, cache_minutes: int = 30):
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
        Returns the minmum sell value on the trading post, in gold
        rounded to two decimals.
        '''

        if item in self._cache:
            value = self._cache[item]
            self._logger.debug(f"Found cached item for '{item.name}'")
        else:
            value = ItemValue(timestamp=0)
            self._logger.debug(f"Creating cached item for '{item.name}'")
        
        if time.time() - value.timestamp > self._timeout:
            self._logger.debug(f"Updating cached price for '{item.name}'")
            price = self._get_value_from_api(item)
            value.update_price(price)
            self._cache[item] = value

        self._logger.debug(f"'{item.name}' is currently worth {value.value} units")
        return value.value
    
    def _get_value_from_api(self, itemtype: ItemType):
        api_url = PRICE_URL + str(itemtype.value)
        self._logger.debug(f"Getting data from endpoint: {api_url}")
        data = requests.get(api_url)
        return data.json()['sells']['unit_price']
    
if __name__ == '__main__':
    logger = logging.Logger('testLogger', logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    api = API(logger=logger)
    api.get_item_value(ItemType.ectoplasm)
    time.sleep(1)
    api.get_item_value(ItemType.ectoplasm)