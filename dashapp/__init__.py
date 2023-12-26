from dash import Dash
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


# Inicializando o aplicativo Dash
app = Dash(__name__)
server = app.server
app.config.suppress_callback_exceptions = True

server.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite3',
    SECRET_KEY= "sasdadaasdcfevrqeqweeqw",
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

database = SQLAlchemy(server)
bcrypt = Bcrypt(server)
login_manager = LoginManager(server)
login_manager.login_view = '/login'

from dashapp import views