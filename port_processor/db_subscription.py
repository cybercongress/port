import websockets
import json


from config import HASURA_GRAPHQL_ADMIN_SECRET, HASURA_WS
from db import get_missed_blocks_list
from eth import sync


async def init(websocket):
    json_init = json.dumps({
        "type": "connection_init",
        "payload": {
            "headers": {
                "content-type": "application/json",
                "x-hasura-admin-secret": HASURA_GRAPHQL_ADMIN_SECRET
            }
        }
    })
    await websocket.send(json_init)


async def send_query(websocket, query):
    json_query = json.dumps({
        "id": "1",
        "type": "start",
        "payload": {
            "query": query
        }
    })

    await websocket.send(json_query)


async def receive_data(websocket):
    response_json = {"type": None}
    while response_json["type"] != "data":
        response = await websocket.recv()
        response_json = json.loads(response)

    return response_json["payload"]["data"]


async def subscribe_block():
    async with websockets.connect(HASURA_WS, subprotocols=["graphql-ws"]) as websocket:
        height_query = """
            subscription MyQuery {
              block_aggregate {
                aggregate {
                  max {
                    block
                  }
                }
              }
            }
        """
        await init(websocket)
        await send_query(websocket, height_query)

        while True:
            await receive_data(websocket)
            missed_blocks = await get_missed_blocks_list()
            if missed_blocks == []:
                pass
            else:
                while True:
                    await sync(missed_blocks)