'''
Tiny module for handling requests from the GW2 API.
The size of this module means I could probably include it as a function
in `bot` or something, but I prefer leaving it separate in case I
decide to add more functionality or make my life harder for some
reason.
'''

import requests
from enum import Enum

PRICE_URL = f"https://api.guildwars2.com/v2/commerce/prices/"

class Item(Enum):
    '''Stores the API IDs of various items as integer values.'''
    ectoplasm = 19721
    rune = 83410

def get_item_value(item: Item) -> float:
    '''
    Gets the value of an item from the Guild Wars 2 API.
    Returns the minmum sell value on the trading post, in gold.
    '''

    api_url = PRICE_URL + str(item.value)
    data = requests.get(api_url)
    return data.json()['sells']['unit_price']/10000