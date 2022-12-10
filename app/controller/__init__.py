from flask import *

app = Flask(__name__, template_folder='templates')

from controller import controller
