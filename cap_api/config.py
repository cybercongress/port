import os

HASURA_GRAPHQL_ADMIN_SECRET = os.environ.get("HASURA_GRAPHQL_ADMIN_SECRET")

PROVIDER = os.environ.get("ETH_NODE_RPC")
GCYB_SUPPLY = 1_000_000
HASURA_HOST = os.environ.get("HASURA_HOST", "0.0.0.0")
HASURA_PORT = os.environ.get("HASURA_PORT", '5000')

GRAPHQL_API = f'http://{HASURA_HOST}:{HASURA_PORT}/v1/graphql'
HEADERS = {
    'content-type': 'application/json',
    "x-hasura-admin-secret": HASURA_GRAPHQL_ADMIN_SECRET
  }

QUERY = '''{
  market_data {
    current_price
  }
}'''

QUERY_DAY = '''{
  day_price {
    day
  }
}'''

QUERY_WEEK = '''{
  week_price {
    week
  }
}'''

QUERY_MONTH = '''{
  month_price {
    month
  }
}'''