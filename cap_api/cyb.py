import requests

from config import GCYB_SUPPLY, GRAPHQL_API, HEADERS, QUERY, QUERY_DAY, QUERY_WEEK, QUERY_MONTH


def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post(GRAPHQL_API, json={'query': query}, headers=HEADERS)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def get_eth_gcyb_price():
    current_price = run_query(QUERY)['data']['market_data'][0]['current_price']
    day_price = run_query(QUERY_DAY)['data']['day_price'][0]['day']
    week_price = run_query(QUERY_WEEK)['data']['week_price'][0]['week']
    month_price = run_query(QUERY_MONTH)['data']['month_price'][0]['month']
    return current_price, day_price, week_price, month_price


def get_eth_atom_price():
    sell = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd").json()['ethereum']['usd']
    buy = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=cosmos&vs_currencies=usd").json()['cosmos']['usd']
    return sell / buy


def get_data():
    return requests.get('https://api.coingecko.com/api/v3/coins/ethereum').json()


def get_cyb_market_data():
    resp = get_data()
    current_price = get_current_price(resp)
    market_cap = get_market_cap(current_price[0])['market_cap']
    return {
        "market_data": {
            "current_price": current_price[0]['current_price'],
            "market_cap": market_cap,
            "market_cap_rank": None,
            "price_change_percentage_24h": current_price[1][0],
            "price_change_percentage_7d": current_price[1][1],
            "price_change_percentage_30d": current_price[1][2]
        }
    }


def get_current_price(resp):
    changes_keys = ['price_change_percentage_24h',
                    'price_change_percentage_7d',
                    'price_change_percentage_30d']
    eth_gcyb_price = get_eth_gcyb_price()
    eth_atom_price = get_eth_atom_price()
    changes = [calculate_change(resp, eth_gcyb_price[0], x, k) for x, k in list(zip(eth_gcyb_price[1:], changes_keys))]
    return {
        "current_price": {
            "usd": resp['market_data']["current_price"]['usd'] * eth_gcyb_price[0],
            "btc": resp['market_data']["current_price"]['btc'] * eth_gcyb_price[0],
            "eth": eth_gcyb_price[0],
            "atom": eth_gcyb_price[0] * eth_atom_price
        }
    }, changes


def calculate_change(resp, current, was, vs_change):
    eth_ch = (resp['market_data'][vs_change] / 100) + 1
    print(eth_ch)
    cyb_ch = current/was
    print(cyb_ch)
    arbitrage = (eth_ch * cyb_ch - 1) * 100
    return arbitrage



def get_market_cap(current_price):
    current_price = current_price['current_price']
    return {
        "market_cap": {
            "usd": current_price["usd"] * GCYB_SUPPLY,
            "btc": current_price["btc"] * GCYB_SUPPLY,
            "eth": current_price["eth"] * GCYB_SUPPLY,
            "atom": current_price["atom"] * GCYB_SUPPLY
        }
    }
