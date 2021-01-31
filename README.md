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
3. Go to hasura UI and track all tables
4. Turn on processor

```bash
docker-compose up -d port
```
5. Turn on API
```bash
docker-compose up -d cap_api
```
6. Enjoy!

This set of microservices will listen to an ethereum network for new blocks and write to DB blocks and transaction to address you use. The cyber network sender will listen to new transactions in DB and send eul tokenws for addresses in eth transaction data.
