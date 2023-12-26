from dashapp import server, database
from dashapp.models import Usuario

with server.app_context():
    database.create_all()