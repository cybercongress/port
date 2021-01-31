import psycopg2
import logging
import json
import websockets


from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, START_BLOCK, ETH_NODE_WSS
from exceptions_decorators import ws_exception_handler


logging.basicConfig(format='%(asctime)s %(message)s')


def get_connection():
    return psycopg2.connect(
                            user=POSTGRES_USER,
                            password=POSTGRES_PASSWORD,
                            host=POSTGRES_HOST,
                            port=POSTGRES_PORT,
                            database=POSTGRES_DB
    )


def write_data_to_db(block, data):
    conn = get_connection()
    c = conn.cursor()
    save_data(c, data)
    save_block(c, block)
    logging.warning(f"block {block} data saved in db")
    conn.commit()
    conn.close()


def write_block_to_db(block):
    conn = get_connection()
    c = conn.cursor()
    save_block(c, block)
    logging.warning(f"block {block} number saved in db")
    conn.commit()
    conn.close()


def save_data(cursor, data):
    cursor.executemany(
                    f'''INSERT INTO transaction (eth_txhash, block, index, sender, cyber, eth)
                    VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;''', data)


def save_block(cursor, block):
    cursor.execute(f'''INSERT INTO block (block) VALUES ({block}) ON CONFLICT DO NOTHING;''')


def bookmark_as_synced(block):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
                        UPDATE block
                        SET checked = true
                        WHERE block IN ({block})
                    '''
                   )
    conn.commit()
    conn.close()


@ws_exception_handler
async def get_last_block():
    query = json.dumps({
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1})
    async with websockets.connect(ETH_NODE_WSS) as websocket:
        while True:
            await websocket.send(query)
            resp = await websocket.recv()
            block = json.loads(resp)['result']
            block = int(block, 0)
            return block


async def get_missed_blocks_list():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM block where checked is not Null')
    blocks = [row[0] for row in c.fetchall()]
    conn.commit()
    conn.close()
    last_block = await get_last_block()
    blocks_list = blocks + [last_block]
    return [x for x in range(START_BLOCK, max(blocks_list) + 1) if x not in blocks_list]
