from unittest import *
from psycopg2 import *
from pathlib import Path
from cryptography.fernet import Fernet
from usuario import Usuario
from venda import Venda

#Guarda os 10 usuarios de teste
Usuarios = []
cur = None

#Pega o hash para encriptagem e desencriptagem
pathToKey = str(Path(__file__).parents[2]) + '/utils/.key.bin'
with open(pathToKey, 'rb') as file_object:
    for line in file_object:
        encryptionKey = line


#Cria 10 usuarios para fins de testes
def criaUsuariosTeste():
    global Usuarios
    cur = conn = connect(dbname="pokemarket", user="postgres", password="docker", host="localhost").cursor()

    #deleta os usuarios dos testes (falhos) anteriores
    try:
        print("\n\nDeletando usuarios teste anteriores...\n\n")
        conn = connect(dbname="pokemarket", user="postgres", password="docker", host="localhost")
        conn.cursor().execute("DELETE FROM pokemarket.usuario WHERE email LIKE 'teste%'")
        conn.commit()
    except Error as err:
        raise Exception("Erro em criaUsuariosTeste(): %s"%err)
    for number in range(1, 11):
        nome = "Teste{number}".format(number=number)
        email = "teste{number}@teste.com".format(number=number)
        senha = "12345"
        Usuario.createUser(nome, email, senha)
        Usuarios.append(Usuario.get(email=email))

#Deleta os usuarios testes
def deletaUsuariosTeste():
    global Usuarios

    for usuario in Usuarios:
        usuario.dropUser()

#Deleta as vendas que sobraram dos testes para integridade do Banco de Dados
def deletaVendasTeste():
    global Usuarios

    for usuario in Usuarios:
        vendas = Venda.listVendas(usuario.id)
        for venda in vendas:
            venda.dropVenda()

