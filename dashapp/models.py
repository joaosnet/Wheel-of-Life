from dashapp import database, login_manager, bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_usuario(usuario_id):
    return Usuario.query.get(int(usuario_id))

class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(100), nullable=False, unique=True)
    email = database.Column(database.String(100), nullable=False, unique=True)
    senha = database.Column(database.String(100), nullable=False)
    