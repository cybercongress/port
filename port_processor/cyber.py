import aiohttp
import asyncio
import logging
import json


from exceptions_decorators import aiohttp_exception_handler
from cyberpy import Transaction, seed_to_privkey, privkey_to_address, address_to_address
from config import SENDER, LCD_API, TIME_SLEEP, gRPC_API
from db import get_connection


logging.basicConfig(format='%(asctime)s %(message)s')


async def send():
    while True:
        data = get_data()
        if data:
            await process_txs(data)
            await asyncio.sleep(TIME_SLEEP)
        else:
            await asyncio.sleep(TIME_SLEEP)
            pass


async def process_txs(tx):
    address = tx[3]
    address = address_to_address(address, 'bostrom')
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
    return f"According to this ethereum network transaction hash {eth_hash} you get {euls} cybs."


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
    return 1


def eul_func(x):
    return 0.000099 * x**2 + 0.1 * x


async def get_transaction(to, euls, memo):
    priv_key = seed_to_privkey(SENDER)
    address = privkey_to_address(priv_key)
    info = await get_account_info(address)
    sequence, number = info
    tx = Transaction(
        privkey=priv_key,
        account_num=number,
        sequence=sequence,
        fee=1,
        gas=200000,
        memo=memo,
        chain_id="bostrom-testnet-1",
        sync_mode="broadcast_tx_sync",
    )
    tx.add_transfer(recipient=to, amount=euls)
    return tx.get_pushable()


async def broadcast(tx):
    while True:
        async with aiohttp.ClientSession() as client:
            return await broadcaster(client, tx)


@aiohttp_exception_handler
async def broadcaster(client, tx):
    async with client.post(gRPC_API, data=tx) as resp:
        resp = await process_resp(client, resp)
        print(resp)
        if resp['result']['code'] == 0:
            return resp['result']['hash']
        else:
            return None


async def get_account_info(address):
    while True:
        async with aiohttp.ClientSession() as client:
            return await get_info(client, address)


@aiohttp_exception_handler
async def get_info(client, address):
    url = LCD_API + '/cosmos/auth/v1beta1/accounts/' + address
    async with client.get(url) as resp:
        resp = await process_resp(client, resp)
        resp = resp['account']
        if 'base_vesting_account' in resp.keys():
            sequence = int(resp['base_vesting_account']['base_account']['sequence'])
            number = int(resp['base_vesting_account']['base_account']['account_number'])
        else:
            sequence = int(resp['sequence'])
            number = int(resp['account_number'])
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

