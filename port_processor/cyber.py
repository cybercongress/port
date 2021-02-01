import aiohttp
import asyncio
import logging
import json


from exceptions_decorators import aiohttp_exception_handler
from cyberpy import Transaction
from cyberpy import seed_to_privkey, privkey_to_address
from config import SENDER, LCD_API, TIME_SLEEP
from db import get_connection


logging.basicConfig(format='%(asctime)s %(message)s')


async def send():
    while True:
        data = get_data()
        if data:
            await process_txs(data)
        else:
            await asyncio.sleep(TIME_SLEEP)
            pass


async def process_txs(tx):
    address = tx[3]
    euls = get_euls(tx[4], tx[7])
    memo = generate_memo(tx[1], euls)
    _tx = await get_transaction(address, euls, memo)
    cyber_hash = await broadcast(_tx)
    if cyber_hash:
        update_db(tx[1], cyber_hash,  euls)
        logging.warning(f"processed cyberhash {cyber_hash} by transaction {tx[1]} with {euls} euls")
    else:
        pass


def update_db(eth_hash, cyber_hash, euls):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
                    UPDATE transaction
                    SET eul = {euls}, cyber_hash = \'{cyber_hash}\'
                    WHERE eth_txhash like (\'{eth_hash}\');
                    ''')
    conn.commit()
    conn.close()


def generate_memo(eth_hash, euls):
    return f"According to this ethereum network transaction hash {eth_hash} you get {euls} euls."


def get_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                    SELECT * 
                    FROM txs_queue 
                    WHERE cyber_hash is Null and checked is not Null limit 1
    ''')
    txs = cursor.fetchall()
    if txs != []:
        return txs[0]
    else:
        return None


def get_euls(eth, sum_eul):
    if not sum_eul:
        sum_eul = 0
    geul = sum_eul / 10**9
    const = eul_func(geul) + eth
    x0_eul = ((1000 / 99) * (((99 * const + 2500)**(1/2)) - 50)) * 10**9
    return int(x0_eul - sum_eul)


def eul_func(x):
    return 0.000099 * x**2 + 0.1 * x


async def get_transaction(to, euls, memo):
    priv_key = seed_to_privkey(SENDER)
    address = privkey_to_address(priv_key)
    info = await get_account_info(address)
    sequence, number = info
    euls = int(euls / 1000)
    tx = Transaction(
        privkey=priv_key,
        account_num=number,
        sequence=sequence,
        fee=0,
        gas=200000,
        memo=memo,
        chain_id="euler-6",
        sync_mode="block",
    )
    tx.add_transfer(recipient=to, amount=euls)

    return tx.get_pushable()


async def broadcast(tx):
    while True:
        async with aiohttp.ClientSession() as client:
            return await broadcaster(client, tx)


@aiohttp_exception_handler
async def broadcaster(client, tx):
    async with client.post(LCD_API + '/txs', data=tx, headers={'content-type': 'application/json'}) as resp:
        while True:
            resp = await process_resp(client, resp)
            if 'code' in resp.keys():
                return None
            else:
                return resp['txhash']


async def get_account_info(address):
    while True:
        async with aiohttp.ClientSession() as client:
            return await get_info(client, address)


@aiohttp_exception_handler
async def get_info(client, address):
    async with client.get(LCD_API + '/auth/accounts/' + address) as resp:
        while True:
            resp = await process_resp(client, resp)
            sequence = resp['result']['value']['sequence']
            number = resp['result']['value']['account_number']
            return sequence, number


async def process_resp(client, resp):
    if resp.status != 200:
        logging.warning(f'CYBER LCD Connection error {resp.status}. {TIME_SLEEP} for the next reconnect attempt...')
        await asyncio.sleep(TIME_SLEEP)
        await send()
    else:
        resp = await resp.read()
        await client.close()
        return json.loads(resp)

