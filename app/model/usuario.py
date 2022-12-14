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

    #Cria um objeto usuario. O Objeto só será criado se o usuário existir no banco de dados.
    def __init__(self, email=None, id=None):
        if (email == None):
            query = """SELECT * FROM pokemarket.usuario WHERE id = {ID}"""
            query = query.format(ID=id)
        else:
            query = """SELECT * FROM pokemarket.usuario WHERE email = '{EMAIL}'"""
            query = query.format(EMAIL=email)

        try:
            cur.execute(query)
            userTuple = cur.fetchone()
            
            if userTuple == None:
                raise Exception("Usuário não encontrado.")

            else:
                print(userTuple)
                self.id = userTuple[0]
                self.nome = userTuple[1]
                self.email = userTuple[2]
                self.senha = userTuple[3]
                self.carteira = userTuple[4]
                self.tipo = userTuple[5]
                self.pokemons = userTuple[6]

        except Exception as err:
            print("Erro em usuario.__init__(): %s"%err)

    #Registra o usuario no banco de dados
    def createUser(nome, email, senha, tipo="user", carteira="1000"):
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
            print("Erro em usuario.createUser: %s."%err)
            conn.rollback()

    #Retorna um usuario (Objeto) com os dados do usuário (Banco de Dados)
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
            print("Erro em usuario.get: %s."%err)
        
        userTuple = cur.fetchone()
        
        if (userTuple != None):
            return usuario(id=userTuple[0])
        
        print("Usuário não encontrado.")
        return None

    def buyRandomPokemon(self):
        pokemon = randint(1, 151)

        try:
            cur.execute("""UPDATE pokemarket.usuario SET pokemons = pokemons || %s, carteira = carteira - 50 WHERE id = %s;""",(pokemon, self.id))
            conn.commit()
        except Exception as err:
            print("Erro em buyRandomPokemon: %s."%err)
            conn.rollback()
        
        return 0

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
            print("Erro em usuario.getPassword: %s."%err)
            return -1
            
    def auth(email, senha):
        passwordDB = usuario.getPassword(email)
        
        if (passwordDB != -1):
            return passwordDB == senha
        return False

    def listPokemons(self):

        #A query abaixo gera um array de um unico elemento (pokemon.id) e checa se este elemento esta contido no array usuario.pokemon. OBS: Cada travessia SQL obtem um dos pokemons de usuario.
        try:
            cur.execute("""SELECT pokemarket.pokemon.id, pokemarket.pokemon.nome
                   FROM pokemarket.usuario
                   JOIN pokemarket.pokemon ON pokemarket.usuario.pokemons @> ARRAY[pokemarket.pokemon.id]
                   WHERE pokemarket.usuario.id = %s""", str(self.id))
            
        except Exception as err:
            print("Erro em usuario.listPokemons: %s."%err)
            return -1

        return cur.fetchall()

    def containsPokemon(self, pokemonId):
        pokemons = usuario.listPokemons(self.id)

        if pokemons != -1:
            for pokemon in pokemons:
                if pokemon[0] == pokemonId:
                    return True
                
        return False

    def sell(self, pokemonId, price):
        id_ = self.id
        if usuario.containsPokemon(id_, pokemonId):
            
            try:
                cur.execute("""INSERT INTO pokemarket.venda(vendedor_id, pokemon_id, preco) VALUES(%s, %s, %s)""",(id_, pokemonId, price))
                conn.commit()
                return 0
            except Exception as err:
                print("Erro em usuario.sell: %s"%err)
                conn.rollback()

        return -1

    #Wrapper para auth que pode ser usado com o flask-login
    def is_authenticated(self):
        return auth(self.email, self.senha)

    #Função necessária para o flask-login
    def is_active(self):
        return True
    
    #Função necessária para o flask-login
    def is_anonymous(self):
        return False

    #Função necessária para o flask-login
    def get_id(self):
        return self.id
    
    def bestowAdminPriviledges(self):
        try:
            cur.execute("""UPDATE pokemarket.usuario SET tipo = 'admin' WHERE id = %s""",(self.id))
            conn.commit()
        except Exception as err:
            print("Erro em usuario.bestowAdminPriviledges: %s"%err)
            conn.rollback()