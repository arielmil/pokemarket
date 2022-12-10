FROM postgres
ENV POSTGRES_PASSWORD docker
ENV POSTGRES_DB pokemarket
COPY utils/pokemonlist.csv .
COPY utils/start.sql /docker-entrypoint-initdb.d/
COPY utils/start.sh .