class Tester(TestCase):            
    #Testes de Banco de Dados:

    #Teste de conexão com o Banco de dados
    def testConnection(self):
        print("\n\nTestando conexão com o Banco de Dados...\n\n")

        try:
            conn = connect(dbname="pokemarket", user="postgres", password="docker", host="localhost")
            self.cur = conn.cursor()
        except psycop2.Error as err:
            print("\n\nErro ao conectar ao banco de dados: %s\n\n"%err.pgerror)
            conn = None

        self.assertEqual(conn != None, True)

    #Teste de restricao de email unico
    def testUniqueEmail(self):
        print("\n\nTestando restrição de email único...\n\n")

        try:
            cur.execute("INSERT INTO pokemarket.usuario (nome, email, senha, tipo, carteira) VALUES ('Teste', 'teste@testando.com', '12345', 'user', '1000')")
            cur.execute("INSERT INTO pokemarket.usuario (nome, email, senha, tipo, carteira) VALUES ('Teste', 'teste@testando.com', '12345', 'user', '1000')")
            conn.commit()
        except psycop2.Error as err:
            conn.rollback()
            self.assertEqual(err.pgerror == "duplicate key value violates unique constraint \"usuario_email_key\"", True)
        
    #Testes de Usuário:

    
    #Teste de criação de usuário
    def testCreateUser(self):
        print("\n\nTestando criação de usuário...\n\n")

        try:
            Usuario.createUser("Mock", "mock@mockman.com", "1234567")
        except Exception as err:
            self.assertEqual(False, True)
        
        self.assertEqual((Usuario.get(email="mock@mockman.com") != None), True)

    #Teste de fornecer a um usuario 50₪
    def testGiveMoney(self):
        print("\n\nTestando fornecimento de dinheiro...\n\n")

        mockmanId = Usuario.get(email="mock@mockman.com").get_id()
        self.assertEqual(Usuario.giveMoney(mockmanId), True)

    #Teste de dar privilégios de admin a um usuário
    def testBestowAdminPriviledges(self):
        print("\n\nTestando privilégios de admin...\n\n")

        self.assertEqual(Usuario.get(email="mock@mockman.com").bestowAdminPriviledges(), 0)

    #Teste de autenticação de usuário com sucesso
    def testAuthSucess(self):
        print("\n\nTestando autenticação de usuário (Sucesso)...\n\n")

        senha = encrypter.encrypt(str.encode("1234567")).decode("utf-8")
        self.assertEqual(Usuario.auth("mock@mockman.com", senha), True)

    #Teste de autenticação de usuário com falha
    def testAuthFail(self):
        print("\n\nTestando autenticação de usuário (Falha)...\n\n")

        senha = encrypter.encrypt(str.encode("123456789")).decode("utf-8")
        self.assertEqual(Usuario.auth("mock@mockman.com", senha), False)

    #Teste de exclusão de usuário
    def testDropUser(self):
        print("\n\nTestando exclusão de usuário...\n\n")

        user = Usuario.get(email="mock@mockman.com")

        if user.dropUser() != 0:
            self.assertEqual(False, True)
        
        self.assertEqual((Usuario.get(email="mock@mockman.com") == None), True)
    
    
    #Testes de Regras de negócio:

    #Teste de restrição de saldo insuficiente para a compra de um Pokemon
    def testRestricaoSaldoInsuficiente(self):
        print("\n\nTestando restrição de saldo insuficiente...\n\n")

        mockman1 = Usuario.createUser("Mockman1", "mock@mockman1.com", "1234567", carteira = 0)
        mockman2 = Usuario.createUser("Mockman2", "mock@mockman2.com", "1234567")

        mockman2.sell(mockman2.listPokemons()[0], 30)

        try:
            mockman1.buy(mockman2.listVendas()[0])
        except Exception as err:
            self.assertEqual(err == "Saldo insuficiente.", True)
        
        self.assertEqual(True, False)



    #Teste de restrição de um usuário não poder comprar um Pokemon dele mesmo (Mock não pode comprar de Mock)
    def testRestricaoComprarDeSiMesmo(self):
        print("\n\nTestando restrição de comprar de si mesmo...\n\n")

        mockman1 = Usuario.createUser("Mockman1", "mock@mockman1.com", "1234567")

        mockman1.sell(mockman1.listPokemons()[0], 30)

        try:
            mockman.buy(Vendas.listVendas(vendedorId = mockman1.getId())[0])
        
        except Exception as err:
            self.assertEqual(err.pgerror == 'new row for relation "venda" violates check constraint "check_diff"', True)


    #Testes de stress:
    
    #Teste de todos os usuarios colocam dois pokemons a venda
    def testStress1(self):
        print("\n\nTestando stress1 (Todos os usuarios colocam dois pokemons a venda)...\n\n")

        for usuario in self.Usuarios:
            pokemons = usuario.getPokemons()

            for pokemon in pokemons[0:1]:
                venda = usuario.sell(pokemon[0], 30)
                if (venda != None):
                    self.assertEqual(False, True)
            
        self.assertEqual(True, True)

    #Teste de todos os usuarios compram um pokemon de cada usuario (Falta garantir que cada usuario tem pokemons a venda para satisfazer todo mundo)
    def testStress2(self):
        print("\n\nTestando stress2 (Todos os usuarios compram um pokemon de cada usuario)...\n\n")

        UsuariosTemp = self.Usuarios.copy()
        jaForam = []

        for usuario in UsuariosTemp:

            carteira = usuario.getCarteira()

            jaForam.append(UsuariosTemp.pop(usuario))

            for usuario2 in UsuariosTemp:

                vendas = usuario2.getVendas()

                venda = vendas[randint(0, len(vendas)-1)]
                venda.setBuyer(usuario.get_id())
                venda.finishSale()
                usuario.appendToPokemons(venda.getPokemonId())

                Usuario.giveMoney(usuario2.get_id())
                usuario2.buyRandomPokemon()
            
            for usuario2 in jaForam:
                vendas = usuario2.getVendas()

                venda = vendas[randint(0, len(vendas)-1)]
                venda.setBuyer(usuario.get_id())
                venda.finishSale()
                usuario.appendToPokemons(venda.getPokemonId())

                Usuario.giveMoney(usuario2.get_id())
                usuario2.buyRandomPokemon()

            if (usuario.getCarteira() == carteira):
                self.assertEqual(False, True)
        
        self.assertEqual(True, True)

if __name__ == '__main__':
    criaUsuariosTeste()

    unittest.main()

    deletaVendasTeste()

    deletaUsuariosTeste()

    print("\n\n\nAplicação testada com sucesso!\n\n\n")