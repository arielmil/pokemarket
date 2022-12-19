import pokebase as pb
import copy

ids = []
pokemons = []

#Template para a lista de Pokemons
pokemon = {"number": 1, "name": '', "abilities": [], "types": []}

#Lista com os ids dos Pokemons gen I
for num in range(1, 152):
    ids.append(num)
    pokemons.append(copy.deepcopy(pokemon))

#Query para obter os dados de Pokemons
i = 0
for id_ in ids:
    pokemon_ = pb.pokemon(id_)

    number = pokemon_.id
    name = pokemon_.name.title()

    abilities_ = pokemon_.abilities

    #Lista com as abilidades do Pokemon
    abilities = []

    types_ = pokemon_.types

    #Lista com os tipos do Pokemon
    types = []

    for ability in abilities_:
        abilities.append(ability.ability.name.title())

    for type_ in types_:
        types.append(type_.type.name.title())

    pokemons[i]["number"] = number
    pokemons[i]["name"] = name
    pokemons[i]["abilities"] = abilities
    pokemons[i]["types"] = types
    
    i = i + 1


with open("pokemonlist.csv", "w") as writer:
    writer.write("id,nome,tipo,abilidades\n")
    for pokemon in pokemons:

        tipo = ""
        ultima_pos = len(pokemon["types"]) - 1
        i = 0
        
        for tipo_ in pokemon["types"]:
            if (i == ultima_pos):
                tipo = tipo + str(tipo_)
            else:
                tipo = tipo + str(tipo_) + ","

            i = i + 1
        
        abilidades = ""
        ultima_pos = len(pokemon["abilities"]) - 1
        i = 0
        
        for abilidade in pokemon["abilities"]:
            if (i == ultima_pos):
                abilidades = abilidades + str(abilidade)
            else:
                abilidades = abilidades + str(abilidade) + ","

            i = i + 1
            
        string = '{0},{1},"{{{2}}}","{{{3}}}"\n'
        writer.write(string.format(str(pokemon["number"]), pokemon["name"], tipo, abilidades))
