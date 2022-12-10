from controller import *
from model.usuario import usuario
from pathlib import Path

@app.route('/')
def index():
    return 'Bem vindo ao Pokemarket !'

@app.route('/singup', methods = ['GET', 'POST'])
def createUser():
    if request.method == 'POST':
        if usuario.get(email=email) == None:
            usuario(nome, email, senha)
            return redirect('/')
        else:
            return redirect('/singup')
    return render_template('singup.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        if (usuario.auth(request.form['Email'], request.form['senha'])):
            print("Usuário logado")
        else:
            redirect('/')
    return render_template('login.html', error=None)
