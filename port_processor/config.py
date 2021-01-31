import json
import os

# ---------------------------------------------------------------------------
# DATABASE CONFIG

POSTGRES_DB = os.environ.get("POSTGRES_DB", "PORT")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "cyber")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", '127.0.0.1')
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", '5432')
HASURA_GRAPHQL_ADMIN_SECRET = os.environ.get("HASURA_GRAPHQL_ADMIN_SECRET")
HASURA_HOST = os.environ.get("HASURA_HOST", "0.0.0.0")
HASURA_PORT = os.environ.get("HASURA_PORT", '5000')
HASURA_WS = f'ws://{HASURA_HOST}:{HASURA_PORT}/v1/graphql'
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# ETHEREUM NODE CONFIG
START_BLOCK = int(os.environ.get("START_BLOCK"))
ETH_NODE_WSS = os.environ.get("ETH_NODE_WSS")
ETH_NODE_RPC = os.environ.get("ETH_NODE_RPC")
RECEIVER = os.environ.get("RECEIVER").lower()
RECEIVER = RECEIVER.lower()
QUERY = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_subscribe",
        "params": ["newHeads"]
})
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# CYBER CONFIG
LCD_API = os.environ.get("LCD_API")
SENDER = os.environ.get("SENDER")
# ---------------------------------------------------------------------------

TIME_SLEEP = 10
