import requests

from uniswap import Uniswap
from config import PROVIDER


address = "0x0000000000000000000000000000000000000000"
private_key = None
uniswap_wrapper = Uniswap(address, private_key, version=2, provider=PROVIDER)  # pass version=2 to use Uniswap v2
eth = "0x0000000000000000000000000000000000000000"
gol = "0xF4ecdBa8ba4144Ff3a2d8792Cad9051431Aa4F64"

ETH_GGOL_PRICE = uniswap_wrapper.get_eth_token_output_price(gol, 1) / (1*10**18)
GGOL_SUPPLY = 14_406_844_988_437 / 10**9

def get_data():
    return requests.get('https://api.coingecko.com/api/v3/coins/ethereum').json()


def get_gol_market_data():
    resp = get_data()
    current_price = get_current_price(resp)['current_price']
    market_cap = get_market_cap(current_price)['market_cap']
    return {
        "market_data": {
            "current_price": current_price,
            "market_cap": market_cap,
            "market_cap_rank": None,
            "price_change_percentage_24h": None,
            "price_change_percentage_7d": None,
            "price_change_percentage_30d": None
        }
    }

def get_current_price(resp):
    mult = ETH_GGOL_PRICE * 10**9
    return {
        "current_price": {
            "usd": resp['market_data']["current_price"]['usd'] * mult,
            "btc": resp['market_data']["current_price"]['btc'] * mult,
            # "atom": resp['market_data']["current_price"]['atom'] * ETH_GGOL_PRICE,
            "eth": mult
        }
    }

def get_market_cap(current_price):
    return {
        "market_cap": {
            "usd": current_price["usd"] * GGOL_SUPPLY,
            "btc": current_price["btc"] * GGOL_SUPPLY,
            # "atom": current_price["atom"] * GGOL_SUPPLY,
            "eth": current_price["eth"] * GGOL_SUPPLY
        }
    }