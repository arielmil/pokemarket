CREATE SCHEMA pokemarket;

CREATE TYPE pokemarket.user_type AS ENUM ('admin', 'user');

SET datestyle = "ISO, DMY";

CREATE TABLE pokemarket.usuario (
    id SERIAL PRIMARY KEY,
    nome text NOT NULL,
    email text NOT NULL UNIQUE,
    senha text NOT NULL,
    carteira integer default 50 NOT NULL,
    tipo pokemarket.user_type default 'user'::pokemarket.user_type NOT NULL,
    pokemons smallint[]
    
    --Tentei colocar cada item de pokemon para ser uma chave estrangeira, mas aparentemente isso quebraria a integridade referencial do BD.
);

CREATE TABLE pokemarket.pokemon (
    id smallint PRIMARY KEY NOT NULL,
    nome text NOT NULL,
    tipo text[] NOT NULL,
    abilidades text[] NOT NULL
);

CREATE TABLE pokemarket.venda (
    id SERIAL PRIMARY KEY,
    vendedor_id integer REFERENCES pokemarket.usuario(id) NOT NULL,
    comprador_id integer REFERENCES pokemarket.usuario(id),
    pokemon_id integer REFERENCES pokemarket.pokemon(id) NOT NULL,
    preco integer NOT NULL,
    data_venda timestamp default NULL,
    finalizada boolean default FALSE NOT NULL
);

ALTER TABLE pokemarket.venda
ADD CONSTRAINT check_comprador_diff_vendedor CHECK (venda.comprador_id != venda.vendedor_id);

COPY pokemarket.pokemon(
id, 
nome, 
tipo, 
abilidades
)

FROM '/pokemonlist.csv'
DELIMITER ','
CSV HEADER;
