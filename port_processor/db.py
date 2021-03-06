import psycopg2
import logging
import json
import websockets
import itertools


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


def write_data_to_db(block, data, timestamp):
    conn = get_connection()
    c = conn.cursor()
    save_data(c, data)
    save_block(c, block, timestamp)
    logging.warning(f"block {block} data saved in db")
    conn.commit()
    conn.close()


def write_block_to_db(block, timestamp):
    conn = get_connection()
    c = conn.cursor()
    save_block(c, block, timestamp)
    logging.warning(f"block {block} number saved in db")
    conn.commit()
    conn.close()


def save_data(cursor, data):
    cursor.executemany(
                    f'''INSERT INTO transaction (eth_txhash, block, index, sender, cyber, eth)
                    VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;''', data)


def save_block(cursor, block, timestamp=None):
    if timestamp:
        cursor.execute(f'''INSERT INTO block (block, block_time) VALUES ({block}, {timestamp}) ON CONFLICT DO NOTHING;''')
    else:
        cursor.execute(
            f'''INSERT INTO block (block) VALUES ({block}) ON CONFLICT DO NOTHING;''')


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
    c.execute('SELECT max(block) FROM block where checked is not Null')
    last_synced_block = c.fetchall()[0][0]
    try:
        c.execute(f'SELECT block FROM block where checked is Null and block < {last_synced_block}')
        missed_blocks = list(itertools.chain(*c.fetchall()))
    except psycopg2.errors.InFailedSqlTransaction:
        missed_blocks = []
    conn.commit()
    conn.close()
    last_block = await get_last_block()
    if last_synced_block:
        start = max([START_BLOCK, last_synced_block])
        blocks_list = missed_blocks + list(range(start + 1, last_block + 1))
    else:
        start = START_BLOCK
        blocks_list = missed_blocks + list(range(start, last_block + 1))
    return blocks_list
