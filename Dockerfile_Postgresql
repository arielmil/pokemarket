FROM postgres:14.5
ENV POSTGRES_PASSWORD docker
ENV POSTGRES_DB pokemarket

RUN mkdir utils
COPY utils/postgresqlContainerFiles/pokemonScrapper.py ./utils

RUN apt-get update && apt-get install python3-pip -y && pip install --upgrade pip pokebase

RUN python3 ./utils/pokemonScrapper.py

COPY utils/postgresqlContainerFiles/start.sql /docker-entrypoint-initdb.d/
