from controller import *
from model.usuario import usuario
from pathlib import Path
from functools import wraps
from time import sleep

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (usuario.get(userId=session.get('userId'))['tipo'] != 'admin'):
            print('\n\nVocê não tem permissão para acessar essa página.\n\n')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (session.get("Email")):
            print("\n\nUsuário Logado!\n\n")
            print(session)
            return f(*args, **kwargs)
        else:
            print('\n\nVocê precisa estar logado para acessar essa página.\n\n')
            return redirect(url_for('login'))
    return decorated_function

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        if (usuario.auth(request.form['Email'], request.form['Senha'])):
            session["Email"] = request.form['Email']
            session["userId"] = usuario.get(email=request.form['Email'])['id']
            print("\n\nUsuário Logado!\n\n")
            print(session)
            print(session.get("Email"))
            return redirect(url_for('index'))
        else:
            print("\n\nUsuário não encontrado!\n\n")
            return redirect(url_for('createUser'))

    return render_template('login.html', error=None)

@login_required
@app.route('/')
def index():
    print("\n\nSession!!!\n\n")
    print(session)
    print(session.get('userId'))
    print(session.get('Email'))
    print("\n\n")
    return 'Bem vindo ao Pokemarket !'

@app.route('/singup', methods = ['GET', 'POST'])
def createUser():
    if request.method == 'POST':
        
        Email = request.form['Email']
        Nome = request.form['Nome']
        Senha = request.form['Senha']
        
        if (usuario.get(email=Email) == -1):
            usuario(Nome, Email, Senha)
        
        else:
            print('\n\nUsuário já cadastrado.\n\n')

        return redirect('/login')
        
    return render_template('singup.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('goodbye'))

@app.route('/goodbye')
def goodbye():
    return 'Obrigado por utilizar o meu App !'

@app.route('/giveMoney/<userId>')
@admin_only
def bestowUser50Coins(userId):
    if (usuario.get(userId=userId) != None):
        usuario.giveMoney(userId)
        return "50₪ fornecidos para o usuário de id %s."%userId
    else:
        return "Usuário inválido."