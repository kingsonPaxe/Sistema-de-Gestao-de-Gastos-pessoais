"""
extensions.py – Instâncias das extensões Flask (sem importar a app).
Importadas por app.py e pelos models/routes sem gerar import circular.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
