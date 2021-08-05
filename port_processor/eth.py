import websockets
import json
import logging

from config import RECEIVER, ETH_NODE_WSS, QUERY, START_BLOCK
from db import write_data_to_db, bookmark_as_synced, write_block_to_db
from exceptions_decorators import ws_exception_handler
from cyberpy._wallet import address_to_address


logging.basicConfig(format='%(asctime)s %(message)s')


def get_block_number(resp):
    block = resp['params']['result']['number']
    timestamp = resp['params']['result']['timestamp']
    return int(block, 0), int(timestamp, 0)


@ws_exception_handler
async def get_transactions(block):
    block = hex(block)
    query = json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": [block, True],
            "id": 1
    })
    async with websockets.connect(ETH_NODE_WSS, ping_interval=None) as websocket:
        await websocket.send(query)
        resp = await websocket.recv()
        txs = json.loads(resp)['result']['transactions']
        timestamp = json.loads(resp)['result']['timestamp']
        return txs, timestamp


async def get_receiver_txs(txs: list):
    _txs = []
    _hashes = []
    for tx in txs:
        tx = dict(tx)
        if tx['to'] and tx['to'] == RECEIVER:
            _txs.append(tx)
            _hashes.append((tx['hash']))
        else:
            continue
    __txs = []
    for txhash in _hashes:
        status = await get_valid_txs(txhash)
        if status == 1:
            __txs.extend([x for x in _txs if (txhash == x.get('hash'))])
    return __txs

@ws_exception_handler
async def get_valid_txs(tx):
    query = json.dumps({
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [tx],
        "id": 1
    })
    async with websockets.connect(ETH_NODE_WSS, ping_interval=None) as websocket:
        await websocket.send(query)
        resp = await websocket.recv()
        status = int(json.loads(resp)['result']['status'], 0)
        return status


def parse_txs(txs: list):
    parsed_txs = []
    for tx in txs:
        eth_txhash = tx['hash']
        block = int(tx['blockNumber'], 0)
        index = int(tx['transactionIndex'], 0)
        sender = tx['from']
        cyber = hex_to_str(tx['input'])
        eth = int(tx['value'], 0) / 10**18
        temp = (eth_txhash, block, index, sender, cyber, eth)
        if cyber is None or eth == 0:
            pass
        else:
            parsed_txs.append(temp)
    return parsed_txs


async def process(block):
    txs = await get_transactions(block)
    txs, timestamp = txs[0], txs[1]
    _txs = await get_receiver_txs(txs)
    data = parse_txs(_txs)
    timestamp = int(timestamp, 0)
    if block >= START_BLOCK:
        write_data_to_db(block, data, timestamp)
        bookmark_as_synced(block)
    else:
        pass


def hex_to_str(hex_str):
    hex_str = hex_str[2:]
    bytes_object = bytes.fromhex(hex_str)
    address = bytes_object.decode()
    try:
        address = address_to_address(address, 'cyber')
        if len(address) != 44 or 'cyber' not in address:
            return None
        else:
            return address
    except Exception:
        return None


@ws_exception_handler
async def receive():
    async with websockets.connect(ETH_NODE_WSS, ping_interval=None) as websocket:
        await websocket.send(QUERY)
        while True:
            resp = await websocket.recv()
            resp = json.loads(resp)
            if 'params' in resp.keys():
                block, timestamp = get_block_number(resp)
                if block >= START_BLOCK:
                    write_block_to_db(block, timestamp)
                else:
                    pass
            else:
                pass


async def sync(missing_blocks):
    for block in missing_blocks:
        await process(block)
