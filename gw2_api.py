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
import json
import os

PRICE_URL = "https://api.guildwars2.com/v2/commerce/prices/"
API_LOGGER = logging.Logger('API', logging.DEBUG)
API_LOGGER.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
API_LOGGER.addHandler(handler)
API_CACHE_FILE = 'api-cache.json'
API_CACHE_TIME_MINUTES = 30

class ItemType(Enum):
    '''Stores the API IDs of various items as integer values.'''
    ectoplasm = 19721
    rune = 83410

class ItemValue:
    '''Contains the value and last update time of an item.'''

    def __init__(self, item: ItemType, price: int | None = None, cache_timeout: int = 0):
        '''
        Creates a new ItemData instance.
        - `price` - price in coppers, as given by the api.
        - `timestamp` - float, unix time in seconds. Leave empty to use the current time.
        '''

        self._timestamp: float = 0
        self._cache_timeout = cache_timeout
        self._price = price
        self._item = item

    @property
    def get_value(self) -> tuple[float, bool]:
        '''
        Returns two values. The first the value of the item in gold.
        This value is cached by default; if the cache was updated, returns a true second value.
        Otherwise returns a false second value.
        '''
        updated = False
        if time.time() - self._timestamp > self._cache_timeout:
            try:
                self._update_value_from_api()
                updated = True
            except Exception as e:
                API_LOGGER.warning(f"Could not update price of {self._item.name} from API due to the following issue:\n{e}\nUsing cached value.")
        return self._price/10000, updated

    def _update_value_from_api(self):
        api_url = PRICE_URL + str(self._item.value)
        API_LOGGER.debug(f'Getting data from {api_url}')
        response = requests.get(api_url)
        response.raise_for_status()
        self._price = response.json()['sells']['unit_price']
        self._timestamp = time.time()

class API:
    '''Manages the bot's requests to the GW2 API.'''

    def __init__(self, logger: logging.Logger = API_LOGGER, cache_minutes: int = API_CACHE_TIME_MINUTES):
        '''
        Creates a new API link.
        - `cache_minutes` - time that the price of an
        item will be cached before re-querying the API.
        '''

        self._timeout = cache_minutes * 60
        self._cache: dict[ItemType, ItemValue] = self._load_cache_from_file()
        self._logger = logger
    
    def _load_cache_from_file(self) -> dict[ItemType, ItemValue]:
        '''
        Loads the API cache from a json file.
        '''
        cache: dict[ItemType, ItemValue] = {}
        if not os.path.exists(API_CACHE_FILE):
            return cache
        with open(API_CACHE_FILE, 'r') as cache_file:
            try:
                saved_data: dict[str, int] = json.load(cache_file)

                for item_name, cached_price in saved_data.items():
                    item_type = ItemType[item_name]
                    cache[item_type] = ItemValue(item_type, cached_price, self._timeout)

                return cache
            
            except Exception as e:
                API_LOGGER.warning(f"Could not load API cache from file: {e}")
                return {}
    
    def _save_cache_to_file(self):
        '''
        Saves the API cache to a json file.
        '''
        saved_data: dict[str, int] = {}
        for item, value in self._cache.items():
            saved_data[item.name] = value._price

        with open(API_CACHE_FILE, 'w') as cachefile:
            json.dump(saved_data, cachefile)

    def get_item_value(self, item: ItemType) -> float:
        '''
        Gets the value of an item from the Guild Wars 2 API.
        Returns the minimum sell value on the trading post, in gold.
        '''

        if item not in self._cache:
            self._cache[item] = ItemValue(item, cache_timeout=self._timeout)
        value, updated = self._cache[item].get_value
        if updated:
            self._save_cache_to_file()
        return value
    
if __name__ == '__main__':
    API_LOGGER.removeHandler(handler)
    API_LOGGER.addHandler(logging.StreamHandler(sys.stdout))
    api = API()
    print(api.get_item_value(ItemType.ectoplasm))
    print(api.get_item_value(ItemType.rune))