#Importando as bibliotecas necessárias:
from controller import *
from model.usuario import Usuario
from model.venda import Venda
from controller.logger import Logger
from functools import wraps
from datetime import datetime


#Objeto para Logging
logger = Logger()

#Configurações de uso com o Flask-Seesion
sessionUser = None

#Decorators:

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario = Usuario.get(userId=session.get('userId'))
        
        try:
            tipo = usuario.getTipo
        except Exception as err:
            print("Erro em admin_only: %s."%err)
            tipo = None

        if usuario == None or tipo != 'admin':
            return current_app.login_manager.unauthorized()

        return f(*args, **kwargs)
    return decorated_function

#Rotas para usuario:

@app.route('/login', methods = ['GET', 'POST'])
def login():
    global sessionUser

    if request.method == 'POST':
        
        auth = Usuario.auth(request.form['Email'], request.form['Senha'])
        
        if (auth):
            userId = Usuario.get(email=request.form['Email']).get_id()

            session["Email"] = request.form['Email']
            session["userId"] = userId
            sessionUser = Usuario(id=userId)

            login_user(sessionUser)

            if current_user.is_authenticated:
                print("\n\nUsuário logado!\n\n")
            else:
                print("\n\nErro: Usuário não autenticado.\n\n")

            logger.log("Usuário %s (De id %s) logou no dia %s as %s."%(sessionUser.getNome(), sessionUser.get_id(), 
            datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M:%S")))

            return redirect(url_for('meusPokemons'))

        else:
            print("\n\nUsuário não encontrado!\n\n")
            return redirect(url_for('login'))

    return render_template('login.html', error=None)

@app.route('/')
@login_required
def index():
    return 'Bem vindo ao Pokemarket !'

@app.route('/singup', methods = ['GET', 'POST'])
def createUser():
    if request.method == 'POST':
        
        Email = request.form['Email']
        Nome = request.form['Nome']
        Senha = request.form['Senha']
        
        if (Usuario.get(email=Email) == None):
            Usuario.createUser(Nome, Email, Senha)
        
        else:
            print('\n\nUsuário já cadastrado.\n\n')

        return redirect('/login')
        
    return render_template('singup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('goodbye'))

@app.route('/goodbye')
def goodbye():
    return 'Obrigado por utilizar o meu App !'

@app.route('/giveMoney/<userId>')
@admin_only
def bestowUser50Coins(userId):
    if (Usuario.get(userId) != None):
        Usuario.giveMoney(userId)
        return "50₪ fornecidos para o usuário de id %s."%userId
    else:
        return "Usuário inválido."

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get(user_id)


#Rotas para vendas:
@app.route('/meusPokemons', methods = ['GET', 'POST'])
@login_required
def meusPokemons():
    pokemonList = sessionUser.listPokemons()

    if request.method == 'POST':

        preco = request.form['preco']
        pokemonId = int(request.form['pokemonId'])
        sessionUser.sell(pokemonId, preco)

        logger.log("Usuário %s (De id: %s) colocou o pokemon de número: %s a venda por: %s₪ na data: %s as: %s."%(sessionUser.getNome(), sessionUser.get_id(), pokemonId, preco,
        datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M:%S")))

        return redirect(url_for('meusPokemons'))

    return render_template('meusPokemons.html', pokemonList=pokemonList)

@app.route('/feed', methods = ['GET', 'POST'])
@login_required
def feed():
    ofertas = Venda.listVendas()

    if request.method == 'POST':

        vendaId = request.form['vendaId']
        sessionUser.buy(vendaId)
        

        logger.log("Usuário %s (De id: %s) completou a venda de id: %s na data: %s as: %s."%(sessionUser.getNome(), sessionUser.get_id(), vendaId,
        datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M:%S")), vendaInfo = True)
        
        return redirect(url_for('feed'))

    return render_template('feed.html', ofertas=ofertas)