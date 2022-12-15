from psycopg2 import *
from datetime import datetime

conn = connect(dbname="pokemarket", user="postgres", password="docker", host="localhost")
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
                self.id = vendaTuple[0]
                self.vendedor_d = vendaTuple[1]
                self.comprador_d = vendaTuple[2]
                self.pokemon_id = vendaTuple[3]
                self.preco = vendaTuple[4]
                self.data = vendaTuple[5]
                self.finalizada = vendaTuple[6]
        except Exception as err:
            print("Erro em venda.__init__(): %s"%err)
            return None

    #Registra a venda no Banco de Dados e retorna o seu id ou um código de erro.
    def createVenda(vendedorId, pokemonId, preco):
        
        dateString = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cur.execute("""INSERT INTO pokemarket.venda(vendedor_id, pokemon_id, preco, data_venda) VALUES(%s, %s, %s, %s);""",(vendedorId, pokemonId, preco, dateString))
            conn.commit()
        except Exception as err:
            print("Erro em venda.createVenda: %s."%err)
            conn.rollback()
            return -1

        cur.execute("""SELECT id FROM pokemarket.venda WHERE vendedor_id = %s AND data_venda = %s;""",(vendedorId, dateString))
        return cur.fetchone()[0]

    #Define o comprador da venda no Banco de Dados.
    def setBuyer(self, buyerId):
        try:
            cur.execute("""UPDATE pokemarket.venda SET comprador_id = {BUYERID} WHERE id = {IDVENDA}""".format(BUYERID = str(buyerId), IDVENDA = str(self.idVenda)))
            conn.commit()
        except Exception as err:
            print("Erro em venda.setBuyer: %s."%err)
            conn.rollback()
            return -1
        return 0
    
    #Altera o preço da venda no Banco de Dados.
    def alterPrice(self):
        try:
            cur.execute("""UPDATE pokemarket.venda SET preco = {PRECO} WHERE id = {IDVENDA}""".format(PRECO = str(self.preco), IDVENDA = str(self.idVenda)))
            conn.commit()
        except Exception as err:
            print("Erro em venda.alterPrice: %s."%err)
            conn.rollback()
            return -1
        return 0

    #Recebe alguns filtros(a definir), e uma quantidade de itens maxima, e retorna uma lista com as vendas(tuplas) que atendem aos filtros.
    def listVendas():
        return

    #Altera a coluna "finalizada" para True no Banco de Dados.
    def finishSale(self):
        try:
            cur.execute("""UPDATE pokemarket.venda SET finalizada = true WHERE idVenda = {IDVENDA}""".format(IDVENDA = str(self.idVenda)))
            conn.commit()
        except Exception as err:
            print("Erro em venda.finishSale: %s."%err)
            conn.rollback()
            return -1
        return 0