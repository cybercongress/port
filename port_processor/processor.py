import asyncio
from eth import receive
from db_subscription import subscribe_block
from cyber import send


def processor():
    print("Starting PORT...")
    ioloop = asyncio.get_event_loop()
    tasks = [
        ioloop.create_task(receive()),
        ioloop.create_task(subscribe_block()),
        ioloop.create_task(send())
    ]
    ioloop.run_until_complete(asyncio.wait(tasks))
    ioloop.close()
