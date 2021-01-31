# Port

ETH-CYBER bridge for the great future.

## Structure

- Postgres DB
- Hasura graphql engine
- ETH network indexer
- Cyber network sender
- API for market data

## Usage

1. Fill `.env` file with necessary credentials
2. Run:

```bash
./start-docker.sh
```

This set of microservices will listen to an ethereum network for new blocks and write to DB blocks and transaction to address you use. The cyber network sender will listen to new transactions in DB and send eul tokenws for addresses in eth transaction data.
