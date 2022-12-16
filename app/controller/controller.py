#Importando as bibliotecas necessárias:

from controller import *
from model.usuario import Usuario
from functools import wraps
from time import sleep

#Configurações de uso com o Flask-Seesion
sessionUser = None

#Decorators:

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario = Usuario.get(userId=session.get('userId'))
        
        try:
            tipo = usuario.tipo
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
        
        if (Usuario.auth(request.form['Email'], request.form['Senha'])):
            userId = Usuario.get(email=request.form['Email']).id

            session["Email"] = request.form['Email']
            session["userId"] = userId
            sessionUser = Usuario(id=userId)

            login_user(sessionUser)

            if current_user.is_authenticated:
                print("\n\nUsuário logado!\n\n")
            else:
                print("\n\nErro: Usuário não autenticado.\n\n")

            return redirect(url_for('index'))

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
def myPokemons():
    pokemonList = sessionUser.listPokemons()
    return render_template('myPokemons.html', pokemonList=pokemonList)