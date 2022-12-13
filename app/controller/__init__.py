from flask import *
from flask_session import Session

app = Flask(__name__, template_folder='templates')
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False
app.config.from_object(__name__)
Session(app)

from controller import controller
