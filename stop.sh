#!/bin/bash

docker compose down
docker image rm projeto_pokemon-cron:latest projeto_pokemon-pokemarket_app:latest projeto_pokemon-pokemarket_database:latest
