from psycopg2 import *
from random import randint
from pathlib import Path
from cryptography.fernet import Fernet
from model.venda import Venda

#Conecta com a database e gera um cursor para queries
conn = connect("host=localhost dbname=pokemarket user=postgres password=docker")
cur = conn.cursor()

#Pega o hash para encriptagem e desencriptagem
pathToKey = str(Path(__file__).parents[2]) + '/utils/.key.bin'
with open(pathToKey, 'rb') as file_object:
    for line in file_object:
        encryptionKey = line

#Gera um objeto para encriptar e desencriptar
encrypter = Fernet(encryptionKey)

class Usuario:

    #Cria um objeto Usuario. O Objeto só será criado se o usuário existir no banco de dados.
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

        except Error as err:
            raise Exception("Erro em Usuario.__init__(): %s"%err)

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
            
        except Error as err:
            conn.rollback()
            raise Exception("Erro em Usuario.createUser: %s."%err)

    #Retorna um usuario (Objeto) com os dados do usuário (Banco de Dados)
    def get(id=None, email=None):
        if email == None:
            query = """SELECT * FROM pokemarket.usuario WHERE id = {ID}"""
            query = query.format(ID=id)
        else:
            query = """SELECT * FROM pokemarket.usuario WHERE email = '{EMAIL}'"""
            query = query.format(EMAIL=email)

        try:
            cur.execute(query)

        except Error as err:
            raise Exception("Erro em Usuario.get: %s."%err)
        
        userTuple = cur.fetchone()
        
        if (userTuple != None):
            return Usuario(id=userTuple[0])
        
        print("Usuário não encontrado.")
        return None

    #Coloca o pokemon de id pokemonId na lista de pokemons do usuario no Banco de dados
    def appendToPokemons(self, pokemonId):
        try:
            cur.execute("""UPDATE pokemarket.usuario SET pokemons = pokemons || %s WHERE id = %s;""",(pokemonId, self.id))
            conn.commit()
        except Error as err:
            conn.rollback()
            raise Exception("Erro em Usuario.appendToPokemons: %s."%err)

        self.pokemons.append(pokemonId)
        return 0

    #Compra um pokemon aleatório por 50₪ e adiciona aos pokemons do usuário
    def buyRandomPokemon(self):
        pokemon = randint(1, 151)

        try:
            cur.execute("""UPDATE pokemarket.usuario SET pokemons = pokemons || %s, carteira = carteira - 50 WHERE id = %s;""",(pokemon, self.id))
            conn.commit()
        except Error as err:
            conn.rollback()
            raise Exception("Erro em Usuario.buyRandomPokemon: %s."%err)
        
        self.carteira = self.carteira - 50
        self.pokemons.append(pokemon)
        return 0

    #Da 50₪ para um usuário
    def giveMoney(userId):

        try:
            cur.execute("""UPDATE pokemarket.usuario SET carteira = carteira + 50 WHERE id = %s;""",(userId))
            conn.commit()

        except Error as err:
            conn.rollback()
            raise Exception("Erro em giveMoney: %s."%err)
                
        return 0
        
    #Retorna o tipo do usuário
    def getTipo(self):
        return self.tipo

    #Retorna a senha do usuário
    def getPassword(email):
        query = """SELECT senha FROM pokemarket.usuario WHERE email = '{EMAIL}'""".format(EMAIL=email)
        
        try:
            cur.execute(query)
            ret = cur.fetchone()
            return -1 if ret == None else ret[0]

        except Error as err:
            raise Exception("Erro em Usuario.getPassword: %s."%err)
    
    #Retorna True se a senha estiver correta
    def auth(email, senha):
        passwordDB = Usuario.getPassword(email)
        if (passwordDB != -1):
            passwordDB = encrypter.decrypt(passwordDB.encode("utf-8")).decode("utf-8")
            return passwordDB == senha
        return False

    #Retorna um array com os pokemons do usuario
    def listPokemons(self):

        #A query abaixo gera um array de um unico elemento (pokemon.id) e checa se este elemento esta contido no array usuario.pokemon. OBS: Cada travessia SQL obtem um dos pokemons de usuario.
        try:
            query = """SELECT pokemarket.pokemon.id, pokemarket.pokemon.nome
                   FROM pokemarket.usuario
                   JOIN pokemarket.pokemon ON pokemarket.usuario.pokemons @> ARRAY[pokemarket.pokemon.id]
                   WHERE pokemarket.usuario.id = {ID}""".format(ID=self.id)
            cur.execute(query)
            conn.commit()
        except Error as err:
            print("errooooooooooo")
            raise Exception("Erro em Usuario.listPokemons: %s."%err)

        return cur.fetchall()

    #Checa se o usuario possui um pokemon
    def containsPokemon(self, pokemonId):
        pokemons = self.listPokemons()
        if pokemons != None:
            for pokemon in pokemons:
                if pokemon[0] == pokemonId:
                    return True
                
        return False

    #Coloca um pokemon a venda no mercado e retorna um objeto Venda (ou -1 em caso de erro)
    def sell(self, pokemonId, price):
        userId = self.id
        if self.removePokemon(pokemonId) != -1:
            vendaId = Venda.createVenda(userId, pokemonId, price)
            
            if vendaId != -1:
                venda = Venda(vendaId)
            else:
                raise Exception("Erro ao criar venda.")
            
            return venda if venda != None else -1

        else:
            raise Exception("Erro ao remover pokemon do usuario.")
    
    #Compra o pokemon de uma venda
    def buy(self, vendaId):
        venda = Venda(vendaId)
        if venda != None:
            if self.carteira >= venda.getPreco():
                venda.setBuyer(self.id)
                venda.finishSale()
                self.appendToPokemons(venda.getPokemonId())
            else:
                raise Exception("Saldo insuficiente.")

            
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
    
    #Fornece privilégios de administrador para um usuário
    def bestowAdminPriviledges(self):

        try:
            cur.execute("""UPDATE pokemarket.usuario SET tipo = 'admin' WHERE id = %s""",(self.id))
            conn.commit()

        except Error as err:
            conn.rollback()
            raise Exception("Erro em Usuario.bestowAdminPriviledges:")

        self.tipo = 'admin'
        return 0
    
    #Retorna a carteira (Quantidade de dinheiro) do usuário
    def getCarteira(self):
        try:
            cur.execute("""SELECT carteira FROM pokemarket.usuario WHERE id = {ID}""".format(ID = str(self.id)))
            return cur.fetchone()[0]

        except Error as err:
            raise Exception("Erro em Usuario.getCarteira: %s."%err)

    #Retira um pokemon (identificado por pokemonId) do usuário
    def removePokemon(self, pokemonId):
        if self.containsPokemon(pokemonId):
            try:
                cur.execute("""UPDATE pokemarket.usuario SET pokemons = array_remove(pokemons, %s) WHERE id = %s""",(pokemonId, self.id))
                conn.commit()

            except Error as err:
                conn.rollback()
                raise Exception("Erro em Usuario.removePokemon: %s"%err)

            self.pokemons.remove(pokemonId)
            return 0

        else:
           print("\n\n\nUsuário não possui o pokemon especificado.\n\n\n")
           return -1
    
    #Deleta um usuário do anco de dados
    def dropUser(self):
        try:
            cur.execute("""DELETE FROM pokemarket.usuario WHERE id = %s""",(self.id))
            conn.commit()

        except Error as err:
            conn.rollback()
            raise Exception("Erro em Usuario.dropUser: %s"%err)

        return 0

    #Retorna o nome do usuário
    def getNome(self):
        return self.nome