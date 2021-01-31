import requests

from config import GCYB_SUPPLY, GRAPHQL_API, HEADERS, QUERY


def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post(GRAPHQL_API, json={'query': query}, headers=HEADERS)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def get_eth_gcyb_price():
    resp = run_query(QUERY)
    return resp['data']['market_data'][0]['current_price']


def get_eth_atom_price():
    sell = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd").json()['ethereum']['usd']
    buy = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=cosmos&vs_currencies=usd").json()['cosmos']['usd']
    return  sell / buy


def get_data():
    return requests.get('https://api.coingecko.com/api/v3/coins/ethereum').json()


def get_cyb_market_data():
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
    eth_gcyb_price = get_eth_gcyb_price()
    eth_atom_price = get_eth_atom_price()
    return {
        "current_price": {
            "usd": resp['market_data']["current_price"]['usd'] * eth_gcyb_price,
            "btc": resp['market_data']["current_price"]['btc'] * eth_gcyb_price,
            "eth": eth_gcyb_price,
            "atom": eth_gcyb_price * eth_atom_price
        }
    }


def get_market_cap(current_price):
    return {
        "market_cap": {
            "usd": current_price["usd"] * GCYB_SUPPLY,
            "btc": current_price["btc"] * GCYB_SUPPLY,
            "eth": current_price["eth"] * GCYB_SUPPLY,
            "atom": current_price["atom"] * GCYB_SUPPLY
        }
    }