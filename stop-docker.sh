docker stop port
docker stop cap_api
docker stop port_hasura
docker stop port_postgres

docker rm port
docker rm cap_api
docker rm port_hasura
docker rm port_postgres

docker image rm port_port
docker image rm port_cap_api

# rm -rf pdb
# mkdir pdb