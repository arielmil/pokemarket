data=$(/bin/date +\%d-\%m-\%Y--\%H:\%M:\%S)
pg_dump -h pokemarket_database -p 5432 -U postgres -w -Fc >> $data.dump
