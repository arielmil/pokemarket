# pokemarket

## Python

- Trello: https://trello.com/b/iWBne7tr/projeto-pokemon

- Para rodar o projeto, execute o instalador setup.sh no diretório raiz do projeto (setup.sh, ou ./setup.sh). Ele cuidara da instalação do Docker Engine (Caso não exista uma), e colocara o projeto no ar em Localhost. OBS: Isso significa que não é necessário clonar este repositório manualmente. Basta baixar os arquivos setup.sh, e stop.sh

- Para parar o projeto, execute o programa stop.sh no diretório raiz do projeto.

- Os backups são feitos a meia noite (UTC), e são armazenados no diretório projeto_pokemon-cron:/backups no container projeto_pokemon-cron.

- Logs são feitos a cada criação / conclusão de venda, e a cada login de usuário. São armazenados em projeto_pokemon-cron:/logs.
