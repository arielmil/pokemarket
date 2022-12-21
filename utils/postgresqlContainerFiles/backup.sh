data=$(printf '%(%Y-%m-%d)T\n' -1)
pg_dump -d pokemarket -h localhost -U postgres >> backup/$data
