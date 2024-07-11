from flask import Flask
from .routes import routes

def create_app():
    app = Flask(__name__)
    app.secret_key = '18082006Dd!'  # Defina uma chave secreta para a sessão

    app.register_blueprint(routes)

    return app
