from psycopg2 import *
from datetime import datetime

conn = connect(dbname="pokemarket", user="postgres", password="docker", host="database", port= "dababase:5432")
cur = conn.cursor()

class Venda:
    #Cria um objeto Venda. O Objeto só será criado se a venda existir no Banco de dados.
    def __init__(self, id):
        
        query = """SELECT * FROM pokemarket.venda WHERE id = {IDVENDA}"""
        query = query.format(IDVENDA = str(id))
        
        try:
            cur.execute(query)
            vendaTuple = cur.fetchone()
            
            if vendaTuple == None:
                raise Exception("Venda não encontrada.")
            else:
                self.id = id
                self.vendedor_id = vendaTuple[1]
                self.comprador_id = vendaTuple[2]
                self.pokemon_id = vendaTuple[3]
                self.preco = vendaTuple[4]
                self.data = vendaTuple[5]
                self.finalizada = vendaTuple[6]

        except Error as err:
            raise Exception("Erro em venda.__init__(): %s"%err)

    #Registra a venda no Banco de Dados e retorna o seu id.
    def createVenda(vendedorId, pokemonId, preco):
        
        dateString = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cur.execute("""INSERT INTO pokemarket.venda(vendedor_id, pokemon_id, preco, data_venda) VALUES(%s, %s, %s, %s);""",(vendedorId, pokemonId, preco, dateString))
            conn.commit()

        except Error as err:
            conn.rollback()
            raise Exception("Erro em venda.createVenda: %s."%err)

        cur.execute("""SELECT id FROM pokemarket.venda WHERE vendedor_id = %s AND data_venda = %s;""",(vendedorId, dateString))
        return cur.fetchone()[0]

    #Define o comprador da venda no Banco de Dados.
    def setBuyer(self, buyerId):
        try:
            cur.execute("""UPDATE pokemarket.venda SET comprador_id = %s WHERE id = %s""",(buyerId, self.id))
            conn.commit()

        except Error as err:
            conn.rollback()
            raise Exception("Erro em venda.setBuyer: %s."%err)

        self.comprador_id = buyerId
        return 0
    
    #Altera o preço da venda no Banco de Dados.
    def alterPrice(self, price):
        try:
            cur.execute("""UPDATE pokemarket.venda SET preco = %s WHERE id = %s""",(price, self.id))
            conn.commit()
        except Error as err:
            conn.rollback()
            raise Exception("Erro em venda.alterPrice: %s."%err)
        
        self.preco = price
        return 0

    #Recebe alguns filtros(a definir), e uma quantidade de itens maxima, e retorna uma lista com as vendas(tuplas) que atendem aos filtros.
    def listVendas(vendedorId = None):
        if vendedorId == None:
            query = """SELECT venda.id, usuario.nome, pokemon_id, pokemon.nome, preco, data_venda
            FROM pokemarket.venda
            INNER JOIN pokemarket.usuario ON vendedor_id = usuario.id
            INNER JOIN pokemarket.pokemon ON pokemon_id = pokemon.id
            WHERE finalizada = false"""
        
        else:
            query = """SELECT venda.id, usuario.nome, pokemon_id, pokemon.nome, preco, data_venda
            FROM pokemarket.venda
            INNER JOIN pokemarket.usuario ON vendedor_id = usuario.id
            INNER JOIN pokemarket.pokemon ON pokemon_id = pokemon.id
            WHERE finalizada = false AND vendedor_id = {ID}"""
            query = query.format(ID = vendedorId)

        try:
            cur.execute(query)
            return cur.fetchall()
            
        except Error as err:
            raise Exception("Erro em venda.listVendas: %s."%err)
                
    #Altera a coluna "finalizada" para True no Banco de Dados, e transfere a quantidade de dinheiro do comprador para o vendedor.
    def finishSale(self):
        try:
            print("\n\n\nPreco da venda: %s\n\n\n", self.preco)
            query = """UPDATE pokemarket.venda SET finalizada = true WHERE id = {ID}""".format(ID = self.id)
            cur.execute(query)

            query = """UPDATE pokemarket.usuario SET carteira = carteira + {PRECO} WHERE id = {ID}""".format(PRECO = self.preco, ID = self.vendedor_id)
            cur.execute(query)

            query = """UPDATE pokemarket.usuario SET carteira = carteira - {PRECO} WHERE id = {ID}""".format(PRECO = self.preco, ID = self.comprador_id)
            cur.execute(query)

            conn.commit()

        except Error as err:
            print("Erro em venda.finishSale: %s."%err)
            conn.rollback()
            raise Exception ("Erro ao finalizar venda.")

        return 0

    def getPreco(self):
        return self.preco

    def getPokemonId(self):
        return self.pokemon_id

    def dropVenda(self):
        try:
            cur.execute("""DELETE FROM pokemarket.venda WHERE id = %s""",(self.id,))
            conn.commit()
        except Error as err:
            conn.rollback()
            raise Exception("Erro em venda.dropVenda: %s."%err)
        return 0
