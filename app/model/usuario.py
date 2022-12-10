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
            cur.execute("""INSERT INTO pokemarket.usuario(nome, email, carteira, senha, tipo, pokemon) VALUES(%s, %s, %s, %s, %s, %s);""",(nome, email, carteira, senha, tipo, pokemons))
            conn.commit()
        except Exception as err:
            print("Erro: %s."%err)
            conn.rollback()
    
    def get(id_=None, email=None):
        if email == None:
            query = """SELECT * FROM pokemarket.usuario WHERE id = {ID}"""
            query = query.format(ID=id_)
        else:
            query = """SELECT * FROM pokemarket.usuario WHERE email = '{EMAIL}'"""
            query = query.format(EMAIL=email)

        cur.execute(query)
        return cur.fetchone()

    def buyRandomPokemon(id_):
        pokemon = randint(1, 151)
        try:
            cur.execute("""UPDATE pokemarket.usuario SET pokemon = pokemon || %s, carteira = carteira - 50 WHERE id = %s;""",(pokemon, id_))
        except Exception as err:
            print("Erro: %s."%err)
            conn.rollback()

    #Da 50₪ para um usuário
    def giveMoney(id_):
        try:
            cur.execute("""UPDATE pokemarket.usuario SET carteira = carteira + 50 WHERE id = %s;""",(pokemon, id_))
        except Exception as err:
            print("Erro: %s."%err)
            conn.rollback()

    def getPassword(email):
        query = """SELECT senha FROM pokemarket.usuario WHERE email = '{EMAIL}'""".format(EMAIL=email)
        
        try:
            cur.execute(query)
            return encrypter.decrypt(str.encode(cur.fetchone()[0])).decode('utf-8')

        except Exception as err:
            print("Erro: %s."%err)
            return -1
            
    def auth(email, senha):
        passwordDB = usuario.getPassword(email)
        
        if (passwordDB != -1):
            return passwordDB == senha
        return -1
