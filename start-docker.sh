#! /bin/bash
# temporeraly import variables
export $(cat .env)

# run postgres and hasura in containers
docker-compose up -d postgres
sleep 10

docker-compose up -d graphql-engine
sleep 10

# init database with basic tables
docker exec -ti port_postgres psql -f /root/schema/block.sql -d PORT -U cyber
docker exec -ti port_postgres psql -f /root/schema/transaction.sql -d PORT -U cyber
docker exec -ti port_postgres psql -f /root/schema/views.sql -d PORT -U cyber

# docker-compose up -d port
# docker-compose up -d cap_api

# docker exec -ti port_postgres psql -c "DROP TABLE block, transaction CASCADE;" -d PORT -U cyber

