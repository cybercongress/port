# Port

The amazing tool provide tickets to `cyber` network.

## Structure

- Postgres DB
- Hasura graphql engine
- ETH network indexer
- Cyber network sender
- API for market data

## Usage

1. Fill `.env` file with necessary credentials

    > Filled data is default. Don't touch it without reason.

    ```bash
    POSTGRES_FOLDER=./pdb                                       # dir for the postgres db data
    POSTGRES_HOST=127.0.0.1                                     # host for postgres db
    POSTGRES_PORT=5432                                          # port for postgres db
    POSTGRES_DB=PORT                                            # postgres db name
    POSTGRES_USER=<username>                                    # postgres db user name
    POSTGRES_PASSWORD=<password>                                # postgres db user password
    HASURA_HOST=0.0.0.0                                         # graph-ql engine host
    HASURA_PORT=<port>                                          # graph-ql engine port
    HASURA_GRAPHQL_ADMIN_SECRET=<secret>                        # graph-ql engine password


    ETH_NODE_WSS=<wss://your_endpoint.xyz>                      # ethereum websocket
    ETH_NODE_RPC=<https://your_endpoint.xyz>                    # ethereum rpc
    RECEIVER=<0x_ethereum_receiver_address>                     # ethereum address


    CAP_API_HOST=0.0.0.0                                        # market data host
    CAP_API_PORT=<port>                                         # market data port


    LCD_API=<https://your_endpoint.xyz>                         # cyber LCD API enpoint
    SENDER=<put your mnemonic phrase here>                      # cyber sender address mnemonic
    START_BLOCK=<block_number>                                  # the block for indexer start
    ```

2. Run:

    ```bash
    ./start-docker.sh
    ```

    This command will export all environment values from `.env` file and run postgres and hasura docker containers.

3. Go to hasura UI and track all tables

    This is necessary for sender listener if db updated.

4. Turn on port processor

    ```bash
    docker-compose up -d port
    ```

5. Turn on API

    ```bash
    docker-compose up -d cap_api
    ```

6. Enjoy!

This set of microservices will listen to an ethereum network for new blocks and write to DB blocks and transaction to address you use with correct conditions:

- transaction contain cyberadress in `data`
- this is not zero-value transaction
- transaction executed by contract (status: success).

The cyber network sender will listen to new transactions in DB and send eul tokens for addresses in eth transaction data by implemented formula.
