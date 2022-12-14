from flask import *
from flask_session import Session
from flask_login import LoginManager

app = Flask(__name__, template_folder='templates')
app.secret_key = b'8b1607dc2765e5654876ac3cd8ee66199f9daec1f8b3dab7f6da18517481a645'

SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False

app.config.from_object(__name__)
Session(app)

login_manager = LoginManager()

from controller import controller
