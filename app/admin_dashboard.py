from psycopg2 import *

class Dashboard():
    def __init__(self):
        self.conn = connect("host=localhost dbname=pokemarket user=postgres password=docker")
        self.cur = self.conn.cursor()
    
    #Retorna o nome do comprador, nome do vendedor, data, nome do pokemon, o preço da compra e o id
    def maiorCompra(self):
        query = """SELECT comprador.nome, vendedor.nome, venda.data, pokemon.nome, venda.preco, venda.id
                   FROM pokemarket.venda as venda
                   INNER JOIN pokemarket.usuario as comprador ON venda.comprador_id = comprador.id
                   INNER JOIN pokemarket.usuario as vendedor ON venda.vendedor_id = vendedor.id
                   INNER JOIN pokemarket.pokemon as pokemon ON venda.pokemon_id = pokemon.id
                   ORDER BY venda.preco DESC
                   LIMIT 1"""
        
        try:
            self.cur.execute(query)
            return self.cur.fetchall()

        except Error as err:
            raise Exception("Erro em Dashboard.maiorCompra(): %s"%err)
    
    #Retorna o nome e o id do usuário com o maior número de pokemons
    def usuarioComMaisPokemons(self):
        query = """SELECT usuario.nome, usuario.id
                   FROM pokemarket.usuario as usuario
                   ORDER BY usuario.pokemons DESC
                   LIMIT 1"""
        
        try:
            self.cur.execute(query)
            return self.cur.fetchone()
        
        except Error as err:
            raise Exception("Erro em Dashboard.usuarioComMaisPokemons(): %s"%err)
    
    #Retorna o nome e o id do usuário com a maior carteira
    def usuarioComMaisDinheiro(self):
        query = """SELECT usuario.nome, usuario.id
                   FROM pokemarket.usuario as usuario
                   ORDER BY usuario.carteira DESC
                   LIMIT 1"""
        
        try:
            self.cur.execute(query)
        
        except Error as err:
            raise Exception("Erro em Dashboard.usuarioComMaisDinheiro(): %s"%err)

    #Retorna a data, e o id da última venda concluída
    def ultimaVenda(self):
        query = """SELECT venda.data, venda.id
                   FROM pokemarket.venda as venda
                   ORDER BY venda.data DESC
                   LIMIT 1"""
        
        try:
            self.cur.execute(query)
        
        except Error as err:
            raise Exception("Erro em Dashboard.ultimaVenda(): %s"%err)
    
    #Retorna a média de vendas por diária nos últimos 30 dias
    def mediaDeVendas(self):
        query = """SELECT COUNT(venda.id)/30
                   FROM pokemarket.venda as venda
                   WHERE venda.finalizada = TRUE
                   AND venda.data >= (SELECT CURRENT_DATE - INTERVAL '30 days')"""

        try:
            self.cur.execute(query)
        
        except Error as err:
            raise Exception("Erro em Dashboard.mediaDeVendas(): %s"%err)

    #Retorna a quantidade de vendas concluídas no dia de hoje
    def vendasHoje(self):
        query = """SELECT COUNT(venda.id)
                   FROM pokemarket.venda as venda
                   WHERE venda.finalizada = TRUE
                   AND venda.data >= (SELECT CURRENT_DATE)"""

        try:
            self.cur.execute(query)
        
        except Error as err:
            raise Exception("Erro em Dashboard.vendasHoje(): %s"%err)

    #Retorna a data do dia com o maior número de vendas concluídas
    def recordeDeVendas(self):
        query = """SELECT venda.data
                   FROM pokemarket.venda as venda
                   WHERE venda.finalizada = TRUE
                   GROUP BY venda.data
                   ORDER BY COUNT(venda.id) DESC
                   LIMIT 1"""

        try:
            self.cur.execute(query)
        
        except Error as err:
            raise Exception("Erro em Dashboard.recordeDeVendas(): %s"%err)
    
    #Retorna o nome e o preço médio do pokemon mais vendido
    def pokemonMaisVendido(self):
        query = """SELECT pokemon.nome, AVG(venda.preco)
                   FROM pokemarket.venda as venda
                   INNER JOIN pokemarket.pokemon as pokemon ON venda.pokemon_id = pokemon.id
                   GROUP BY pokemon.nome
                   ORDER BY COUNT(venda.id) DESC
                   LIMIT 1"""

        try:
            self.cur.execute(query)
        
        except Error as err:
            raise Exception("Erro em Dashboard.pokemonMaisVendido(): %s"%err)
