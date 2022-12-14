from psycopg2 import *
from random import randint
from pathlib import Path
from cryptography.fernet import Fernet

#Conecta com a database e gera um cursor para queries
conn = connect(dbname="pokemarket", user="postgres", password="docker", host="localhost")
cur = conn.cursor()

#Pega o hash para encriptagem e desencriptagem
pathToKey = str(Path(__file__).parents[2]) + '/utils/.key.bin'
with open(pathToKey, 'rb') as file_object:
    for line in file_object:
        encryptionKey = line

#Gera um objeto para encriptar e desencriptar
encrypter = Fernet(encryptionKey)

class usuario:
    def __init__(self, nome, email, senha, tipo="user", carteira="1000"):
        
        i = 0
        pokemons = []

        #Encripta a senha e converte o bytecode gerado para uma string para ser armazenada no Banco de Dados.
        senha = encrypter.encrypt(str.encode(senha)).decode("utf-8")

        #Usuário recebe 3 Pokemons aleatórios
        while(i < 3):
            pokemons.append(randint(1, 151))
            i = i + 1
            
        try:
            cur.execute("""INSERT INTO pokemarket.usuario(nome, email, carteira, senha, tipo, pokemons) VALUES(%s, %s, %s, %s, %s, %s);""",(nome, email, carteira, senha, tipo, pokemons))
            conn.commit()
        except Exception as err:
            print("Erro em __init__: %s."%err)
            conn.rollback()
    
    def get(userId=None, email=None):
        if email == None:
            query = """SELECT * FROM pokemarket.usuario WHERE id = {ID}"""
            query = query.format(ID=userId)
        else:
            query = """SELECT * FROM pokemarket.usuario WHERE email = '{EMAIL}'"""
            query = query.format(EMAIL=email)

        try:
            cur.execute(query)
        except Exception as err:
            print("Erro em get: %s."%err)
        
        userTuple = cur.fetchone()
        
        if (userTuple != None):

            userDictionary = {
                "id": userTuple[0],
                "nome": userTuple[1],
                "email": userTuple[2],
                "carteira": userTuple[3],
                "senha": userTuple[4],
                "tipo": userTuple[5],
                "pokemons": userTuple[6]
            }

            return userDictionary
        
        print("Usuário não encontrado.")
        return -1

    def buyRandomPokemon(userId):
        pokemon = randint(1, 151)
        try:
            cur.execute("""UPDATE pokemarket.usuario SET pokemons = pokemons || %s, carteira = carteira - 50 WHERE id = %s;""",(pokemon, userId))
            conn.commit()
        except Exception as err:
            print("Erro em buyRandomPokemon: %s."%err)
            conn.rollback()

    #Da 50₪ para um usuário
    def giveMoney(userId):
        try:
            cur.execute("""UPDATE pokemarket.usuario SET carteira = carteira + 50 WHERE id = %s;""",(userId))
            conn.commit()
        except Exception as err:
            print("Erro em giveMoney: %s."%err)
            conn.rollback()

    def getPassword(email):
        query = """SELECT senha FROM pokemarket.usuario WHERE email = '{EMAIL}'""".format(EMAIL=email)
        
        try:
            cur.execute(query)
            return encrypter.decrypt(str.encode(cur.fetchone()[0])).decode('utf-8')

        except Exception as err:
            print("Erro em getPassword: %s."%err)
            return -1
            
    def auth(email, senha):
        passwordDB = usuario.getPassword(email)
        
        if (passwordDB != -1):
            return passwordDB == senha
        return False

    def listPokemons(userId):

        #A query abaixo gera um array de um unico elemento (pokemon.id) e checa se este elemento esta contido no array usuario.pokemon. OBS: Cada travessia SQL obtem um dos pokemons de usuario.
        try:
            cur.execute("""SELECT pokemarket.pokemon.id, pokemarket.pokemon.nome
                   FROM pokemarket.usuario
                   JOIN pokemarket.pokemon ON pokemarket.usuario.pokemons @> ARRAY[pokemarket.pokemon.id]
                   WHERE pokemarket.usuario.id = %s""", str(userId))
            
        except Exception as err:
            print("Erro em listPokemons: %s."%err)
            return -1

        return cur.fetchall()

    def containsPokemon(userId, pokemonId):
        pokemons = usuario.listPokemons(userId)

        if pokemons != -1:
            for pokemon in pokemons:
                if pokemon[0] == pokemonId:
                    return True
                
        return False

    def sell(userId, pokemonId, price):
        if usuario.containsPokemon(userId, pokemonId):
            
            try:
                cur.execute("""INSERT INTO pokemarket.venda(vendedor_id, pokemon_id, preco) VALUES(%s, %s, %s)""",(userId, pokemonId, price))
                conn.commit()
                return 0
            except Exception as err:
                print("Erro em sell: %s"%err)
                conn.rollback()

        return -1
